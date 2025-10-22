from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from api.serializers.reservations.serializers import SearchRouteSerializer, ChooseItinerarySerializer
from reservations.services.reservations import RouteService

from flight.models import Flight, Route

from services.calculate_data_route_chain import calc_route_chain
from ...utils.token_store import save_itineraries, get_itineraries, delete_itineraries

# Carga múltiples pasajeros en base a la cantidad seleccionada
class LoadPassengers(APIView):

    def get(self, request, token):
        itinerariesSelected = get_itineraries("itinerariesSelected", token)
        print(get_itineraries("itinerariesSelected", token))
        if not itinerariesSelected:
            return Response(
                {"errors": "itineraries Selected No found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response ({
            "passenger_count":itinerariesSelected.get("passengers_count")
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        return