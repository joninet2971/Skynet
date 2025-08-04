from django.views.generic import TemplateView
from django.contrib import messages
from reservations.services.reservations import (
    ItineraryService, FlightSegmentService, TicketService
)

class GroupSummaryView(TemplateView):
    template_name = "group_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        itinerary_ids = self.request.session.get("created_itineraries", [])

        try:
            itineraries = []
            for iid in itinerary_ids:
                itinerary = ItineraryService.get(iid)
                if itinerary:
                    passenger = itinerary.passenger
                    segments = FlightSegmentService.list_by_itinerary(itinerary)
                    ticket = TicketService.get_by_itinerary(itinerary)

                    flights_data = []
                    for seg in segments:
                        flights_data.append({
                            "flight_number": seg.flight.id,
                            "origin": seg.flight.route.origin_airport.name + " - " + seg.flight.route.origin_airport.city,
                            "destination": seg.flight.route.destination_airport.name + " - " + seg.flight.route.destination_airport.city,
                            "departure_time": seg.flight.departure_time,
                            "arrival_time": seg.flight.arrival_time,
                            "duration": seg.flight.route.estimated_duration,
                            "seat": f"{seg.seat.row}{seg.seat.column}" if seg.seat else "No asignado",
                            "price": seg.price,
                        })

                    itineraries.append({
                        "reservation_code": itinerary.reservation_code,
                        "passenger": {
                            "name": passenger.name,
                            "document": passenger.document,
                            "email": passenger.email,
                            "phone": passenger.phone,
                            "birth_date": passenger.birth_date,
                        },
                        "flights": flights_data,
                        "total_price": sum(f["price"] for f in flights_data),
                        "ticket": ticket,
                    })

            context["group_itineraries"] = itineraries

        except Exception as e:
            messages.error(self.request, f"Error cargando itinerarios del grupo: {str(e)}")
            context["group_itineraries"] = []

        return context
