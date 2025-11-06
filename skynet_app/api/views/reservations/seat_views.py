from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from reservations.services.seat_read import SeatReadService
from flight.models import Flight, Route
from ...utils.token_store import get_itineraries, get_namespace, _key


def _cast_int(val):
    if val is None: 
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _ensure_flights_in_cache(request, token, payload):
    """Guarda en cache los flights/locks/selections que armamos en el GET (cache-only)."""
    user_type, user_id = get_namespace(request)
    current = get_itineraries(request, token) or {}
    current.update({
        "itinerary": {"itinerary": payload["itinerary"]},
        "passengers": payload["passengers"],
        "flights": payload["flights"],
        "locks": payload.get("locks", []),
        "selections": payload.get("selections", []),
    })
    cache.set(_key(user_type, user_id, token), current, timeout=600)


def _fill_missing_selections(passenger_docs, flights, selections):
    """Asegura una entrada por (pasajero × vuelo), seat_id=None si no eligió todavía."""
    seen = {(s["passenger_document"], s["flight_id"]) for s in selections}
    for doc in passenger_docs:
        for f in flights:
            key = (doc, f["id"])
            if key not in seen:
                selections.append({
                    "passenger_document": doc,
                    "flight_id": f["id"],
                    "seat_id": None
                })
    return selections


def _assignment_status(passengers, flights, selections):
    """
    Devuelve:
      - remaining_per_flight: { flight_id: cuantos faltan asignar }
      - all_assigned_for_flight: { flight_id: bool }
      - all_assigned_for_itinerary: bool (todos los vuelos completos)
    """
    total = len(passengers)
    remaining_per_flight = {}
    all_for_flight = {}

    for f in flights:
        fid = f["id"]
        assigned = sum(1 for s in selections if s["flight_id"] == fid and s["seat_id"] is not None)
        remaining = max(0, total - assigned)
        remaining_per_flight[fid] = remaining
        all_for_flight[fid] = (remaining == 0)

    all_itinerary = all(all_for_flight.values()) if flights else False
    return remaining_per_flight, all_for_flight, all_itinerary


token_param = openapi.Parameter(
    name="token",
    in_=openapi.IN_PATH,
    description="Token de itinerario (generado previamente)",
    type=openapi.TYPE_STRING,
    required=True,
)

choose_seat_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["passenger_document", "flight_id"],
    properties={
        "passenger_document": openapi.Schema(type=openapi.TYPE_STRING, description="Documento del pasajero"),
        "flight_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del vuelo"),
        "seat_id": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description="ID del asiento (opcional: null para desasignar)"),
    },
    example={"passenger_document": "32123456", "flight_id": 1, "seat_id": 200}
)

choose_seat_ok_example = {
    "ok": True,
    "flight_id": 1,
    "seat_id": 200,
    "remaining_per_flight": {"1": 0, "4": 0},
    "all_assigned_for_flight": {"1": True, "4": True},
    "all_assigned_for_itinerary": True,
    "itinerary": {
        "id": 1,
        "route_summary": "AEP → COR → BRC",
        "duration": 225,
        "total_price": "220000.00",
        "route_ids": [1, 4],
    },
    "passengers": [
        {"name": "Juan Pérez", "document": "32123456", "email": "juan.perez@example.com",
         "phone": "+54 9 351 555-1111", "birth_date": "1990-05-10", "document_type": "dni"},
        {"name": "María Gomez", "document": "28999888", "email": "maria.gomez@example.com",
         "phone": "+54 9 351 555-2222", "birth_date": "1992-11-22", "document_type": "dni"},
    ],
    "flights": [
        {"id": 1, "code": "1", "seat_map": {"version": 3, "rows": []}},
        {"id": 4, "code": "4", "seat_map": {"version": 1, "rows": []}},
    ],
    "selections": [
        {"passenger_document": "32123456", "flight_id": 1, "seat_id": 200},
        {"passenger_document": "32123456", "flight_id": 4, "seat_id": 410},
        {"passenger_document": "28999888", "flight_id": 1, "seat_id": 201},
        {"passenger_document": "28999888", "flight_id": 4, "seat_id": 411},
    ],
    "locks": [],
}


