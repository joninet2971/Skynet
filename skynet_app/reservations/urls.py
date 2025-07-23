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
    path('passenger/create/', CreatePassengerView.as_view(), name='create_passenger'),

    # Búsqueda de ruta + creación automática de itinerario
    path('itinerary/search/', SearchAndCreateItineraryView.as_view(), name='create_itinerary'),

    # Agregar segmentos manualmente (opcional)
    path('itinerary/<int:itinerary_id>/add-segment/', AddSegmentView.as_view(), name='add_segment'),

    # Crear ticket automáticamente
    path('itinerary/<int:itinerary_id>/create-ticket/', CreateTicketView.as_view(), name='create_ticket'),

    # Ver resumen final del itinerario
    path('itinerary/<int:itinerary_id>/summary/', ViewSummary.as_view(), name='view_summary'),
]
