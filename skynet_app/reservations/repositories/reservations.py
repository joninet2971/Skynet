from typing import Optional, List
from django.db.models import Q
from reservations.models import Passenger, Itinerary, FlightSegment, Ticket
from flight.models import Flight
from airplane.models import Seat


class PassengerRepository:
    @staticmethod
    def create(**data) -> Passenger:
        return Passenger.objects.create(**data)

    @staticmethod
    def get_by_id(passenger_id: int) -> Optional[Passenger]:
        return Passenger.objects.filter(id=passenger_id).first()

    @staticmethod
    def update(passenger: Passenger, **data) -> Passenger:
        for attr, value in data.items():
            setattr(passenger, attr, value)
        passenger.save()
        return passenger

    @staticmethod
    def delete(passenger: Passenger) -> bool:
        passenger.delete()
        return True

    @staticmethod
    def get_all() -> List[Passenger]:
        return list(Passenger.objects.all())

    @staticmethod
    def search(query: str) -> List[Passenger]:
        return list(Passenger.objects.filter(
            Q(name__icontains=query) |
            Q(document__icontains=query) |
            Q(email__icontains=query)
        ))


class ItineraryRepository:
    @staticmethod
    def create(passenger: Passenger, reservation_code: str) -> Itinerary:
        return Itinerary.objects.create(passenger=passenger, reservation_code=reservation_code)

    @staticmethod
    def get_by_id(itinerary_id: int) -> Optional[Itinerary]:
        return Itinerary.objects.filter(id=itinerary_id).first()

    @staticmethod
    def get_by_reservation_code(code: str) -> Optional[Itinerary]:
        return Itinerary.objects.filter(reservation_code=code).first()

    @staticmethod
    def update(itinerary: Itinerary, **data) -> Itinerary:
        for attr, value in data.items():
            setattr(itinerary, attr, value)
        itinerary.save()
        return itinerary

    @staticmethod
    def delete(itinerary: Itinerary) -> bool:
        itinerary.delete()
        return True

    @staticmethod
    def get_all() -> List[Itinerary]:
        return list(Itinerary.objects.all())


class FlightSegmentRepository:
    @staticmethod
    def create(itinerary: Itinerary, flight: Flight, seat: Seat, price: float, status: str) -> FlightSegment:
        return FlightSegment.objects.create(
            itinerary=itinerary,
            flight=flight,
            seat=seat,
            price=price,
            status=status
        )

    @staticmethod
    def get_by_id(segment_id: int) -> Optional[FlightSegment]:
        return FlightSegment.objects.filter(id=segment_id).first()

    @staticmethod
    def update(segment: FlightSegment, **data) -> FlightSegment:
        for attr, value in data.items():
            setattr(segment, attr, value)
        segment.save()
        return segment

    @staticmethod
    def delete(segment: FlightSegment) -> bool:
        segment.delete()
        return True

    @staticmethod
    def get_by_itinerary(itinerary: Itinerary) -> List[FlightSegment]: #Traé todos los segmentos de este itinerario, y además cargá de una vez el vuelo y el asiento asociado a cada segmento (con JOINs), para no hacer más queries después.
        return list(itinerary.segments.select_related('flight', 'seat'))


class TicketRepository:
    @staticmethod
    def create(itinerary: Itinerary, barcode: str, status: str = 'issued') -> Ticket:
        return Ticket.objects.create(
            itinerary=itinerary,
            barcode=barcode,
            status=status
        )

    @staticmethod
    def get_by_id(ticket_id: int) -> Optional[Ticket]:
        return Ticket.objects.filter(id=ticket_id).first()

    @staticmethod
    def update(ticket: Ticket, **data) -> Ticket:
        for attr, value in data.items():
            setattr(ticket, attr, value)
        ticket.save()
        return ticket

    @staticmethod
    def delete(ticket: Ticket) -> bool:
        ticket.delete()
        return True

    @staticmethod
    def get_by_itinerary(itinerary: Itinerary) -> Optional[Ticket]:
        return Ticket.objects.filter(itinerary=itinerary).first()

    