class ChooseSeatNormalizedViewAPI(APIView):
    permission_classes = [AllowAny]
    """
    GET /api/itineraries/{token}/seat/
    POST /api/itineraries/{token}/seat/
    """

    @swagger_auto_schema(
        operation_id="get_itinerary_seat_maps",
        operation_summary="Obtener grillas de asientos por vuelo del itinerario",
        operation_description=(
            "Devuelve grillas normalizadas por vuelo, asientos confirmados/retenidos, "
            "selecciones existentes por (pasajero × vuelo) y locks activos."
        ),
        manual_parameters=[token_param],
        responses={
            200: openapi.Response(
                description="OK",
                examples={
                    "application/json": {
                        "itinerary": {
                            "id": 1,
                            "route_summary": "AEP → COR → BRC",
                            "duration": 225,
                            "total_price": "220000.00",
                            "route_ids": [1, 4],
                        },
                        "passengers": [
                            {"name": "Juan Pérez", "document": "32123456", "email": "juan.perez@example.com",
                             "phone": "+54 9 351 555-1111", "birth_date": "1990-05-10", "document_type": "dni"},
                            {"name": "María Gomez", "document": "28999888", "email": "maria.gomez@example.com",
                             "phone": "+54 9 351 555-2222", "birth_date": "1992-11-22", "document_type": "dni"},
                        ],
                        "flights": [
                            {"id": 1, "code": "1", "seat_map": {"version": 1, "rows": []}},
                            {"id": 4, "code": "4", "seat_map": {"version": 1, "rows": []}},
                        ],
                        "selections": [
                            {"passenger_document": "32123456", "flight_id": 1, "seat_id": None},
                            {"passenger_document": "32123456", "flight_id": 4, "seat_id": None},
                            {"passenger_document": "28999888", "flight_id": 1, "seat_id": None},
                            {"passenger_document": "28999888", "flight_id": 4, "seat_id": None},
                        ],
                        "locks": [],
                    }
                },
            ),
            400: openapi.Response(description="Token válido pero datos mal formados (route_ids inválido)"),
            404: openapi.Response(description="Itinerario no encontrado"),
        },
        tags=["Reservations"],
    )
    def get(self, request, token):
        data = get_itineraries(request, token)
        if not data:
            return Response({"error": "Itinerario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        itinerary = (data.get("itinerary") or {}).get("itinerary") or {}
        route_ids = itinerary.get("route_ids") or []
        if not isinstance(route_ids, list):
            return Response({"error": "route_ids inválido"}, status=status.HTTP_400_BAD_REQUEST)

        passengers = data.get("passengers") or []
        passenger_docs = [p.get("document") for p in passengers if p.get("document")]

        routes = Route.objects.filter(id__in=route_ids)
        flights_qs = Flight.objects.filter(route__in=routes, status="active").order_by("id")
        flights = list(flights_qs)

        confirmed_by_flight, held_by_flight = SeatReadService.get_status_sets_by_flight(flights)


        flights_payload = []
        for fl in flights:
            seat_map = SeatReadService.build_seat_map(
                flight=fl,
                confirmed_ids=confirmed_by_flight.get(fl.id, set()),
                held_ids=set(held_by_flight.get(fl.id, {}).keys()),
            )
            flights_payload.append({
                "id": fl.id,
                "code": getattr(fl, "code", str(fl.id)),
                "seat_map": seat_map,
            })


        selections_payload = SeatReadService.get_selections_for_itinerary_docs(passenger_docs, flights)

        selections_payload = _fill_missing_selections(passenger_docs, flights_payload, selections_payload)

        locks_payload = SeatReadService.locks_payload_from_held(held_by_flight)

        payload = {
            "itinerary": {
                "id": itinerary.get("id"),
                "route_summary": itinerary.get("route_summary"),
                "duration": itinerary.get("duration"),
                "total_price": itinerary.get("total_price"),
                "route_ids": route_ids,
            },
            "passengers": passengers,
            "flights": flights_payload,
            "selections": selections_payload,
            "locks": locks_payload,
        }

        _ensure_flights_in_cache(request, token, payload)

        return Response(payload, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="choose_seat",
        operation_summary="Elegir / actualizar asiento para un pasajero en un vuelo",
        operation_description=(
            "Asigna o actualiza el **asiento** de un **pasajero** para un **vuelo** del itinerario.\n"
            "- Si `seat_id` es `null`, desasigna.\n"
            "- Valida que el asiento exista y esté disponible.\n"
            "- Responde con el estado de asignación por vuelo e itinerario."
        ),
        manual_parameters=[token_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            allOf=[choose_seat_request_schema],  
        ),
        responses={
            200: openapi.Response(
                description="Asignación/actualización realizada",
                examples={"application/json": choose_seat_ok_example},
            ),
            400: openapi.Response(description="Body inválido / pasajero o vuelo fuera del token"),
            404: openapi.Response(description="Token inválido o expirado"),
            409: openapi.Response(description="Asiento no disponible"),
        },
        tags=["Reservations"],
    )
    def post(self, request, token):
        body = request.data
        doc = body.get("passenger_document")
        flight_id = _cast_int(body.get("flight_id"))
        seat_id = body.get("seat_id")
        seat_id = None if seat_id is None else _cast_int(seat_id)

        data = get_itineraries(request, token)
        if not data:
            return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_404_NOT_FOUND)

        passengers = data.get("passengers") or []
        flights = data.get("flights") or []
        selections = data.setdefault("selections", [])


        docs = {p.get("document") for p in passengers}
        if doc not in docs:
            return Response({"detail": "Pasajero inválido para este token."}, status=400)


        flight = next((f for f in flights if _cast_int(f.get("id")) == flight_id), None)
        if not flight:
            return Response({"detail": "Vuelo inválido para este token."}, status=400)


        prev_seat_id = None
        for s in selections:
            if s["passenger_document"] == doc and _cast_int(s["flight_id"]) == flight_id:
                prev_seat_id = s.get("seat_id")
                break

        target_seat = None
        if seat_id is not None:
            for row in flight["seat_map"]["rows"]:
                for s in row["seats"]:
                    if _cast_int(s["id"]) == seat_id:
                        target_seat = s
                        break
                if target_seat:
                    break
            if not target_seat:
                return Response({"detail": "Asiento no existe en este vuelo."}, status=400)
            if target_seat.get("status") != "available" and seat_id != prev_seat_id:
                return Response({"detail": "Asiento no disponible."}, status=409)

        data["selections"] = [
            s for s in selections
            if not (s["passenger_document"] == doc and _cast_int(s["flight_id"]) == flight_id)
        ]
        data["selections"].append({
            "passenger_document": doc,
            "flight_id": flight_id,
            "seat_id": seat_id
        })

        if prev_seat_id and prev_seat_id != seat_id:
            for row in flight["seat_map"]["rows"]:
                for s in row["seats"]:
                    if _cast_int(s["id"]) == prev_seat_id and s.get("status") == "held":
                        s["status"] = "available"
        if seat_id is not None:
            target_seat["status"] = "held"

        flight["seat_map"]["version"] = int(flight["seat_map"]["version"]) + 1
        flight["seat_map"]["updated_at"] = timezone.now().isoformat().replace("+00:00", "Z")

        user_type, user_id = get_namespace(request)
        cache.set(_key(user_type, user_id, token), data, timeout=600)

        selections_filled = _fill_missing_selections(
            [p.get("document") for p in passengers if p.get("document")],
            flights,
            list(data["selections"])
        )
        remaining_per_flight, all_for_flight, all_itinerary = _assignment_status(passengers, flights, selections_filled)

        payload = {
            "ok": True,
            "flight_id": flight_id,
            "seat_id": seat_id,
            "remaining_per_flight": remaining_per_flight,
            "all_assigned_for_flight": all_for_flight,
            "all_assigned_for_itinerary": all_itinerary,
            "itinerary": (data.get("itinerary") or {}).get("itinerary"),
            "passengers": data.get("passengers"),
            "flights": data.get("flights"),
            "selections": data.get("selections"),
            "locks": data.get("locks", []),
        }

        return Response(payload, status=200)
