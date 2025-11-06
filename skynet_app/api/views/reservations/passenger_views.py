from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
import json

from api.serializers.reservations.serializers import LoadPassengersSerializer

from ...utils.token_store import save_itineraries, get_itineraries

class LoadPassengersAPI(APIView):
    """
    GET: Devuelve la cantidad de pasajeros guardada en el itinerario (por token).
    POST: Crea o recupera pasajeros a partir del/los payload(s).
          Acepta un objeto o una lista de objetos (batch).
    """

    def get(self, request, token):
        itinerariesSelected = get_itineraries(request, token)

        if not itinerariesSelected:
            return Response(
                {"errors": "itineraries Selected No found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response ({
            "itinerarie":itinerariesSelected.get("itinerary"),
            "passenger_count":itinerariesSelected.get("passengers_count")

        }, status=status.HTTP_200_OK)
    
    def post(self, request, token):
        data = request.data
        if not isinstance(data, (list, dict)):
            #  parsear el body por si vino sin header correcto
            try:
                raw = (request.body or b"").decode("utf-8").strip()
                data = json.loads(raw)
            except Exception:
                return Response(
                    {"error": "Formato inválido. Enviá JSON (objeto o lista)."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not isinstance(data, (list, dict)):
                return Response(
                    {"error": "Formato inválido. Debe ser objeto o lista de objetos."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        is_list = isinstance(request.data, list)
        itineraries = get_itineraries(request, token) or {}
        passengers_count = itineraries.get("passengers_count")

        if passengers_count is None:
            return Response(
                {"error": "No hay 'passengers_count' definido para este itinerario."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incoming_count = len(request.data) if is_list else 1

        if is_list:
            if incoming_count > passengers_count:
                return Response(
                {
                    "error": "Se enviaron más pasajeros de los solicitados.",
                    "expected": passengers_count,
                    "received": incoming_count
                },
                status=status.HTTP_400_BAD_REQUEST
            ) 
        else:
            print("un solo pasajero")

        serializer = LoadPassengersSerializer(data=request.data, many=is_list)
        serializer.is_valid(raise_exception=True)

        items = serializer.validated_data if is_list else [serializer.validated_data]

        passengers = []

        for data in items:
            name = data["name"]
            document = data["document"]
            email = data["email"]
            phone = data["phone"]
            birth_date = data["birth_date"]
            document_type = data["document_type"]

            payload = {
                "name": name,
                "document": document,
                "email": email,
                "phone": phone,
                "birth_date": birth_date,
                "document_type": document_type,
            }

            passengers.append(payload)

            token = save_itineraries(
                request,
                payload_itinerary=itineraries,
                passengers_count=passengers_count,
                payload_passengers=passengers
            )
            
        
        return Response(
            {
                "token": token,
                "passengers": passengers,
                "expected_passenger_count": passengers_count,
                "received": incoming_count
            },
            status=status.HTTP_200_OK
        )
    
   