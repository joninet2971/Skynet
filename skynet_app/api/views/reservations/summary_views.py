from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.utils.timezone import localtime

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from flight.models import Flight
from ...utils.token_store import get_itineraries


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

def _seat_label_from_map(seat_map, seat_id):
    if seat_id is None:
        return "No asignado"
    for row in seat_map.get("rows", []):
        for s in row.get("seats", []):
            if s.get("id") == seat_id:
                return s.get("num") or f"{s.get('row')}{s.get('col')}"
    return "No asignado"

token_param = openapi.Parameter(
    name="token",
    in_=openapi.IN_PATH,
    description="Token de itinerario (generado en pasos anteriores)",
    type=openapi.TYPE_STRING,
    required=True,
)

summary_ok_example = {
    "group_itineraries": [
        {
            "id": None,
            "reservation_code": "dd2533a83a874066ab600a27690a9f1b",
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
                    "origin": "Aeroparque Jorge Newbery - Buenos Aires",
                    "destination": "Ingeniero Ambrosio Taravella - Córdoba",
                    "departure_time": "2025-11-06T09:00:00-03:00",
                    "arrival_time": "2025-11-06T10:15:00-03:00",
                    "duration": 75,
                    "seat": "12A",
                    "price": "110000.00",
                },
                {
                    "flight_number": 4,
                    "origin": "Ingeniero Ambrosio Taravella - Córdoba",
                    "destination": "San Carlos de Bariloche - San Carlos de Bariloche",
                    "departure_time": "2025-11-06T11:00:00-03:00",
                    "arrival_time": "2025-11-06T12:30:00-03:00",
                    "duration": 90,
                    "seat": "14C",
                    "price": "110000.00",
                },
            ],
            "total_price": "220000.00",
            "ticket": None,
        }
    ],
    "preview": True,
    "token": "dd2533a83a874066ab600a27690a9f1b",
}


class GroupSummaryPreviewAPI(APIView):
    permission_classes = [AllowAny]
    """
    GET /api/itineraries/<token>/summary/
    Devuelve 'group_itineraries' por pasajero usando CACHE (preview).
    """

    @swagger_auto_schema(
        operation_id="get_group_summary_preview",
        operation_summary="Resumen de grupo (preview) por token",
        operation_description=(
            "Devuelve, para cada pasajero del token, el detalle de vuelos (origen, destino, horarios), "
            "asiento elegido (si existe), y el precio total calculado **usando solo el cache**."
        ),
        manual_parameters=[token_param],
        responses={
            200: openapi.Response(
                description="OK",
                examples={"application/json": summary_ok_example},
            ),
            404: openapi.Response(description="Token inválido o expirado"),
        },
        tags=["Reservations"],
    )
    def get(self, request, token):
        data = get_itineraries(request, token)
        if not data:
            return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_404_NOT_FOUND)

        passengers = data.get("passengers") or []
        flights_payload = data.get("flights") or []
        selections = data.get("selections") or []

        sel_idx = {(s.get("passenger_document"), int(s.get("flight_id"))): s.get("seat_id")
                   for s in selections}

        flight_ids = [int(f["id"]) for f in flights_payload]
        flights_db = {
            f.id: f
            for f in Flight.objects.select_related(
                "route__origin_airport", "route__destination_airport"
            ).filter(id__in=flight_ids)
        }

        itineraries = []
        for p in passengers:
            doc = p.get("document")
            flights_data = []
            for f in flights_payload:
                fid = int(f["id"])
                fdb = flights_db.get(fid)
                if not fdb:
                    continue
                seat_id = sel_idx.get((doc, fid))
                seat_label = _seat_label_from_map(f["seat_map"], seat_id)
                flights_data.append({
                    "flight_number": fdb.id,
                    "origin": f"{fdb.route.origin_airport.name} - {fdb.route.origin_airport.city}",
                    "destination": f"{fdb.route.destination_airport.name} - {fdb.route.destination_airport.city}",
                    "departure_time": localtime(fdb.departure_time),
                    "arrival_time": localtime(fdb.arrival_time),
                    "duration": safe_duration_minutes_from_flight(fdb),
                    "seat": seat_label,
                    "price": getattr(fdb, "base_price", 0),
                })

            itineraries.append({
                "id": None,
                "reservation_code": token, 
                "passenger": {
                    "name": p.get("name"),
                    "document": doc,
                    "email": p.get("email"),
                    "phone": p.get("phone"),
                    "birth_date": p.get("birth_date"),
                },
                "flights": flights_data,
                "total_price": sum(f["price"] for f in flights_data),
                "ticket": None,
            })

        return Response({"group_itineraries": itineraries, "preview": True, "token": token}, status=200)
