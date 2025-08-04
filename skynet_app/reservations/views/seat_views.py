from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from reservations.services.reservations import (
    SeatService, ReservationService, TicketService
)
import uuid

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
            itineraries = ReservationService.create_reservations_with_seats(
                passenger_ids, 
                route_ids, 
                request.POST,
                status="reserved"  
            )
            
            # Guardamos los IDs en sesión para mostrarlos luego
            request.session["created_itineraries"] = [i.id for i in itineraries]

            messages.success(request, "Asientos asignados correctamente.")
            return redirect("group_summary")  # Redirige a la nueva vista grupal

        except Exception as e:
            messages.error(request, f"Error al asignar asientos: {str(e)}")
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
