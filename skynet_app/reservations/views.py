from django.views.generic import FormView
from django.shortcuts import redirect 
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .forms import PassengerForm, ItineraryForm, SegmentForm, TicketForm
from reservations.repositories import (
    PassengerRepository,
    ItineraryRepository,
    FlightSegmentRepository,
    TicketRepository
)
from flight.models import Flight
from airplane.models import Seat
from reservations.models import Passenger, Itinerary


class CreatePassengerView(FormView):
    template_name = 'create_passenger.html'
    form_class = PassengerForm

    def form_valid(self, form):
        passenger = PassengerRepository.create(**form.cleaned_data)
        return redirect('create_itinerary', passenger_id=passenger.id)


class CreateItineraryView(FormView):
    template_name = 'create_itinerary.html'
    form_class = ItineraryForm

    def get_passenger(self):
        return get_object_or_404(Passenger, id=self.kwargs['passenger_id'])

    def form_valid(self, form):
        passenger = self.get_passenger()
        itinerary = ItineraryRepository.create(passenger, form.cleaned_data["reservation_code"])
        return redirect('add_segment', itinerary_id=itinerary.id)


class AddSegmentView(FormView):
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


class CreateTicketView(FormView):
    template_name = 'create_ticket.html'
    form_class = TicketForm

    def get_itinerary(self):
        return get_object_or_404(Itinerary, id=self.kwargs['itinerary_id'])

    def form_valid(self, form):
        itinerary = self.get_itinerary()
        TicketRepository.create(itinerary, form.cleaned_data["barcode"])
        return redirect('view_summary', itinerary_id=itinerary.id)
