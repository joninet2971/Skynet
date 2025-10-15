from rest_framework import serializers
from airplane.models import Airplane, Seat

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'number', 'row', 'column', 'type', 'status']

class AirplaneSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Airplane
        fields = ['id', 'model', 'rows', 'columns', 'enabled', 'seats']
