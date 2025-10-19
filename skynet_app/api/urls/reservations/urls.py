from django.urls import path
from api.views.reservations.itinerary_views import (
    SearchAndCreateItineraryAPI,
    ChooseItineraryView
    )

urlpatterns = [
    path("itineraries/search/", SearchAndCreateItineraryAPI.as_view(), name="itineraries-search"),
    path("itineraries/choose/", ChooseItineraryView.as_view(), name="itineraries-choose"),
]

