from django.urls import path
from .views import (
    AirportList, AirportCreate, AirportUpdate, AirportDelete,
    RouteList, RouteCreate, RouteUpdate, RouteDelete,
    FlightList, FlightCreate, FlightUpdate, FlightDelete,
)

urlpatterns = [
    # Airports
    path('airports/', AirportList.as_view(), name='airport_list'),
    path('airports/nuevo/', AirportCreate.as_view(), name='airport_create'),
    path('airports/<int:pk>/editar/', AirportUpdate.as_view(), name='airport_update'),
    path('airports/<int:pk>/eliminar/', AirportDelete.as_view(), name='airport_delete'),

    # Routes
    path('routes/', RouteList.as_view(), name='route_list'),
    path('routes/nuevo/', RouteCreate.as_view(), name='route_create'),
    path('routes/<int:pk>/editar/', RouteUpdate.as_view(), name='route_update'),
    path('routes/<int:pk>/eliminar/', RouteDelete.as_view(), name='route_delete'),

    # Flights
    path('flights/', FlightList.as_view(), name='flight_list'),
    path('flights/nuevo/', FlightCreate.as_view(), name='flight_create'),
    path('flights/<int:pk>/editar/', FlightUpdate.as_view(), name='flight_update'),
    path('flights/<int:pk>/eliminar/', FlightDelete.as_view(), name='flight_delete'),
]
