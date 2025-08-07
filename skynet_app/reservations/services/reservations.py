from typing import Optional, List, Tuple
from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from reservations.models import Passenger, Itinerary, FlightSegment, Ticket
from flight.models import Flight, Route
from airplane.models import Seat
from reservations.repositories.reservations import (
    PassengerRepository,
    ItineraryRepository,
    FlightSegmentRepository,
    TicketRepository
)
from reservations.services.route_finder import find_route_chain
from collections import namedtuple
import uuid
from django.db import transaction


# NamedTuple para opciones de itinerario
ItineraryOption = namedtuple("ItineraryOption", ["id", "route_summary", "duration", "total_price"])


# -------------------- Passenger Service --------------------

class PassengerService:
    @staticmethod
    def create(data: dict) -> Passenger:
        if Passenger.objects.filter(document=data.get("document")).exists():
            raise ValidationError("Passenger with this document already exists.")
        return PassengerRepository.create(**data)

    @staticmethod
    def update(passenger_id: int, data: dict) -> Passenger:
        passenger = PassengerRepository.get_by_id(passenger_id)
        if not passenger:
            raise ValidationError("Passenger not found.")

        if "document" in data:
            if Passenger.objects.exclude(id=passenger.id).filter(document=data["document"]).exists():
                raise ValidationError("Document already in use.")

        return PassengerRepository.update(passenger, **data)

    @staticmethod
    def delete(passenger_id: int) -> bool:
        passenger = PassengerRepository.get_by_id(passenger_id)
        if not passenger:
            raise ValidationError("Passenger not found.")
        return PassengerRepository.delete(passenger)

    @staticmethod
    def get(passenger_id: int) -> Optional[Passenger]:
        return PassengerRepository.get_by_id(passenger_id)

    @staticmethod
    def list_all() -> List[Passenger]:
        return PassengerRepository.get_all()

    @staticmethod
    def get_by_document(document: str) -> Optional[Passenger]:
        """Busca un pasajero por su documento"""
        return Passenger.objects.filter(document=document).first()


# -------------------- Itinerary Service --------------------

class ItineraryService:
    @staticmethod
    def create(passenger: Passenger, reservation_code: str = None) -> Itinerary:
        if not reservation_code:
            reservation_code = str(uuid.uuid4())[:8].upper()

        if Itinerary.objects.filter(reservation_code=reservation_code).exists():
            raise ValidationError("Reservation code already exists.")

        return Itinerary.objects.create(passenger=passenger, reservation_code=reservation_code)

    @staticmethod
    def create_auto(passenger: Passenger, origin_code: str, destination_code: str) -> Itinerary:
        routes = find_route_chain(origin_code, destination_code)
        if not routes:
            raise ValidationError("No route found between selected airports.")

        reservation_code = str(uuid.uuid4())[:8].upper()
        itinerary = ItineraryService.create(passenger, reservation_code)

        for route in routes:
            flight = Flight.objects.filter(route=route).first()
            if not flight:
                raise ValidationError(f"No flight found for route {route}")

            seat = Seat.objects.filter(airplane=flight.airplane, status='available').first()
            if not seat:
                raise ValidationError(f"No available seat for flight {flight}")

            # Cambiás el estado del asiento si querés reservarlo
            seat.status = 'reserved'
            seat.save()

            FlightSegmentRepository.create(
                itinerary=itinerary,
                flight=flight,
                seat=seat,
                price=flight.base_price,
                status="confirmed"
            )

        return itinerary

    @staticmethod
    def update(itinerary_id: int, data: dict) -> Itinerary:
        itinerary = ItineraryRepository.get_by_id(itinerary_id)
        if not itinerary:
            raise ValidationError("Itinerary not found.")
        return ItineraryRepository.update(itinerary, **data)

    @staticmethod
    def delete(itinerary_id: int) -> bool:
        itinerary = ItineraryRepository.get_by_id(itinerary_id)
        if not itinerary:
            raise ValidationError("Itinerary not found.")
        return ItineraryRepository.delete(itinerary)

    @staticmethod
    def get(itinerary_id: int) -> Optional[Itinerary]:
        return ItineraryRepository.get_by_id(itinerary_id)

    @staticmethod
    def list_all() -> List[Itinerary]:
        return ItineraryRepository.get_all()


# -------------------- FlightSegment Service --------------------

