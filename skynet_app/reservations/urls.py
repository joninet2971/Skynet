from django.urls import path
from reservations.views import (
    CreatePassengerView,
    AddSegmentView,
    SearchAndCreateItineraryView,
    ChooseItineraryView,
    SelectItineraryView,
    CreateTicketView,
    ViewSummary,
    LoadPassengersView
)

urlpatterns = [
    # 1. Crear pasajero
    path(
        route='passenger/create/',
        view=CreatePassengerView.as_view(),
        name='create_passenger'
    ),

    # 2. Buscar ruta y guardar cadena de rutas en sesión
    path(
        route='itinerary/search/',
        view=SearchAndCreateItineraryView.as_view(),
        name='create_itinerary'
    ),

    # 3. Mostrar opciones de itinerario (basado en la cadena de rutas)
    path(
        route='itinerary/choose/',
        view=ChooseItineraryView.as_view(),
        name='choose_itinerary'
    ),

    # 4. Confirmar selección de itinerario → crear Itinerary real y segmentos
    path(
        route='itinerary/select/',
        view=SelectItineraryView.as_view(),
        name='select_itinerary'
    ),

    # 5. Agregar segmentos manualmente (opcional)
    path(
        route='itinerary/<int:itinerary_id>/add-segment/',
        view=AddSegmentView.as_view(),
        name='add_segment'
    ),

    # 6. Crear ticket automáticamente
    path(
        route='itinerary/<int:itinerary_id>/create-ticket/',
        view=CreateTicketView.as_view(),
        name='create_ticket'
    ),

    # 7. Ver resumen final del itinerario
    path(
        route='itinerary/<int:itinerary_id>/summary/',
        view=ViewSummary.as_view(),
        name='view_summary'
    ),

    path(
    route='passenger/load/',
    view=LoadPassengersView.as_view(),
    name='load_passengers'
),
]
