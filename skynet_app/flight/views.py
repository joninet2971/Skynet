from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView, 
    ListView, 
)
from django.urls import reverse_lazy
from form import AirportForm, RouteForm, FlightForm
from .models import Airport
from .services import AirportService, RouteService, FlightService

class AirportList(ListView):
    template_name='airports_list.html'
    context_object_name = 'airports'

    def get(self):
        return AirportService.get_all()
    