from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils.crypto import get_random_string

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from flight.models import Flight
from airplane.models import Seat
from reservations.services.reservations import (
    PassengerService, ItineraryService, FlightSegmentService, TicketService
)
from reservations.models import Passenger, FlightSegment
from ...utils.token_store import get_itineraries, delete_itineraries


def to_iso(dt):
    if not dt:
        return None
    try:
        from django.utils.timezone import localtime
        return localtime(dt).isoformat()
    except Exception:
        return getattr(dt, "isoformat", lambda: str(dt))()

def safe_duration_minutes_from_flight(flight):
    est = getattr(getattr(flight, "route", None), "estimated_duration", None)
    if isinstance(est, int):
        return est
    dep, arr = getattr(flight, "departure_time", None), getattr(flight, "arrival_time", None)
    if dep and arr:
        try:
            return max(0, int((arr - dep).total_seconds() // 60))
        except Exception:
            pass
    return 0

def _all_assigned(passengers, flights, selections):
    total = len(passengers)
    if not flights or total == 0:
        return False
    for f in flights:
        fid = int(f["id"])
        assigned = sum(1 for s in selections if int(s["flight_id"]) == fid and s["seat_id"] is not None)
        if assigned != total:
            return False
    return True


token_param = openapi.Parameter(
    name="token",
    in_=openapi.IN_PATH,
    description="Token del itinerario generado previamente",
    type=openapi.TYPE_STRING,
    required=True,
)

confirm_ok_example = {
    "group_itineraries": [
        {
            "id": 1,
            "reservation_code": "ABC123",
            "passenger": {
                "name": "Juan Pérez",
                "document": "32123456",
                "email": "juan.perez@example.com",
                "phone": "+54 9 351 555-1111",
                "birth_date": "1990-05-10",
            },
            "flights": [
                {
                    "flight_number": 1,
                    "origin": "AEP - Buenos Aires",
                    "destination": "COR - Córdoba",
                    "departure_time": "2025-11-06T09:00:00-03:00",
                    "arrival_time": "2025-11-06T10:15:00-03:00",
                    "duration": 75,
                    "seat": "12A",
                    "price": "110000.00",
                }
            ],
            "total_price": "110000.00",
            "ticket": {"barcode": "ABC123-XYZ789", "status": "issued"},
        }
    ],
    "preview": False,
}


class ConfirmItineraryAPI(APIView):
    @swagger_auto_schema(
        operation_id="confirm_itinerary",
        operation_summary="Confirmar itinerario y emitir tickets",
        operation_description=(
            "Lee desde el cache (`passengers`, `flights`, `selections`), valida que todos los asientos "
            "estén asignados, crea los registros en base de datos (Passenger, Itinerary, FlightSegment, Ticket) "
            "y devuelve los itinerarios emitidos con tickets generados. Si hay conflicto de asiento, devuelve 409."
        ),
        manual_parameters=[token_param],
        responses={
            200: openapi.Response(
                description="Itinerario confirmado correctamente",
                examples={"application/json": confirm_ok_example},
            ),
            400: openapi.Response(description="Error de validación"),
            404: openapi.Response(description="Token inválido o expirado"),
            409: openapi.Response(description="Conflicto de asiento ocupado"),
        },
        tags=["Reservations"],
    )
    @transaction.atomic
    def post(self, request, token):
        data = get_itineraries(request, token)
        if not data:
            return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_404_NOT_FOUND)

        passengers = data.get("passengers") or []
        flights_payload = data.get("flights") or []
        selections = data.get("selections") or []

        if not _all_assigned(passengers, flights_payload, selections):
            return Response(
                {"detail": "Faltan asientos por asignar para uno o más pasajeros/vuelos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        seen = {}
        for s in selections:
            fid = int(s["flight_id"])
            sid = s["seat_id"]
            if sid is None:
                continue
            key = (fid, int(sid))
            if key in seen and seen[key] != s["passenger_document"]:
                return Response(
                    {"detail": f"Asiento duplicado en vuelo {fid} para {seen[key]} y {s['passenger_document']}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            seen[key] = s["passenger_document"]

        flight_ids = [int(f["id"]) for f in flights_payload]
        flights_db = {
            f.id: f
            for f in Flight.objects.select_related(
                "route__origin_airport", "route__destination_airport"
            ).filter(id__in=flight_ids, status="active")
        }

        sel_idx = {}
        for s in selections:
            key = (s["passenger_document"], int(s["flight_id"]))
            sel_idx[key] = int(s["seat_id"]) if s["seat_id"] is not None else None

        group_payload = []

        for p in passengers:
            doc = p.get("document")
            if not doc:
                return Response({"detail": "Pasajero sin documento."}, status=400)

            passenger_obj = Passenger.objects.filter(document=doc).first()
            if not passenger_obj:
                try:
                    passenger_obj = PassengerService.create({
                        "name": p.get("name"),
                        "document": doc,
                        "email": p.get("email"),
                        "phone": p.get("phone"),
                        "birth_date": p.get("birth_date"),
                        "document_type": p.get("document_type", "dni"),
                    })
                except Exception as e:
                    return Response({"detail": f"Error creando pasajero {doc}: {e}"}, status=400)

            try:
                itinerary = ItineraryService.create(passenger=passenger_obj)
            except Exception as e:
                return Response({"detail": f"Error creando itinerario para {doc}: {e}"}, status=400)

            flights_data = []

            for f in flights_payload:
                fid = int(f["id"])
                fl = flights_db.get(fid)
                if not fl:
                    return Response({"detail": f"Vuelo {fid} no disponible."}, status=400)

                seat_id = sel_idx.get((doc, fid))
                if seat_id is None:
                    return Response({"detail": f"Asiento faltante para {doc} en vuelo {fid}."}, status=400)

                seat = Seat.objects.filter(id=seat_id, airplane=fl.airplane).first()
                if not seat:
                    return Response({"detail": f"Asiento {seat_id} inválido para el vuelo {fid}."}, status=400)

                if FlightSegment.objects.filter(flight=fl, seat=seat).exists():
                    return Response(
                        {
                            "detail": f"Conflicto: asiento {seat.row}{seat.column} ya está ocupado en vuelo {fid}.",
                            "flight_id": fid,
                            "seat_id": seat_id
                        },
                        status=status.HTTP_409_CONFLICT
                    )

                try:
                    _ = FlightSegmentService.create(
                        itinerary=itinerary,
                        flight=fl,
                        seat=seat,
                        price=getattr(fl, "base_price", 0),
                        status="confirmed"
                    )
                except Exception as e:
                    return Response({"detail": f"Error creando segmento {fid} ({doc}): {e}"}, status=400)

                flights_data.append({
                    "flight_number": fl.id,
                    "origin": f"{fl.route.origin_airport.name} - {fl.route.origin_airport.city}",
                    "destination": f"{fl.route.destination_airport.name} - {fl.route.destination_airport.city}",
                    "departure_time": to_iso(fl.departure_time),
                    "arrival_time": to_iso(fl.arrival_time),
                    "duration": safe_duration_minutes_from_flight(fl),
                    "seat": f"{seat.row}{seat.column}",
                    "price": getattr(fl, "base_price", 0),
                })

            try:
                barcode = f"{itinerary.reservation_code}-{get_random_string(6).upper()}"
                ticket = TicketService.create(itinerary=itinerary, barcode=barcode, status="issued")
            except Exception as e:
                return Response({"detail": f"Error emitiendo ticket: {e}"}, status=400)

            group_payload.append({
                "id": itinerary.id,
                "reservation_code": itinerary.reservation_code,
                "passenger": {
                    "name": passenger_obj.name,
                    "document": passenger_obj.document,
                    "email": passenger_obj.email,
                    "phone": passenger_obj.phone,
                    "birth_date": passenger_obj.birth_date,
                },
                "flights": flights_data,
                "total_price": sum(f["price"] for f in flights_data),
                "ticket": {
                    "barcode": ticket.barcode,
                    "status": ticket.status,
                },
            })

        delete_itineraries(request, token)

        return Response({"group_itineraries": group_payload, "preview": False}, status=200)