class FlightSegmentService:
    @staticmethod
    def create(itinerary: Itinerary, flight: Flight, seat: Seat, price: float, status: str) -> FlightSegment:
        # Validar que el asiento no esté asignado        
        if FlightSegment.objects.filter(seat=seat, flight=flight).exists():
            raise ValidationError("The seat is already assigned.")

        # Validar que el pasajero no tenga ya una reserva para ese vuelo
        if FlightSegment.objects.filter(
            flight=flight,
            itinerary__passenger=itinerary.passenger
        ).exists():
            raise ValidationError("This passenger already has a reservation for this flight.")

        return FlightSegmentRepository.create(itinerary, flight, seat, price, status)


    @staticmethod
    def update(segment_id: int, data: dict) -> FlightSegment:
        segment = FlightSegmentRepository.get_by_id(segment_id)
        if not segment:
            raise ValidationError("Flight segment not found.")

        if "seat" in data:
            if FlightSegment.objects.exclude(id=segment.id).filter(seat=data["seat"]).exists():
                raise ValidationError("Seat already assigned.")

        return FlightSegmentRepository.update(segment, **data)

    @staticmethod
    def delete(segment_id: int) -> bool:
        segment = FlightSegmentRepository.get_by_id(segment_id)
        if not segment:
            raise ValidationError("Flight segment not found.")
        return FlightSegmentRepository.delete(segment)

    @staticmethod
    def get(segment_id: int) -> Optional[FlightSegment]:
        return FlightSegmentRepository.get_by_id(segment_id)

    @staticmethod
    def list_by_itinerary(itinerary: Itinerary) -> List[FlightSegment]:
        return FlightSegmentRepository.get_by_itinerary(itinerary)


# -------------------- Ticket Service --------------------

class TicketService:
    @staticmethod
    def create(itinerary: Itinerary, barcode: str, status: str = "issued") -> Ticket:
        # Verificar si ya tiene ticket
        if hasattr(itinerary, 'ticket'):
            return itinerary.ticket  # Ya existe, devolvemos el existente

        if Ticket.objects.filter(barcode=barcode).exists():
            raise ValidationError("Barcode already exists.")

        return TicketRepository.create(itinerary, barcode, status)


    @staticmethod
    def update(ticket_id: int, data: dict) -> Ticket:
        ticket = TicketRepository.get_by_id(ticket_id)
        if not ticket:
            raise ValidationError("Ticket not found.")
        return TicketRepository.update(ticket, **data)

    @staticmethod
    def delete(ticket_id: int) -> bool:
        ticket = TicketRepository.get_by_id(ticket_id)
        if not ticket:
            raise ValidationError("Ticket not found.")
        return TicketRepository.delete(ticket)

    @staticmethod
    def get(ticket_id: int) -> Optional[Ticket]:
        return TicketRepository.get_by_id(ticket_id)

    @staticmethod
    def get_by_itinerary(itinerary: Itinerary) -> Optional[Ticket]:
        return TicketRepository.get_by_itinerary(itinerary)


# -------------------- Route Service --------------------

class RouteService:
    @staticmethod
    def find_available_routes(origin_code: str, destination_code: str, fecha, passenger_count: int) -> List[List[int]]:
        """Encuentra rutas disponibles entre aeropuertos en una fecha específica,
        validando que cada vuelo tenga suficientes asientos disponibles."""
        route_chains = find_route_chain(origin_code, destination_code)

        if not route_chains:
            return [], ["No se encontraron rutas entre los aeropuertos seleccionados."]

        rutas_validas = []
        errores = []

        for chain in route_chains:
            vuelos = []
            ruta_valida = True

            for tramo in chain:
                vuelo = Flight.objects.filter(
                    route=tramo,
                    departure_time__date=fecha,
                    status="active"
                ).first()

                if not vuelo:
                    errores.append(f"No hay vuelo activo para la ruta {tramo}")
                    ruta_valida = False
                    break

                available_seats_count = Seat.objects.filter(
                    airplane=vuelo.airplane
                ).exclude(
                    id__in=FlightSegment.objects.filter(flight=vuelo).values_list("seat_id", flat=True)
                ).count()

                if available_seats_count < passenger_count:
                    errores.append(
                        f"Vuelo {vuelo} no tiene suficientes asientos disponibles: se necesitan {passenger_count}, hay {available_seats_count}."
                    )
                    ruta_valida = False
                    break

                vuelos.append(vuelo)

            if ruta_valida and len(vuelos) == len(chain):
                rutas_validas.append([r.id for r in chain])

        return rutas_validas, errores


    @staticmethod
    def get_itinerary_options(route_chains_ids: List[List[int]], search_date: str) -> Tuple[List[ItineraryOption], List]:
        """Obtiene las opciones de itinerario con precios y duraciones"""
        options = []
        rutas_completas = []

        for idx, chain_ids in enumerate(route_chains_ids, 1):
            routes = Route.objects.filter(id__in=chain_ids).select_related(
                "origin_airport", "destination_airport"
            )
            if not routes:
                continue
                
            flights = Flight.objects.filter(route__in=chain_ids, status="active")
           
            rutas_completas.append(routes)

            summary = " → ".join([r.origin_airport.code for r in routes] + 
                               [routes.last().destination_airport.code])
            
            duration = sum(f.route.duration for f in flights)
            total_price = sum(f.base_price for f in flights)
            options.append(ItineraryOption(idx, summary, duration, total_price))

        return options, rutas_completas


