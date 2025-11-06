from django.urls import path
from api.views.reservations.itinerary_views import (
    SearchAndCreateItineraryAPI,
    ChooseItineraryAPI
    )
from api.views.reservations.passenger_views import LoadPassengersAPI
from api.views.reservations.seat_views import ChooseSeatNormalizedViewAPI
from api.views.reservations.summary_views import GroupSummaryPreviewAPI
from api.views.reservations.confirm_api import ConfirmItineraryAPI

urlpatterns = [
    path("itineraries/search/", SearchAndCreateItineraryAPI.as_view(), name="itineraries-search"),
    path("itineraries/<str:token>/choose/", ChooseItineraryAPI.as_view(), name="itineraries-choose"),
    path("itineraries/<str:token>/passengers/", LoadPassengersAPI.as_view(), name="itineraries-passengers"),
    path("itineraries/<str:token>/seat/", ChooseSeatNormalizedViewAPI.as_view(), name="itineraries-seat"),
    path("itineraries/<str:token>/summary/", GroupSummaryPreviewAPI.as_view(), name="group-summary-preview"),
    path("itineraries/<str:token>/confirm/", ConfirmItineraryAPI.as_view(), name="confirm-itinerary"),
]

