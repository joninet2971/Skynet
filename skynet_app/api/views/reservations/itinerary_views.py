from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from api.serializers.reservations.serializers import SearchRouteSerializer, ChooseItinerarySerializer
from reservations.services.reservations import RouteService

from flight.models import Flight, Route

from services.calculate_data_route_chain import calc_route_chain
from ...utils.token_store import save_itineraries, get_itineraries, delete_itineraries


class SearchAndCreateItineraryAPI(APIView):
    #permission_classes = [permissions.AllowAny]  

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

            payloadCache = {
                "itineraries": options["itineraries"],
                "passengers_count": passengers_count,  
            }
            tokenItineraries = save_itineraries(request,payloadCache)
            #print(get_itineraries(request, tokenItineraries))

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


class ChooseItineraryView(APIView):
    #permission_classes = [permissions.AllowAny]  # ajustá según tu auth
    
    def post(self, request, token):
        serializer = ChooseItinerarySerializer(
            data=request.data,
            context={"request": request, "token": token}
        )
        serializer.is_valid(raise_exception=True)
      
        
        payload = {
            "itinerarie": serializer.validated_data["selected_itinerarie"],
            "passengers_count": serializer.validated_data["passengers_count"],
        }

        tokenItinerariesSelected = save_itineraries(request, payload)
        print(get_itineraries(request, tokenItinerariesSelected))

        return Response({
            "tokenItinerariesSelected": tokenItinerariesSelected,
            "itinerarieSelected": payload
            
        }, status=status.HTTP_200_OK)