# -------------------- Seat Service --------------------

class SeatService:
    @staticmethod
    def _remove_expired_segments():
        EXPIRATION_MINUTES = 5
        expired_segments = FlightSegment.objects.filter(
            status="reserved",
            reserved_at__lt=timezone.now() - timedelta(minutes=EXPIRATION_MINUTES)
        )
        itinerary_ids = set()
        for seg in expired_segments:
            itinerary_ids.add(seg.itinerary_id)
            seg.delete()
        for itin_id in itinerary_ids:
            if not FlightSegment.objects.filter(itinerary_id=itin_id).exists():
                itinerary = ItineraryRepository.get_by_id(itin_id)
                if itinerary:
                    ItineraryRepository.delete(itinerary)

    @staticmethod
    def get_available_seats_for_passengers(passenger_ids: List[int], route_ids: List[int]) -> List[dict]:
        """Obtiene asientos disponibles con su estado (disponible, reservado, ocupado)"""
        SeatService._remove_expired_segments()
            
        passengers = Passenger.objects.filter(id__in=passenger_ids)
        routes = Route.objects.filter(id__in=route_ids)
        flights = [Flight.objects.filter(route=route, status="active").first() for route in routes]

        seat_data = []

        for p_index, passenger in enumerate(passengers):
            for f_index, flight in enumerate(flights):
                if not flight:
                    continue

                # Subquery para obtener el estado del segmento de vuelo (si existe) para ese asiento y vuelo
                segment_status_subquery = FlightSegment.objects.filter(
                    seat=OuterRef("pk"),
                    flight=flight
                ).values("status")[:1]

                # Anotamos el estado, si no hay segmento asociado, es "available"
                available_seats = Seat.objects.filter(
                    airplane=flight.airplane
                ).annotate(
                    segment_status=Coalesce(
                        Subquery(segment_status_subquery),
                        Value("available")
                    )
                )

                key = f"{p_index}_{f_index}"
                seat_data.append({
                    "key": key,
                    "passenger": passenger,
                    "flight": flight,
                    "seats": available_seats
                })

        return seat_data


    @staticmethod
    def is_seat_available(seat_id: int, flight: Flight) -> bool:
        """Verifica si un asiento está disponible para un vuelo"""
        return not FlightSegment.objects.filter(
            seat_id=seat_id, 
            flight=flight
        ).exists()

    

# -------------------- Reservation Service --------------------

class ReservationService:
    @staticmethod
    def _generate_unique_reservation_code() -> str:
        """Genera un código de reserva único"""
        reservation_code = str(uuid.uuid4())[:8].upper()
        while Itinerary.objects.filter(reservation_code=reservation_code).exists():
            reservation_code = str(uuid.uuid4())[:8].upper()
        return reservation_code
    
    @staticmethod
    def create_reservations_with_seats(passenger_ids: List[int], route_ids: List[int], post_data: dict, status:str) -> Itinerary:
        """Crea reservas pudiendo elegir un asiento disponible"""
        with transaction.atomic():
            passengers = Passenger.objects.filter(id__in=passenger_ids)
            routes = Route.objects.filter(id__in=route_ids)
            flights = [
                Flight.objects.filter(route=route, status="active").first()
                for route in routes
            ]

            seat_assignments = {}  # { flight.id: set(seat_ids) }
            created_itineraries = []
            errores = []

            for p_index, passenger in enumerate(passengers):
                reservation_code = ReservationService._generate_unique_reservation_code()

                itinerary = ItineraryService.create(
                    passenger=passenger,
                    reservation_code=reservation_code
                )
                created_itineraries.append(itinerary)

                for f_index, flight in enumerate(flights):
                    if not flight:
                        errores.append(f"Vuelo no encontrado para la ruta {f_index}")
                        continue

                    key = f"{p_index}_{f_index}"
                    seat_id = post_data.get(f"seat_{key}")

                    if not seat_id:
                        errores.append(f"Falta asignar asiento para {passenger.name} en vuelo {flight}")
                        continue

                    assigned = seat_assignments.setdefault(flight.id, set())
                    if seat_id in assigned:
                        errores.append(f"Asiento duplicado en vuelo {flight} para distintos pasajeros.")
                        continue
                    assigned.add(seat_id)

                    seat = Seat.objects.filter(id=seat_id).first()
                    if not seat:
                        errores.append(f"Asiento no válido para {passenger.name}")
                        continue

                    if FlightSegment.objects.filter(flight=flight, seat=seat).exists():
                        errores.append(f"Asiento {seat.row}{seat.column} ya está ocupado.")
                        continue

                    FlightSegmentService.create(
                        itinerary=itinerary,
                        flight=flight,
                        seat=seat,
                        price=flight.base_price,
                        status=status
                    )

            if errores:
                raise ValidationError(" | ".join(errores))

            return created_itineraries
    
 


