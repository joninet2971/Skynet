from django.core.exceptions import ValidationError
from flight.models import Airport, Route, Flight
from flight.repositories.flight import AirportRepository, RouteRepository, FlightRepository

class AirportService:
    @staticmethod
    def create(data):
        code = data.get("code")
        if AirportRepository.filter_by_code(code):
            raise ValidationError(f"Airport with code '{code}' already exists.")
        return AirportRepository.create(**data)

    @staticmethod
    def get_all():
        return AirportRepository.get_all()

    @staticmethod
    def get_by_id(id):
        airport = AirportRepository.get_by_id(id)
        if not airport:
            raise ValidationError("Airport not found.")
        return airport

    @staticmethod
    def update(airport, **data):
        if not airport:
            raise ValidationError("Airport not found.")

        new_code = data.get("code")
        if new_code and new_code != airport.code:
            if AirportRepository.filter_by_code(new_code):
                raise ValidationError(f"Another airport with code '{new_code}' already exists.")

        return AirportRepository.update(airport, **data)

    @staticmethod
    def delete(id):
        airport = AirportRepository.get_by_id(id)
        if not airport:
            raise ValidationError("Airport not found.")
        AirportRepository.delete(airport)
        return True


class RouteService:
    @staticmethod
    def create(data):
        origin = data.get("origin_airport")
        destination = data.get("destination_airport")

        if origin == destination:
            raise ValidationError("Origin and destination airports must be different.")

        if RouteRepository.find_by_airports(origin.code, destination.code):
            raise ValidationError("This route already exists.")

        return RouteRepository.create(**data)

    @staticmethod
    def get_all():
        return RouteRepository.get_all()

    @staticmethod
    def get_by_id(id):
        route = RouteRepository.get_by_id(id)
        if not route:
            raise ValidationError("Route not found.")
        return route

    @staticmethod
    def update(route, **data):
        if not route:
            raise ValidationError("Route not found.")

        origin = data.get("origin_airport")
        destination = data.get("destination_airport")

        if origin is None or destination is None:
            raise ValidationError("Both origin and destination airports are required.")

        if origin == destination:
            raise ValidationError("Origin and destination airports cannot be the same.")


        # Validación de código (si aplica a tu modelo)
        new_code = data.get("code")
        if new_code and new_code != route.code:
            if RouteRepository.filter_by_code(new_code):
                raise ValidationError(f"Another route with code '{new_code}' already exists.")

        return RouteRepository.update(route, **data)

    @staticmethod
    def delete(id):
        route = RouteRepository.get_by_id(id)
        if not route:
            raise ValidationError("Route not found.")
        RouteRepository.delete(route)
        return True


class FlightService:
    @staticmethod
    def create(data):
        airplane = data.get("airplane")
        route = data.get("route")
        departure_time = data.get("departure_time")
        arrival_time = data.get("arrival_time")

        if FlightRepository.filter_by_airplane_id(airplane.id).filter(
            route=route,
            departure_time=departure_time
        ).exists():
            raise ValidationError("This flight already exists.")

        if arrival_time <= departure_time:
            raise ValidationError("Arrival time must be after departure time.")

        return FlightRepository.create(**data)

    @staticmethod
    def get_all():
        return FlightRepository.get_all()

    @staticmethod
    def get_by_id(id):
        flight = FlightRepository.get_by_id(id)
        if not flight:
            raise ValidationError("Flight not found.")
        return flight

    @staticmethod
    def update(flight, **data):
        if not flight:
            raise ValidationError("Flight not found.")

        departure_time = data.get("departure_time", flight.departure_time)
        arrival_time = data.get("arrival_time", flight.arrival_time)

        if departure_time >= arrival_time:
            raise ValidationError("Departure time must be before arrival time.")

        return FlightRepository.update(flight, **data)


    @staticmethod
    def delete(id):
        flight = FlightRepository.get_by_id(id)
        if not flight:
            raise ValidationError("Flight not found.")
        FlightRepository.delete(flight)
        return True
