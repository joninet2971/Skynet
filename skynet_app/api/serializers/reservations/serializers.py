from rest_framework import serializers
from datetime import date
from utils.token_store import get_itineraries


class SearchRouteSerializer(serializers.Serializer):
    origin = serializers.CharField(max_length=10)
    destination = serializers.CharField(max_length=10)
    date = serializers.DateField()
    passengers = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        if attrs["origin"] == attrs["destination"]:
            raise serializers.ValidationError("El origen y destino no pueden ser iguales.")
        #if attrs["date"] < date.today():
        #    raise serializers.ValidationError("La fecha no puede ser en el pasado.")
        return attrs

class ChooseItinerarySerializer(serializers.Serializer):
    idItinerarie = serializers.IntegerField(min_value=1)
    tokenItineraries = serializers.CharField(max_length=50)

    def validate_tokenItineraries(self, value):
        data = get_itineraries(value)
        if not data:
            raise serializers.ValidationError("El token es inválido o expiró.")
        
        self.context["itineraries_data"] = data
        return value
