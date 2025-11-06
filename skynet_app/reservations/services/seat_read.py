from collections import defaultdict
from datetime import timedelta
from django.utils import timezone

from airplane.models import Seat
from reservations.models import FlightSegment

STATUS_AVAILABLE = "available"
STATUS_HELD = "held"
STATUS_CONFIRMED = "confirmed"

class SeatReadService:
    """Solo lectura/adaptación para armar seat_map normalizado desde tus modelos."""

    HOLD_TTL_MIN = 5  # debe coincidir con _remove_expired_segments()

    @staticmethod
    def get_status_sets_by_flight(flights):
        """
        Devuelve, por vuelo:
          - confirmed_ids: seats con FlightSegment (cualquier status != reserved vigente)
          - held: { seat_id: held_until } para reserved no vencidos
        """
        now = timezone.now()
        flight_ids = [f.id for f in flights]
        segs = (FlightSegment.objects
                .filter(flight_id__in=flight_ids)
                .values("flight_id", "seat_id", "status", "reserved_at"))

        confirmed_by_flight = defaultdict(set)
        held_by_flight = defaultdict(dict)

        for s in segs:
            fid = s["flight_id"]
            sid = s["seat_id"]
            status = s["status"]
            if status == "reserved" and s["reserved_at"]:
                held_until = s["reserved_at"] + timedelta(minutes=SeatReadService.HOLD_TTL_MIN)
                if held_until > now:
                    held_by_flight[fid][sid] = held_until
                    continue  # mientras está held, no lo marcamos confirmed
            # cualquier otro caso con segmento existente = ocupado
            confirmed_by_flight[fid].add(sid)

        return confirmed_by_flight, held_by_flight

    @staticmethod
    def build_seat_map(flight, confirmed_ids, held_ids):
        """
        Construye la grilla por vuelo:
          - rows: [{row, seats:[{id,col,num,status}]}]
          - version/updated_at: usamos campos del Flight si existen, si no los “simulamos”
        """
        seats = (Seat.objects
                 .filter(airplane=flight.airplane)
                 .values("id", "row", "column", "number")
                 .order_by("row", "column"))

        rows_dict = defaultdict(list)
        for s in seats:
            sid = s["id"]
            if sid in confirmed_ids:
                st = STATUS_CONFIRMED
            elif sid in held_ids:
                st = STATUS_HELD
            else:
                st = STATUS_AVAILABLE
            rows_dict[s["row"]].append({
                "id": sid,
                "col": s["column"],
                "num": s["number"],
                "status": st,
            })

        rows = []
        for r in sorted(rows_dict.keys()):
            rows.append({"row": r, "seats": sorted(rows_dict[r], key=lambda x: x["col"])})

        version = getattr(flight, "seatmap_version", 1)
        updated_at = getattr(flight, "seatmap_updated_at", timezone.now())
        return {
            "rows": rows,
            "legend": {STATUS_AVAILABLE: "#", STATUS_CONFIRMED: "#", STATUS_HELD: "#"},
            "version": version,
            "updated_at": updated_at.isoformat().replace("+00:00", "Z"),
        }

    @staticmethod
    def get_selections_for_itinerary_docs(passenger_docs, flights):
        """
        Devuelve [{ passenger_document, flight_id, seat_id }]
        a partir de FlightSegment del pasajero (si existe).
        """
        if not passenger_docs or not flights:
            return []

        qs = (FlightSegment.objects
              .filter(flight__in=flights,
                      itinerary__passenger__document__in=passenger_docs)
              .values("flight_id", "seat_id",
                      "itinerary__passenger__document"))
        out = []
        for row in qs:
            out.append({
                "passenger_document": row["itinerary__passenger__document"],
                "flight_id": row["flight_id"],
                "seat_id": row["seat_id"],
            })
        return out

    @staticmethod
    def locks_payload_from_held(held_by_flight):
        """
        Convierte held_by_flight → lista [{ seat_id, flight_id, held_until }]
        """
        locks = []
        for fid, mapping in held_by_flight.items():
            for sid, held_until in mapping.items():
                locks.append({
                    "seat_id": sid,
                    "flight_id": fid,
                    "held_until": held_until,
                })
        return locks
