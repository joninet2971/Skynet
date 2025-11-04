from rest_framework import serializers
from flight.models import Flight, Route, Airport
from api.serializers.airplane.serializer import AirplaneSerializer


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['id', 'name', 'code', 'city', 'country']


class RouteSerializer(serializers.ModelSerializer):
    origin_airport = AirportSerializer(read_only=True)
    destination_airport = AirportSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'origin_airport', 'destination_airport', 'estimated_duration']


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
