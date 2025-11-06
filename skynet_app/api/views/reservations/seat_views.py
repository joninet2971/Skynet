from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache

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
        # asientos asignados (seat_id no nulo) para este vuelo
        assigned = sum(1 for s in selections if s["flight_id"] == fid and s["seat_id"] is not None)
        remaining = max(0, total - assigned)
        remaining_per_flight[fid] = remaining
        all_for_flight[fid] = (remaining == 0)

    all_itinerary = all(all_for_flight.values()) if flights else False
    return remaining_per_flight, all_for_flight, all_itinerary


class ChooseSeatNormalizedViewAPI(APIView):
    """
    GET /api/itineraries/{token}/seat/
    POST /api/itineraries/{token}/seat/
    """

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

        # Vuelos activos en esas rutas
        routes = Route.objects.filter(id__in=route_ids)
        flights_qs = Flight.objects.filter(route__in=routes, status="active").order_by("id")
        flights = list(flights_qs)

        # Estados por vuelo (desde DB, solo lectura)
        confirmed_by_flight, held_by_flight = SeatReadService.get_status_sets_by_flight(flights)

        # Grillas por vuelo (normalizadas)
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

        # Selecciones existentes (si el pasajero ya tiene FlightSegments)
        selections_payload = SeatReadService.get_selections_for_itinerary_docs(passenger_docs, flights)
        # Rellenar faltantes (seat_id=None)
        selections_payload = _fill_missing_selections(passenger_docs, flights_payload, selections_payload)

        # Locks derivados de reserved no vencido
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

        # cache para que el POST no tenga que ir a DB
        _ensure_flights_in_cache(request, token, payload)

        return Response(payload, status=status.HTTP_200_OK)

    def post(self, request, token):
        body = request.data
        doc = body.get("passenger_document")
        flight_id = _cast_int(body.get("flight_id"))
        seat_id = body.get("seat_id")
        seat_id = None if seat_id is None else _cast_int(seat_id)

        # cache actual
        data = get_itineraries(request, token)
        if not data:
            return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_404_NOT_FOUND)

        passengers = data.get("passengers") or []
        flights = data.get("flights") or []
        selections = data.setdefault("selections", [])

        # validar pasajero
        docs = {p.get("document") for p in passengers}
        if doc not in docs:
            return Response({"detail": "Pasajero inválido para este token."}, status=400)

        # validar vuelo
        flight = next((f for f in flights if _cast_int(f.get("id")) == flight_id), None)
        if not flight:
            return Response({"detail": "Vuelo inválido para este token."}, status=400)

        # validar asiento (si viene)
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

        # actualizar selections (una por pasajero×vuelo)
        data["selections"] = [
            s for s in selections
            if not (s["passenger_document"] == doc and _cast_int(s["flight_id"]) == flight_id)
        ]
        data["selections"].append({
            "passenger_document": doc,
            "flight_id": flight_id,
            "seat_id": seat_id
        })

        #feedback optimista en grilla
        if prev_seat_id and prev_seat_id != seat_id:
            for row in flight["seat_map"]["rows"]:
                for s in row["seats"]:
                    if _cast_int(s["id"]) == prev_seat_id and s.get("status") == "held":
                        s["status"] = "available"
        if seat_id is not None:
            target_seat["status"] = "held"

        flight["seat_map"]["version"] = int(flight["seat_map"]["version"]) + 1
        flight["seat_map"]["updated_at"] = timezone.now().isoformat().replace("+00:00", "Z")

        # guardar en cache
        user_type, user_id = get_namespace(request)
        cache.set(_key(user_type, user_id, token), data, timeout=600)

        # calcular pendientes
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
