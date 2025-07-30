# Django imports
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from collections import namedtuple
import uuid

# Formularios
from reservations.forms import PassengerForm, SearchRouteForm

# Modelos (solo para imports necesarios)
from reservations.models import Itinerary

# Servicios
from reservations.services.reservations import (
    ItineraryService, FlightSegmentService, TicketService, PassengerService,
    RouteService, SeatService, ReservationService
)

# Algoritmo para encontrar rutas
from reservations.services.route_finder import find_route_chain

    
# Vista para cargar múltiples pasajeros en base a la cantidad seleccionada
class LoadPassengersView(View):
    template_name = "create_passenger.html"

    def get(self, request):
        passenger_count = int(request.session.get("passenger_count", 1))
        return render(request, self.template_name, {
            "form": PassengerForm(),
            "count": passenger_count,
            "range": range(passenger_count)
        })

    def post(self, request):
        passenger_count = int(request.session.get("passenger_count", 1))
        passengers = []

        for i in range(passenger_count):
            form_data = {
                'name': request.POST.get(f'name_{i}'),
                'document': request.POST.get(f'document_{i}'),
                'email': request.POST.get(f'email_{i}'),
                'phone': request.POST.get(f'phone_{i}') or None,
                'birth_date': request.POST.get(f'birth_date_{i}') or None,
                'document_type': request.POST.get(f'document_type_{i}') or None,
            }
            document = form_data["document"]
            
            # Buscar pasajero existente usando el servicio
            existing_passenger = PassengerService.get_by_document(document)

            if existing_passenger:
                passengers.append(existing_passenger)
            else:
                form = PassengerForm(form_data)
                if form.is_valid():
                    try:
                        passenger = PassengerService.create(form.cleaned_data)
                        passengers.append(passenger)
                    except Exception as e:
                        messages.error(request, f"Error creando pasajero {i + 1}: {str(e)}")
                        return render(request, self.template_name, {
                            "form": form,
                            "count": passenger_count,
                            "range": range(passenger_count)
                        })
                else:
                    messages.error(request, f"Error en el pasajero {i + 1}. Verifica los datos.")
                    return render(request, self.template_name, {
                        "form": form,
                        "count": passenger_count,
                        "range": range(passenger_count)
                    })

        request.session['passenger_ids'] = [p.id for p in passengers]
        messages.success(request, f"{len(passengers)} pasajero(s) cargado(s) correctamente.")
        return redirect('choose_seat_view')


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
            # Buscar posibles rutas usando el servicio
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


# Objeto que representa un itinerario posible
ItineraryOption = namedtuple("ItineraryOption", ["id", "route_summary", "duration", "total_price"])


# Vista para mostrar las opciones de itinerario posibles
class ChooseItineraryView(TemplateView):
    template_name = "choose_itinerary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_chains_ids = self.request.session.get("route_chain_ids_list", [])
        search_date = self.request.session.get("search_date")
        
        try:
            options, rutas_completas = RouteService.get_itinerary_options(
                route_chains_ids, 
                search_date
            )
            
            context["itineraries"] = options
            context["route_options"] = route_chains_ids
            context["rutas_completas"] = rutas_completas
            context["origin"] = options[0].route_summary.split(" → ")[0] if options else None
            context["destination"] = options[0].route_summary.split(" → ")[-1] if options else None
            context["date"] = search_date
            context["passengers"] = self.request.session.get("passenger_count")
            
        except Exception as e:
            messages.error(self.request, f"Error cargando opciones: {str(e)}")
            context["itineraries"] = []
            context["route_options"] = []
            context["rutas_completas"] = []
            
        return context


# Vista que se ejecuta cuando se selecciona el itinerario
class SelectItineraryView(View):    
    def get(self, request):
        # Redirigimos a la vista de elección de itinerario si se accede por GET
        return redirect("choose_itinerary")
        
    def post(self, request):
        option_idx = int(request.POST.get("option_idx", 0))

        print(option_idx)
        print(self.request.session["route_chain_ids_list"])
        select_route = self.request.session["route_chain_ids_list"]
        
        request.session["route_chain"] = select_route[option_idx]
        print(request.session["route_chain"])
        return redirect("load_passengers")  # Paso siguiente: cargar pasajeros


# Vista que permite al usuario seleccionar manualmente los asientos
class ChooseSeatView(View):
    template_name = "choose_seat.html"

    def get(self, request):
        passenger_ids = request.session.get("passenger_ids", [])
        route_ids = request.session.get("route_chain", [])

        try:
            seat_data = SeatService.get_available_seats_for_passengers(
                passenger_ids, 
                route_ids
            )
            
            return render(request, self.template_name, {"seat_data": seat_data})
            
        except Exception as e:
            messages.error(request, f"Error cargando asientos: {str(e)}")
            return redirect("choose_itinerary")

    def post(self, request):
        passenger_ids = request.session.get("passenger_ids", [])
        route_ids = request.session.get("route_chain", [])

        try:
            last_itinerary = ReservationService.create_reservations_with_seats(
                passenger_ids, 
                route_ids, 
                request.POST
            )
            
            messages.success(request, "Asientos asignados correctamente.")
            return redirect("view_summary", itinerary_id=last_itinerary.id)
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect("choose_seat_view")


# Vista que genera itinerarios automáticamente sin selección manual de asientos
class GenerateItineraryView(View):
    def get(self, request):
        route_ids = request.session.get("route_chain", [])
        passenger_ids = request.session.get("passenger_ids", [])

        try:
            last_itinerary = ReservationService.create_automatic_reservations(
                passenger_ids, 
                route_ids
            )
            
            return redirect("view_summary", itinerary_id=last_itinerary.id)
            
        except Exception as e:
            messages.error(request, f"Error generando itinerario: {str(e)}")
            return redirect("choose_itinerary")


# Vista que genera un ticket (código de barras) asociado a un itinerario
class CreateTicketView(View):
    def get(self, request, itinerary_id):
        try:
            itinerary = ItineraryService.get(itinerary_id)
            if not itinerary:
                messages.error(request, "Itinerario no encontrado.")
                return redirect("search_route")
                
            barcode = str(uuid.uuid4())[:10].upper()
            TicketService.create(itinerary, barcode)
            
            return redirect('view_summary', itinerary_id=itinerary.id)
            
        except Exception as e:
            messages.error(request, f"Error creando ticket: {str(e)}")
            return redirect('view_summary', itinerary_id=itinerary_id)


# Vista que muestra el resumen completo del itinerario reservado
class ViewSummary(TemplateView):
    template_name = "view_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        itinerary_id = self.kwargs["itinerary_id"]
        
        try:
            itinerary = ItineraryService.get(itinerary_id)
            if not itinerary:
                raise Exception("Itinerario no encontrado")

            context["itinerary"] = itinerary
            context["passenger"] = itinerary.passenger
            context["segments"] = FlightSegmentService.list_by_itinerary(itinerary)
            context["ticket"] = TicketService.get_by_itinerary(itinerary)
            
        except Exception as e:
            messages.error(self.request, f"Error cargando resumen: {str(e)}")
            context["itinerary"] = None
            
        return context