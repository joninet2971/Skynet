from rest_framework import serializers
from flight.models import Flight, Route, Airport
from api.serializers.airplane.serializer import AirplaneSerializer
from datetime import datetime


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['id', 'name', 'code', 'city', 'country']

    def validate_code(self, value):
        # Validar que el código tenga exactamente 3 letras (formato IATA)
        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError("El código del aeropuerto debe tener exactamente 3 letras.")
        return value.upper()


class RouteSerializer(serializers.ModelSerializer):
    origin_airport = AirportSerializer(read_only=True)
    destination_airport = AirportSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'origin_airport', 'destination_airport', 'estimated_duration']

    def validate(self, data):
        origin = self.instance.origin_airport if self.instance else None
        destination = self.instance.destination_airport if self.instance else None

        # Validar que el aeropuerto de origen y destino no sean iguales
        if origin and destination and origin == destination:
            raise serializers.ValidationError("El aeropuerto de origen y destino no pueden ser iguales.")

        # Validar que la duración estimada sea positiva
        if 'estimated_duration' in data and data['estimated_duration'].total_seconds() <= 0:
            raise serializers.ValidationError("La duración estimada debe ser mayor a cero.")

        return data


class FlightSerializer(serializers.ModelSerializer):
    airplane = AirplaneSerializer(read_only=True)
    route = RouteSerializer(read_only=True)

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

        # Validar que las fechas sean coherentes
        if departure and arrival and arrival <= departure:
            raise serializers.ValidationError("La hora de llegada debe ser posterior a la hora de salida.")

        # Validar que no sea un vuelo en el pasado (opcional)
        if departure and departure < datetime.now():
            raise serializers.ValidationError("La hora de salida no puede estar en el pasado.")

        # Validar precio base
        if base_price is not None and base_price <= 0:
            raise serializers.ValidationError("El precio base debe ser mayor a 0.")

        return data
