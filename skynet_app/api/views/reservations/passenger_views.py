from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers.reservations.serializers import LoadPassengersSerializer
from ...utils.token_store import save_itineraries, get_itineraries

token_param = openapi.Parameter(
    name="token",
    in_=openapi.IN_PATH,
    description="Token de itinerario generado previamente",
    type=openapi.TYPE_STRING,
    required=True,
)


class LoadPassengersAPI(APIView):
    permission_classes = [AllowAny]
    """
    GET: Devuelve la cantidad de pasajeros guardada en el itinerario (por token).
    POST: Crea o recupera pasajeros a partir del/los payload(s).
          Acepta un objeto o una lista de objetos (batch).
    """

    @swagger_auto_schema(
        operation_id="get_itinerary_passenger_count",
        operation_summary="Obtener datos del itinerario por token",
        operation_description="Devuelve el objeto de itinerario y la cantidad de pasajeros esperada.",
        manual_parameters=[token_param],
        responses={
            200: openapi.Response(
                description="OK",
                examples={
                    "application/json": {
                        "itinerarie": {
                            "itinerary": {
                                "id": 1,
                                "route_summary": "AEP → COR → BRC",
                                "duration": 225,
                                "total_price": "220000.00",
                                "route_ids": [1, 4],
                                "flights": [{"id": 1}, {"id": 4}],
                            }
                        },
                        "passenger_count": 2,
                    }
                },
            ),
            400: openapi.Response(description="Token inválido o no encontrado"),
        },
        tags=["Reservations"],
    )
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

    @swagger_auto_schema(
        operation_id="load_passengers",
        operation_summary="Cargar pasajeros para un itinerario",
        operation_description=(
            "Recibe **un objeto** de pasajero **o** una **lista** de pasajeros. "
            "Valida que la cantidad coincida con la esperada para el itinerario."
        ),
        manual_parameters=[token_param],

        request_body=LoadPassengersSerializer(many=True),
        responses={
            200: openapi.Response(
                description="Pasajeros cargados en cache",
                examples={
                    "application/json": {
                        "token": "f29136348c7f493aa120ab3964915351",
                        "passengers": [
                            {
                                "name": "Juan Pérez",
                                "document": "32123456",
                                "email": "juan.perez@example.com",
                                "phone": "+54 9 351 555-1111",
                                "birth_date": "1990-05-10",
                                "document_type": "dni",
                            },
                            {
                                "name": "María Gomez",
                                "document": "28999888",
                                "email": "maria.gomez@example.com",
                                "phone": "+54 9 351 555-2222",
                                "birth_date": "1992-11-22",
                                "document_type": "dni",
                            },
                        ],
                        "expected_passenger_count": 2,
                        "received": 2,
                    }
                },
            ),
            400: openapi.Response(description="Error de validación / cantidad incorrecta / formato inválido"),
        },
        tags=["Reservations"],
    )
    def post(self, request, token):
        data = request.data
        if not isinstance(data, (list, dict)):
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
            diff = incoming_count - passengers_count

            if diff < 0:
                return Response(
                    {
                        "error": "Faltan pasajeros en la lista enviada.",
                        "expected": passengers_count,
                        "received": incoming_count,
                        "missing": abs(diff)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            elif diff > 0:
                return Response(
                    {
                        "error": "Se enviaron más pasajeros de los esperados.",
                        "expected": passengers_count,
                        "received": incoming_count,
                        "extra": diff
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if passengers_count != 1:
                return Response(
                    {
                        "error": "Cantidad inválida de pasajeros.",
                        "expected": passengers_count,
                        "received": 1,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

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
