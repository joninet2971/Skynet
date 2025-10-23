from django.urls import path
from api.views.reservations.itinerary_views import (
    SearchAndCreateItineraryAPI,
    ChooseItineraryView
    )
from api.views.reservations.passenger_views import (
    LoadPassengers
)

urlpatterns = [
    path("itineraries/search/", SearchAndCreateItineraryAPI.as_view(), name="itineraries-search"),
    path("itineraries/<str:token>/choose/", ChooseItineraryView.as_view(), name="itineraries-choose"),

    path("itineraries/<str:token>/passengers/", LoadPassengers.as_view(), name="itineraries-passengers"),
]

