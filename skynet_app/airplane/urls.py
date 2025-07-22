from django.urls import path
from airplane.views.airplane_view import create_airplane_view  
from airplane.views.airplane_view import list_airplanes_view

urlpatterns = [
    path('create/', create_airplane_view, name='create_airplane'),
    path('', list_airplanes_view, name='airplane_list'),
]
