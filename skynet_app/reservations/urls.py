from django.urls import path
from reservations.views import (
    CreatePassengerView,
    AddSegmentView,
    SearchAndCreateItineraryView,
    CreateTicketView,
    ViewSummary
)

urlpatterns = [
    # Alta de pasajero
    path(
        route='passenger/create/', 
        view=CreatePassengerView.as_view(), 
        name='create_passenger'
        ),

    # Búsqueda de ruta + creación automática de itinerario
    path(
        route='itinerary/search/', 
        view=SearchAndCreateItineraryView.as_view(), 
        name='create_itinerary'
        ),

    # Agregar segmentos manualmente (opcional)
    path(
        route='itinerary/<int:itinerary_id>/add-segment/', 
        view=AddSegmentView.as_view(), 
        name='add_segment'
        ),

    # Crear ticket automáticamente
    path(
        route='itinerary/<int:itinerary_id>/create-ticket/', 
        view=CreateTicketView.as_view(), 
        name='create_ticket'
        ),

    # Ver resumen final del itinerario
    path(
        route='itinerary/<int:itinerary_id>/summary/', 
        view=ViewSummary.as_view(), 
        name='view_summary'
        ),
]
