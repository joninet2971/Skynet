from django.core.exceptions import ValidationError
from flight.models import Airport, Route, Flight
from flight.repositories.flight import (
    AirportRepository,
    RouteRepository,
    FlightRepository
)

class AirportService:
    @staticmethod
    def create(data):
        if Airport.objects.filter(code=data.get("code")).exists():
            raise ValidationError("Airport already exist")
        return AirportRepository.create(data)
    
class RouteService:
    @staticmethod
    def create(data):
        origin = data.get("origin_airport")
        destination = data.get("destination_airport")

        if Route.objects.filter(origin_airport=origin, destination_airport=destination).exists():
            raise ValidationError("This route already exists.")
        
        if origin == destination:
            raise ValidationError("Origin and destination airports must be different.")


        return RouteRepository.create(data)

class FlightService:
    @staticmethod
    def create(data):
        airplane_id = data.get("airplane")
        route_id = data.get("route")
        departure_time = data.get("departure_time")

        if Flight.objects.filter(
            airplane_id=airplane_id,
            route_id=route_id,
            departure_time=departure_time
        ).exists():
            raise ValidationError("This flight already exists.")

        if data.get("arrival_time") <= departure_time:
            raise ValidationError("Arrival time must be after departure time.")

        return FlightRepository.create(data)


