from typing import Optional, List
from django.core.exceptions import ValidationError
from reservations.models import Passenger, Itinerary, FlightSegment, Ticket
from flight.models import Flight
from airplane.models import Seat
from reservations.repositories.reservations import (
    PassengerRepository,
    ItineraryRepository,
    FlightSegmentRepository,
    TicketRepository
)
from reservations.services.route_finder import find_route_chain
import uuid


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
