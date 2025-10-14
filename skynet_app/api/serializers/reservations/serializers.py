from rest_framework import serializers
from datetime import date

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
