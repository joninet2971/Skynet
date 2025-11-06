from django.urls import path
from api.views.flight.views import (
    AirportListCreateAPI, AirportDetailAPI,
    RouteListCreateAPI, RouteDetailAPI,
    FlightListCreateAPI, FlightDetailAPI
)

urlpatterns = [
    path("airports/", AirportListCreateAPI.as_view()),
    path("airports/<int:pk>/", AirportDetailAPI.as_view()),

    path("routes/", RouteListCreateAPI.as_view()),
    path("routes/<int:pk>/", RouteDetailAPI.as_view()),

    path("flights/", FlightListCreateAPI.as_view()),
    path("flights/<int:pk>/", FlightDetailAPI.as_view()),
]
