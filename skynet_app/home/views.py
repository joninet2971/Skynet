from django.shortcuts import render
from reservations.forms import SearchRouteForm 

def home_view(request):
    form = SearchRouteForm()
    return render(request, "home/index.html", {"form": form})

