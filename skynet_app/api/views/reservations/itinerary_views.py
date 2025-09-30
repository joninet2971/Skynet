from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from api.serializers.reservations.serializers import SearchRouteSerializer
from reservations.services.reservations import RouteService

from flight.models import Flight, Route

from services.calculate_data_route_chain import calc_route_chain


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
            calc = calc_route_chain(route_chains, Route.objects, Flight.objects)

            # En API REST devolvemos los datos (stateless). Si querés sesión, ver nota abajo.
            payload = {
                "search_date": str(fecha),
                "origin": calc["origin"],
                "destination": calc["destination"],
                "passenger_count": passenger_count,
                "itineraries": calc["itineraries"],

            }

            return Response(payload, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"errors": [f"Error buscando rutas: {str(e)}"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
















from django.views.generic import FormView, TemplateView, View
from django.shortcuts import redirect
from django.contrib import messages


    
# Muestra las opciones de itinerario posibles
class ChooseItineraryView(TemplateView):
    template_name = "choose_itinerary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_chains_ids = self.request.session.get("route_chain_ids_list", []) #Este valor es una lista de listas con IDs de rutas posibles, por ejemplo:[[12], [4, 7], [5, 9, 11]]
        options = []
        route_full = []

        for idx, chain_ids in enumerate(route_chains_ids, 1): 
            #route_chains_ids = [["A", "B", "C"], ["D", "E"]]  resultado 1: ['A', 'B', 'C'] - 2: ['D', 'E']

            duration = 0
            total_price = 0
            routes = Route.objects.filter(id__in=chain_ids).select_related("origin_airport", "destination_airport")
            #Busca los objetos Route reales para los IDs de la cadena.
            if not routes:
                continue
            flight = Flight.objects.filter(route__in=chain_ids)
            #Busca los vuelos asociados a esas rutas (cada vuelo tiene duración y precio).        
            route_full.append(routes)  # Guardamos todas las rutas reales

            summary = " → ".join([r.origin_airport.code for r in routes] + [routes.last().destination_airport.code])
            
            duration = sum(r.route.estimated_duration for r in flight)
            total_price = sum(a.base_price for a in flight)
            options.append(ItineraryOption(idx, summary, duration, total_price))
         

        context["itineraries"] = options
        context["route_options"] = route_chains_ids
        context["rutas_completas"] = route_full #por el momento no se usa
        context["origin"] = options[0].route_summary.split(" → ")[0] if options else None
        context["destination"] = options[0].route_summary.split(" → ")[-1] if options else None
        context["date"] = self.request.session.get("search_date")
        context["passengers"] = self.request.session.get("passenger_count")
        return context
    
# Vista que se ejecuta cuando se selecciona el itinerario
class SelectItineraryView(View):    
    def get(self, request):
        # Redirigimos a la vista de elección de itinerario si se accede por GET
        return redirect("choose_itinerary")
        
    def post(self, request):
        option_idx = int(request.POST.get("option_idx", 0))
        select_route = self.request.session["route_chain_ids_list"]
        
        request.session["route_chain"] = select_route[option_idx]
        return redirect("load_passengers")  # Paso siguiente: cargar pasajeros



