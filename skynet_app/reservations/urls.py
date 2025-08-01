from django.urls import path
from reservations.views import (
    SearchAndCreateItineraryView,
    ChooseItineraryView,
    SelectItineraryView,
    CreateTicketView,
    GroupSummaryView,
    LoadPassengersView,
    GenerateItineraryView,
    ChooseSeatView,
    TicketDetailView
)

urlpatterns = [

    #  Buscar ruta y guardar cadena de rutas en sesión
    path(
        route='itinerary/search/',
        view=SearchAndCreateItineraryView.as_view(),
        name='create_itinerary'
    ),

    #  Mostrar opciones de itinerario (basado en la cadena de rutas)
    path(
        route='itinerary/choose/',
        view=ChooseItineraryView.as_view(),
        name='choose_itinerary'
    ),

    #  Confirmar selección de itinerario → crear Itinerary real y segmentos
    path(
        route='itinerary/select/',
        view=SelectItineraryView.as_view(),
        name='select_itinerary'
    ),


    # Crear ticket automáticamente
    path(
        route='itinerary/<int:itinerary_id>/create-ticket/',
        view=CreateTicketView.as_view(),
        name='create_ticket'
    ),

    # Ver resumen final del itinerario
    path(
        route='resumen/grupo/',
        view=GroupSummaryView.as_view(),
        name='group_summary'
    ),


    path(
    route='passenger/load/',
    view=LoadPassengersView.as_view(),
    name='load_passengers'
    ),

    path(
        route='itinerary/view/',
        view=GenerateItineraryView.as_view(),
        name='generate_itinerary_view'
    ),

    path(
        route='itinerary/seat/',
        view=ChooseSeatView.as_view(),
        name='choose_seat_view'
    ),

    path(
        "ticket/<int:ticket_id>/", 
        TicketDetailView.as_view(),
        name="ticket_detail"
    ),

]
