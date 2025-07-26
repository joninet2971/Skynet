from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from collections import namedtuple
import uuid

from reservations.forms import PassengerForm, SearchRouteForm, SegmentForm
from reservations.repositories.reservations import (
    PassengerRepository,
    FlightSegmentRepository,
    TicketRepository
)
from flight.models import Flight, Route
from airplane.models import Seat
from reservations.models import Itinerary, Passenger
from reservations.services.reservations import (
    ItineraryService,
    FlightSegmentService,
    TicketService
)
from reservations.services.route_finder import find_route_chain


class CreatePassengerView(FormView):
    template_name = 'create_passenger.html'
    form_class = PassengerForm

    def form_valid(self, form):
        passenger = PassengerRepository.create(**form.cleaned_data)
        self.request.session['passenger_id'] = passenger.id
        return redirect('create_itinerary', passenger_id=passenger.id)


class LoadPassengersView(View):
    template_name = "create_passenger.html"

    def get(self, request):
        passenger_count = int(request.session.get("passenger_count", 1))
        return render(request, self.template_name, {"form": PassengerForm(), "count": passenger_count})

    def post(self, request):
        passenger_count = int(request.session.get("passenger_count", 1))
        passengers = []

        for i in range(passenger_count):
            form_data = {
                'first_name': request.POST.get(f'first_name_{i}'),
                'last_name': request.POST.get(f'last_name_{i}'),
                'document_number': request.POST.get(f'document_number_{i}'),
            }
            form = PassengerForm(form_data)
            if form.is_valid():
                passenger = PassengerRepository.create(**form.cleaned_data)
                passengers.append(passenger)
            else:
                return render(request, self.template_name, {
                    "form": form,
                    "count": passenger_count,
                    "range": range(passenger_count),  # <-- Esto es clave para el loop en el template
                    "error": f"Error en el pasajero {i + 1}"
                })

        request.session['passenger_ids'] = [p.id for p in passengers]
        return redirect("select_itinerary")


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
        return redirect('add_segment', itinerary_id=itinerary.id)


class SearchAndCreateItineraryView(FormView):
    template_name = 'search_route.html'
    form_class = SearchRouteForm

    def form_valid(self, form):
        origin = form.cleaned_data['origin']
        destination = form.cleaned_data['destination']

        route_chain = find_route_chain(origin.code, destination.code)

        if not route_chain:
            form.add_error(None, "No se encontró una ruta válida entre esos aeropuertos.")
            return self.form_invalid(form)

        self.request.session["route_chain_ids"] = [r.id for r in route_chain]
        self.request.session["search_date"] = str(form.cleaned_data['date'])
        self.request.session["passenger_count"] = form.cleaned_data['passengers']

        url = reverse("choose_itinerary")
        return redirect(url)


ItineraryOption = namedtuple("ItineraryOption", ["id", "route_summary", "duration", "total_price"])


class ChooseItineraryView(TemplateView):
    template_name = "choose_itinerary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_ids = self.request.session.get("route_chain_ids", [])
        routes = Route.objects.filter(id__in=route_ids).select_related("origin_airport", "destination_airport")

        if routes:
            summary = " → ".join([r.origin_airport.code for r in routes] + [routes.last().destination_airport.code])
            duration = sum(r.estimated_duration for r in routes)
            total_price = len(routes) * 5000

            option = ItineraryOption(
                id=1,
                route_summary=summary,
                duration=duration,
                total_price=total_price
            )

            context["itineraries"] = [option]
            context["origin"] = routes.first().origin_airport.code
            context["destination"] = routes.last().destination_airport.code
        else:
            context["itineraries"] = []
            context["origin"] = None
            context["destination"] = None

        context["date"] = self.request.session.get("search_date")
        context["passengers"] = self.request.session.get("passenger_count")

        return context


class SelectItineraryView(View):
    def post(self, request):
        route_ids = request.session.get("route_chain_ids", [])
        passenger_ids = request.session.get("passenger_ids", [])
        passengers = Passenger.objects.filter(id__in=passenger_ids)
        routes = Route.objects.filter(id__in=route_ids).select_related("origin_airport", "destination_airport")

        last_itinerary = None
        for passenger in passengers:
            itinerary = Itinerary.objects.create(passenger=passenger)
            last_itinerary = itinerary

            for route in routes:
                flight = Flight.objects.filter(route=route, status="active").first()
                seat = Seat.objects.filter(airplane=flight.airplane, is_available=True).first()
                FlightSegmentRepository.create(
                    itinerary=itinerary,
                    flight=flight,
                    seat=seat,
                    price=flight.base_price,
                    status="confirmed"
                )

        return redirect('view_summary', itinerary_id=last_itinerary.id)


class CreateTicketView(View):
    def get(self, request, itinerary_id):
        itinerary = get_object_or_404(Itinerary, id=itinerary_id)
        barcode = str(uuid.uuid4())[:10].upper()
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