from rest_framework import serializers
from flight.models import Flight, Route, Airport
from airplane.models import Airplane
from django.utils import timezone


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['id', 'name', 'code', 'city', 'country']

    def validate_code(self, value):
        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError("El código del aeropuerto debe tener exactamente 3 letras.")
        return value.upper()


class RouteSerializer(serializers.ModelSerializer):
    origin_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    destination_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())

    origin_name = serializers.CharField(source="origin_airport.name", read_only=True)
    destination_name = serializers.CharField(source="destination_airport.name", read_only=True)

    class Meta:
        model = Route
        fields = [
            'id',
            'origin_airport',
            'origin_name',
            'destination_airport',
            'destination_name',
            'estimated_duration'
        ]

    def validate(self, data):
        origin = data.get("origin_airport") or getattr(self.instance, "origin_airport", None)
        destination = data.get("destination_airport") or getattr(self.instance, "destination_airport", None)
        duration = data.get("estimated_duration") or getattr(self.instance, "estimated_duration", None)

        if origin and destination and origin == destination:
            raise serializers.ValidationError("El aeropuerto de origen y destino deben ser distintos.")

        if duration is not None and duration <= 0:
            raise serializers.ValidationError("La duración estimada debe ser mayor a cero (en minutos).")

        return data


class FlightSerializer(serializers.ModelSerializer):
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())

    class Meta:
        model = Flight
        fields = [
            'id',
            'airplane',
            'route',
            'departure_time',
            'arrival_time',
            'status',
            'base_price'
        ]

    def validate(self, data):
        departure = data.get('departure_time') or getattr(self.instance, 'departure_time', None)
        arrival = data.get('arrival_time') or getattr(self.instance, 'arrival_time', None)
        base_price = data.get('base_price') or getattr(self.instance, 'base_price', None)

        if departure and arrival and arrival <= departure:
            raise serializers.ValidationError("La hora de llegada debe ser posterior a la hora de salida.")

        if departure and departure < timezone.now():
            raise serializers.ValidationError("La hora de salida no puede estar en el pasado.")

        if base_price is not None and base_price <= 0:
            raise serializers.ValidationError("El precio base debe ser mayor a 0.")

        return data
