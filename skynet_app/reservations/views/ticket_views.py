from django.views.generic import DetailView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from reservations.models import Ticket
from reservations.services.reservations import (
    TicketService, FlightSegmentService, ItineraryService
)
import uuid

# Vista que genera un ticket (código de barras) asociado a un itinerario
class CreateTicketView(View):
    def get(self, request, itinerary_id):
        try:
            itinerary = ItineraryService.get(itinerary_id)
            if not itinerary:
                messages.error(request, "Itinerario no encontrado.")
                return redirect("search_route")
            
            # Confirmar los asientos antes de emitir ticket
            print("entre aca")
            for segment in itinerary.segments.all():
                print("entre aca 2")
                if segment.status == "reserved":
                    print("entre aca 3")
                    segment.status = "confirmed"
                    segment.save()
                
            barcode = str(uuid.uuid4())[:10].upper()
            ticket = TicketService.create(itinerary, barcode)
            return redirect('ticket_detail', ticket_id=ticket.id)
            
        except Exception as e:
            messages.error(request, f"Error creando ticket: {str(e)}")
            return redirect('group_summary')
        

class TicketDetailView(DetailView):
    model = Ticket
    template_name = "ticket_detail.html"
    context_object_name = "ticket"

    def get_object(self):
        return get_object_or_404(Ticket, id=self.kwargs["ticket_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = context["ticket"]
        itinerary = ticket.itinerary
        segments = FlightSegmentService.list_by_itinerary(itinerary)

        vuelos = []
        for seg in segments:
            vuelos.append({
                "flight_number": seg.flight.id,
                "origin": seg.flight.route.origin_airport.code +" - "+ seg.flight.route.origin_airport.city,
                "destination": seg.flight.route.destination_airport.code +" - "+ seg.flight.route.destination_airport.city,
                "departure": seg.flight.departure_time,
                "arrival": seg.flight.arrival_time,
                "duration": seg.flight.route.estimated_duration,
                "seat": f"{seg.seat.row}{seg.seat.column}" if seg.seat else "No asignado",
                "price": seg.price,
            })

        context["passenger"] = itinerary.passenger
        context["reservation_code"] = itinerary.reservation_code
        context["flights"] = vuelos
        context["total_price"] = sum(v["price"] for v in vuelos)
        return context


