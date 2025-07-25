from flight.models import Airport, Route, Flight

class AirportRepository:
    @staticmethod
    def create(**data):
        return Airport.objects.create(**data)

    @staticmethod
    def get_all():
        return Airport.objects.all()

    @staticmethod
    def get_by_id(id):
        return Airport.objects.filter(id=id).first()

    @staticmethod
    def filter_by_name(name):
        return Airport.objects.filter(name=name)

    @staticmethod
    def filter_by_code(code):
        return Airport.objects.filter(code=code).first()

    @staticmethod
    def update(airport, **data):
        for attr, value in data.items():
            setattr(airport, attr, value)
        airport.save()
        return airport

    @staticmethod
    def delete(airport):
        airport.delete()


class RouteRepository:
    @staticmethod
    def create(**data):
        return Route.objects.create(**data)

    @staticmethod
    def get_all():
        return Route.objects.all()

    @staticmethod
    def get_by_id(id):
        return Route.objects.filter(id=id).first()

    @staticmethod
    def find_by_airports(origin_code, destination_code):
        return Route.objects.filter(
            origin_airport__code=origin_code,
            destination_airport__code=destination_code
        ).first()

    @staticmethod
    def update(route, **data):
        for attr, value in data.items():
            setattr(route, attr, value)
        route.save()
        return route

    @staticmethod
    def delete(route):
        route.delete()


class FlightRepository:
    @staticmethod
    def create(**data):
        return Flight.objects.create(**data)

    @staticmethod
    def get_all():
        return Flight.objects.all()

    @staticmethod
    def get_by_id(id):
        return Flight.objects.filter(id=id).first()

    @staticmethod
    def filter_by_status(status):
        return Flight.objects.filter(status=status)

    @staticmethod
    def filter_by_airplane_id(airplane_id):
        return Flight.objects.filter(airplane_id=airplane_id)

    @staticmethod
    def update(flight, **data):
        for attr, value in data.items():
            setattr(flight, attr, value)
        flight.save()
        return flight

    @staticmethod
    def delete(flight):
        flight.delete()