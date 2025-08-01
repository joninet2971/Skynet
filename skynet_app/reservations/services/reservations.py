from typing import Optional, List, Tuple
from django.core.exceptions import ValidationError
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
        if FlightSegment.objects.filter(seat=seat).exists():
            raise ValidationError("Seat already assigned.")
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
    def find_available_routes(origin_code: str, destination_code: str, fecha) -> List[List[int]]:
        """Encuentra rutas disponibles entre aeropuertos en una fecha específica"""
        route_chains = find_route_chain(origin_code, destination_code)
        
        if not route_chains:
            return []

        rutas_validas = []
        
        for chain in route_chains:
            vuelos = []
            for tramo in chain:
                vuelo = Flight.objects.filter(
                    route=tramo,
                    departure_time__date=fecha,
                    status="active"
                ).first()
                if vuelo:
                    vuelos.append(vuelo)
                else:
                    break

            if len(vuelos) == len(chain):
                rutas_validas.append([r.id for r in chain])

        return rutas_validas

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
    def get_available_seats_for_passengers(passenger_ids: List[int], route_ids: List[int]) -> List[dict]:
        """Obtiene asientos disponibles para pasajeros en rutas específicas"""
        passengers = Passenger.objects.filter(id__in=passenger_ids)
        routes = Route.objects.filter(id__in=route_ids)
        flights = [Flight.objects.filter(route=route, status="active").first() for route in routes]

        seat_data = []

        for p_index, passenger in enumerate(passengers):
            for f_index, flight in enumerate(flights):
                if not flight:
                    continue
                    
                assigned_seat_ids = FlightSegment.objects.filter(
                    flight=flight,
                    seat__isnull=False
                ).values_list("seat_id", flat=True)

                available_seats = Seat.objects.filter(
                    airplane=flight.airplane
                ).exclude(id__in=assigned_seat_ids)

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
    def create_automatic_reservations(passenger_ids: List[int], route_ids: List[int]) -> Itinerary:
        """Crea reservas automáticas asignando el primer asiento disponible"""
        passengers = Passenger.objects.filter(id__in=passenger_ids)
        routes = Route.objects.filter(id__in=route_ids).select_related(
            "origin_airport", "destination_airport"
        )

        last_itinerary = None
        
        for passenger in passengers:
            reservation_code = ReservationService._generate_unique_reservation_code()

            itinerary = ItineraryService.create(
                passenger=passenger,
                reservation_code=reservation_code
            )
            last_itinerary = itinerary

            for route in routes:
                flight = Flight.objects.filter(route=route, status="active").first()
                if not flight:
                    raise ValidationError(f"No hay vuelo disponible para la ruta {route}")
                    
                # Buscar primer asiento disponible
                assigned_seat_ids = FlightSegment.objects.filter(
                    flight=flight,
                    seat__isnull=False
                ).values_list("seat_id", flat=True)

                seat = Seat.objects.filter(
                    airplane=flight.airplane
                ).exclude(id__in=assigned_seat_ids).first()
                
                if not seat:
                    raise ValidationError(f"No hay asientos disponibles en el vuelo {flight}")

                FlightSegmentService.create(
                    itinerary=itinerary,
                    flight=flight,
                    seat=seat,
                    price=flight.base_price,
                    status="confirmed"
                )

        return last_itinerary

    @staticmethod
    def _generate_unique_reservation_code() -> str:
        """Genera un código de reserva único"""
        reservation_code = str(uuid.uuid4())[:8].upper()
        while Itinerary.objects.filter(reservation_code=reservation_code).exists():
            reservation_code = str(uuid.uuid4())[:8].upper()
        return reservation_code
    
    @staticmethod
    def create_reservations_with_seats(passenger_ids: List[int], route_ids: List[int], post_data: dict) -> Itinerary:

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

                    FlightSegmentRepository.create(
                        itinerary=itinerary,
                        flight=flight,
                        seat=seat,
                        price=flight.base_price,
                        status="confirmed"
                    )

            if errores:
                raise ValidationError(" | ".join(errores))

            return created_itineraries
