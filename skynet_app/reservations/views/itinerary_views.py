from django.views.generic import FormView, TemplateView, View
from django.shortcuts import redirect
from django.contrib import messages
from reservations.forms import SearchRouteForm
from reservations.services.reservations import RouteService
from collections import namedtuple

# Modelos
from flight.models import Flight, Route

# Vista para buscar rutas posibles y guardar los datos en sesión
class SearchAndCreateItineraryView(FormView):
    template_name = 'search_route.html'
    form_class = SearchRouteForm

    def form_valid(self, form):
        origin = form.cleaned_data['origin']
        destination = form.cleaned_data['destination']
        fecha = form.cleaned_data['date']
        passenger_count = form.cleaned_data['passengers']

        try:
            # Buscar posibles rutas usando el servicio find_available_routes
            route_chains = RouteService.find_available_routes(
                origin.code, 
                destination.code, 
                fecha
            )
            
            if not route_chains:
                messages.error(self.request, "No se encontró una ruta válida entre esos aeropuertos.")
                return self.form_invalid(form)

            # Guardar en sesión
            self.request.session["route_chain_ids_list"] = route_chains
            self.request.session["search_date"] = str(fecha)
            self.request.session["passenger_count"] = passenger_count

            messages.success(self.request, "Itinerarios encontrados correctamente.")
            return redirect("choose_itinerary")
            
        except Exception as e:
            messages.error(self.request, f"Error buscando rutas: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor corregí los errores del formulario.")
        return super().form_invalid(form)
    
# Vista para mostrar las opciones de itinerario posibles
class ChooseItineraryView(TemplateView):
    template_name = "choose_itinerary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_chains_ids = self.request.session.get("route_chain_ids_list", []) #Este valor es una lista de listas con IDs de rutas posibles, por ejemplo:[[12], [4, 7], [5, 9, 11]]
        options = []
        route_full = []

        for idx, chain_ids in enumerate(route_chains_ids, 1):
            duration = 0
            total_price = 0
            routes = Route.objects.filter(id__in=chain_ids).select_related("origin_airport", "destination_airport")
            if not routes:
                continue
            flight = Flight.objects.filter(route__in=chain_ids)
                    
            route_full.append(routes)  # Guardamos todas las rutas reales

            summary = " → ".join([r.origin_airport.code for r in routes] + [routes.last().destination_airport.code])
            
            duration = sum(r.route.estimated_duration for r in flight)
            total_price = sum(a.base_price for a in flight)
            options.append(ItineraryOption(idx, summary, duration, total_price))
         

        context["itineraries"] = options
        context["route_options"] = route_chains_ids
        context["rutas_completas"] = route_full 
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
        print(request.session["route_chain"])
        return redirect("load_passengers")  # Paso siguiente: cargar pasajeros



ItineraryOption = namedtuple("ItineraryOption", ["id", "route_summary", "duration", "total_price"])
