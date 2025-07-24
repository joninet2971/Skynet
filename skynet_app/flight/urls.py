from django.urls import path
from flight.views import AirportList

urlpatterns = [
    path(
        route='airport_list/',
        view=AirportList.as_view(),
        name='airport_list'
    )
]
