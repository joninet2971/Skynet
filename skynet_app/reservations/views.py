from django.views.generic import FormView
from django.shortcuts import redirect 
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import TemplateView
import uuid
from reservations.forms import (
    PassengerForm, 
    SearchRouteForm, 
    SegmentForm, 
    )
from reservations.repositories.reservations import (
    PassengerRepository,
    FlightSegmentRepository,
    TicketRepository
)
from flight.models import Flight
from airplane.models import Seat
from reservations.models import Itinerary
from reservations.services.reservations import (
    ItineraryService,
    FlightSegmentService,
    TicketService
)


class CreatePassengerView(FormView): #Muestra formulario y guarda pasajero
    template_name = 'create_passenger.html'
    form_class = PassengerForm

    def form_valid(self, form):
        passenger = PassengerRepository.create(**form.cleaned_data)
        return redirect('create_itinerary', passenger_id=passenger.id)


class AddSegmentView(FormView):#Si querés agregar segmentos manualmente
    template_name = 'add_segment.html'
    form_class = SegmentForm

    def get_itinerary(self):
        return get_object_or_404(Itinerary, id=self.kwargs['itinerary_id'])

    def form_valid(self, form):
        itinerary = self.get_itinerary()
        flight = get_object_or_404(Flight, id=form.cleaned_data["flight_id"])
        seat = get_object_or_404(Seat, id=form.cleaned_data["seat_id"])
        FlightSegmentRepository.create(itinerary, flight, seat, form.cleaned_data["price"], "confirmed")
        return redirect('add_segment', itinerary_id=itinerary.id)  # seguir agregando escalas


class SearchAndCreateItineraryView(FormView):#Usuario elige origen/destino y el sistema crea itinerario con escalas
    template_name = 'search_route.html'
    form_class = SearchRouteForm

    def form_valid(self, form):
        origin = form.cleaned_data['origin']
        destination = form.cleaned_data['destination']

        # Ejemplo: obtener pasajero desde query param (id) o sesión, adaptá según tu lógica
        passenger_id = self.request.GET.get("passenger_id")
        passenger = PassengerRepository.get_by_id(passenger_id)

        if not passenger:
            form.add_error(None, "Passenger not found.")
            return self.form_invalid(form)

        # Crea el itinerario con escalas automáticamente
        itinerary = ItineraryService.create_auto(
            passenger=passenger,
            origin_code=origin.code,
            destination_code=destination.code
        )

        return redirect('view_summary', itinerary_id=itinerary.id)
    

class CreateTicketView(View):  # crea ticket automaticamente 
    def get(self, request, itinerary_id):
        itinerary = get_object_or_404(Itinerary, id=itinerary_id)

        # Generar barcode automáticamente
        barcode = str(uuid.uuid4())[:10].upper()

        # Crear ticket
        TicketRepository.create(itinerary=itinerary, barcode=barcode)

        return redirect('view_summary', itinerary_id=itinerary.id)
    
class ViewSummary(TemplateView):
    template_name = "view_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        itinerary = get_object_or_404(Itinerary, id=self.kwargs["itinerary_id"])

        context["itinerary"] = itinerary
        context["passenger"] = itinerary.passenger
        context["segments"] = FlightSegmentService.list_by_itinerary(itinerary)
        context["ticket"] = TicketService.get_by_itinerary(itinerary)

        return context