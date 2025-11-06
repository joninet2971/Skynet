from rest_framework import serializers
from datetime import date
from ...utils.token_store import  get_itineraries

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

    def validate(self, attrs):
        request = self.context.get("request")
        token = self.context.get("token")

        if not request or not token:
            raise serializers.ValidationError("Falta información del contexto (request o token).")

        data = get_itineraries(request, token)
        if not data:
            raise serializers.ValidationError("Token inválido o expirado.")
        
        items = data.get("itinerary") or []

        target_id = str(attrs["idItinerarie"])
        selected = next((it for it in items if str(it.get("id")) == target_id), None)

        if selected is None:
            raise serializers.ValidationError({"idItinerarie": "Itinerario no encontrado."})

        attrs["selected_itinerarie"] = selected
        attrs["passengers_count"] = data.get("passengers_count", 1)
        return attrs

class LoadPassengersSerializer(serializers.Serializer):
    STATUS_CHOICES = [
        ('dni', 'DNI'),
        ('passport', 'Pasaporte'),
    ]

    name = serializers.CharField(max_length=100)
    document = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    birth_date = serializers.DateField()
    document_type = serializers.ChoiceField(choices=STATUS_CHOICES)

    #def validate_phone(self, value):
    #    if not value.replace("+", "").replace(" ", "").isdigit():
    #        raise serializers.ValidationError("El teléfono debe contener solo números o '+'.")
    #    return value
#
    #def validate_birth_date(self, value):
    #    if value > date.today():
    #        raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
    #    return value