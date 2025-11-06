from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from api.serializers.reservations.serializers import SearchRouteSerializer, ChooseItinerarySerializer
from reservations.services.reservations import RouteService

from flight.models import Flight, Route

from services.calculate_data_route_chain import calc_route_chain
from ...utils.token_store import save_itineraries


class SearchAndCreateItineraryAPI(APIView):

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
        passengers_count = serializer.validated_data["passengers"]
       
        try:
            # El servicio debe devolver datos serializables (IDs o dicts)
            route_chains, errores = RouteService.find_available_routes(
                origin, destination, fecha, passengers_count
            )

            if not route_chains:
                return Response(
                    {"errors": errores or ["No se encontraron itinerarios disponibles."]},
                    status=status.HTTP_404_NOT_FOUND
                )
           
            # Cálculo de opciones 
            options = calc_route_chain(route_chains, Route.objects, Flight.objects)

            
            tokenItineraries = save_itineraries(
                request, 
                payload_itinerary=options["itineraries"],
                passengers_count=passengers_count
                )
           

            payload = {
                "tokenItineraries":tokenItineraries,
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
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChooseItineraryAPI(APIView):
    def post(self, request, token):
        serializer = ChooseItinerarySerializer(
            data=request.data,
            context={"request": request, "token": token}
        )
        serializer.is_valid(raise_exception=True)

        selected_itinerary = serializer.validated_data["selected_itinerarie"]  
        passengers_count = serializer.validated_data["passengers_count"]

        token_itineraries_selected = save_itineraries(
            request,
            payload_itinerary=selected_itinerary,
            passengers_count=passengers_count
        )

        return Response(
            {
                "tokenItinerariesSelected": token_itineraries_selected,
                "itinerarySelected": selected_itinerary,
                "passengers_count": passengers_count
            },
            status=status.HTTP_201_CREATED
        )
