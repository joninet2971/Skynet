from django.urls import path
from api.views.reservations.itinerary_views import SearchAndCreateItineraryAPI

urlpatterns = [
    path("itineraries/search/", SearchAndCreateItineraryAPI.as_view(), name="itineraries-search"),
]