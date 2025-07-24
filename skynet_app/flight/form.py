from django import forms
from .models import Airport, Route, Flight

class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = '__all__'

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = '__all__'

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'
