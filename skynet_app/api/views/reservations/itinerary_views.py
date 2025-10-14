from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from api.serializers.reservations.serializers import SearchRouteSerializer, ChooseItinerarySerializer
from reservations.services.reservations import RouteService

from flight.models import Flight, Route

from services.calculate_data_route_chain import calc_route_chain
from ...utils.token_store import save_itineraries, get_itineraries, delete_itineraries


class SearchAndCreateItineraryAPI(APIView):
    #permission_classes = [permissions.AllowAny]  # ajustá según tu auth

    def post(self, request):
        serializer = SearchRouteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        origin = serializer.validated_data["origin"]
        destination = serializer.validated_data["destination"]
        fecha = serializer.validated_data["date"]
        passenger_count = serializer.validated_data["passengers"]

        try:
            # El servicio debe devolver datos serializables (IDs o dicts)
            route_chains, errores = RouteService.find_available_routes(
                origin, destination, fecha, passenger_count
            )

            if not route_chains:
                # 404 si no hay rutas posibles
                return Response(
                    {"errors": errores or ["No se encontraron itinerarios disponibles."]},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Cálculo de opciones (JSON-serializable)
            options = calc_route_chain(route_chains, Route.objects, Flight.objects)

            tokenItineraries = save_itineraries(options["itineraries"])

            # En API REST devolvemos los datos.
            payload = {
                "tokenItineraries":tokenItineraries,
                "search_date": str(fecha),
                "origin": options["origin"],
                "destination": options["destination"],
                "passenger_count": passenger_count,
                "itineraries": options["itineraries"],

            }

            return Response(payload, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"errors": [f"Error buscando rutas: {str(e)}"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ChooseItineraryView(APIView):
    def post (self,request):
        serializer = ChooseItinerarySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        idItinerarie = serializer.validated_data["idItinerarie"]
        tokenItineraries = serializer.validated_data["tokenItineraries"]

        itineraries = get_itineraries(tokenItineraries)

        for item in itineraries:
            if item["id"] == idItinerarie:
                selectedItinerarie = item
                break

        if not selectedItinerarie:
            return Response(
                {"errors": "Itinerarie No found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payload = {
                "itineraries": itineraries,
                "selectedItinerarie": selectedItinerarie
            }

        return Response(payload , status=status.HTTP_200_OK)