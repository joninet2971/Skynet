from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers.reservations.serializers import (
    SearchRouteSerializer,
    ChooseItinerarySerializer,
)
from reservations.services.reservations import RouteService
from flight.models import Flight, Route
from services.calculate_data_route_chain import calc_route_chain
from ...utils.token_store import save_itineraries


token_param = openapi.Parameter(
    "token",
    openapi.IN_PATH,
    description="Token del itinerario generado por la búsqueda",
    type=openapi.TYPE_STRING,
    required=True,
)


class SearchAndCreateItineraryAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="search_itineraries",
        operation_summary="Buscar itinerarios disponibles",
        operation_description=(
            "Busca itinerarios (con escalas posibles) desde un **origen** a un **destino** "
            "en una **fecha** para una cantidad de **pasajeros**. Devuelve opciones y un token para continuar el flujo."
        ),
        request_body=SearchRouteSerializer,
        responses={
            200: openapi.Response(
                description="Itinerarios encontrados correctamente",
                examples={
                    "application/json": {
                        "tokenItineraries": "59f5b07820784cd58c7fc56a7b3a59f8",
                        "search_date": "2025-11-06",
                        "origin": {"code": "AEP", "city": "Buenos Aires"},
                        "destination": {"code": "BRC", "city": "Bariloche"},
                        "passenger_count": 2,
                        "itineraries": [
                            {
                                "id": 1,
                                "route_summary": "AEP → COR → BRC",
                                "duration": 225,
                                "total_price": "220000.00",
                                "route_ids": [1, 4],
                                "flights": [
                                    {"id": 1, "code": "1"},
                                    {"id": 4, "code": "4"},
                                ],
                            }
                        ],
                    }
                },
            ),
            400: openapi.Response(description="Error de validación"),
            404: openapi.Response(description="No se encontraron itinerarios"),
            500: openapi.Response(description="Error interno del servidor"),
        },
        tags=["Reservations"],
    )
    def post(self, request):
        serializer = SearchRouteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        origin = serializer.validated_data["origin"]
        destination = serializer.validated_data["destination"]
        fecha = serializer.validated_data["date"]
        passengers_count = serializer.validated_data["passengers"]

        try:
            route_chains, errores = RouteService.find_available_routes(
                origin, destination, fecha, passengers_count
            )

            if not route_chains:
                return Response(
                    {"errors": errores or ["No se encontraron itinerarios disponibles."]},
                    status=status.HTTP_404_NOT_FOUND,
                )

            options = calc_route_chain(route_chains, Route.objects, Flight.objects)

            tokenItineraries = save_itineraries(
                request,
                payload_itinerary=options["itineraries"],
                passengers_count=passengers_count,
            )

            payload = {
                "tokenItineraries": tokenItineraries,
                "search_date": str(fecha),
                "origin": options["origin"],
                "destination": options["destination"],
                "passenger_count": passengers_count,
                "itineraries": options["itineraries"],
            }

            return Response(payload, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"errors": [f"Error buscando rutas: {str(e)}"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChooseItineraryAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="choose_itinerary",
        operation_summary="Seleccionar itinerario",
        operation_description=(
            "Selecciona un itinerario de los devueltos por la búsqueda anterior y fija la cantidad de pasajeros. "
            "Devuelve un nuevo token para continuar el flujo de reserva."
        ),
        manual_parameters=[token_param],
        request_body=ChooseItinerarySerializer,
        responses={
            201: openapi.Response(
                description="Itinerario seleccionado correctamente",
                examples={
                    "application/json": {
                        "tokenItinerariesSelected": "dd2533a83a874066ab600a27690a9f1b",
                        "itinerarySelected": {
                            "id": 1,
                            "route_summary": "AEP → COR → BRC",
                            "duration": 225,
                            "total_price": "220000.00",
                            "route_ids": [1, 4],
                            "flights": [
                                {"id": 1, "code": "1"},
                                {"id": 4, "code": "4"},
                            ],
                        },
                        "passengers_count": 2,
                    }
                },
            ),
            400: openapi.Response(description="Error de validación"),
        },
        security=[{"Bearer": []}],
        tags=["Reservations"],
    )
    def post(self, request, token):
        serializer = ChooseItinerarySerializer(
            data=request.data, context={"request": request, "token": token}
        )
        serializer.is_valid(raise_exception=True)

        selected_itinerary = serializer.validated_data["selected_itinerarie"]
        passengers_count = serializer.validated_data["passengers_count"]

        token_itineraries_selected = save_itineraries(
            request,
            payload_itinerary=selected_itinerary,
            passengers_count=passengers_count,
        )

        return Response(
            {
                "tokenItinerariesSelected": token_itineraries_selected,
                "itinerarySelected": selected_itinerary,
                "passengers_count": passengers_count,
            },
            status=status.HTTP_201_CREATED,
        )
