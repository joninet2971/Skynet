from django.urls import path
<<<<<<< HEAD
<<<<<<< HEAD
from api.views.reservations.itinerary_views import SearchAndCreateItineraryAPI

urlpatterns = [
    path("itineraries/search/", SearchAndCreateItineraryAPI.as_view(), name="itineraries-search"),
=======
from api.views.reservations.itinerary_views import (
    SearchAndCreateItineraryAPI,
    ChooseItineraryView
    )

urlpatterns = [
    path("itineraries/search/", SearchAndCreateItineraryAPI.as_view(), name="itineraries-search"),
    path("itineraries/choose/", ChooseItineraryView.as_view(), name="itineraries-choose"),

>>>>>>> main-api
=======
from api.views.reservations.itinerary_views import (
    SearchAndCreateItineraryAPI,
    ChooseItineraryView
    )

urlpatterns = [
    path("itineraries/search/", SearchAndCreateItineraryAPI.as_view(), name="itineraries-search"),
    path("itineraries/choose/", ChooseItineraryView.as_view(), name="itineraries-choose"),

>>>>>>> db674df (intinerary view)
]