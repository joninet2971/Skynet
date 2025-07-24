from flight.models import Airport, Route, Flight

class AirportRepository:
    @staticmethod
    def create(**data):
        return Airport.objects.create(**data)
    
    @staticmethod
    def get_all():
        return Airport.objects.all()

class RouteRepository:
    @staticmethod
    def create(**data):
        return Route.objects.create(**data)
    
    @staticmethod
    def get_all():
        return Route.objects.all()
    
class FlightRepository:
    @staticmethod
    def create(**data):
        return Flight.objects.create(**data)
    
    @staticmethod
    def get_all():
        return Flight.objects.all()


