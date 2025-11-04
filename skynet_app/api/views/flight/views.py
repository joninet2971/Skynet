from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from flight.models import Airport, Route, Flight
from api.serializers.flight.serializer import AirportSerializer, RouteSerializer, FlightSerializer


# --- AIRPORTS CRUD ---
class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminUser]  # Solo admin


# --- ROUTES CRUD ---
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAdminUser]  # Solo admin


# --- FLIGHTS CRUD ---
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsAdminUser]  # Solo admin
