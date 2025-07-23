from django import forms
from reservations.models import (
    Passenger
    )
from flight.models import Airport 

class SearchRouteForm(forms.Form):
    origin = forms.ModelChoiceField(queryset=Airport.objects.all(), label="Origin Airport")
    destination = forms.ModelChoiceField(queryset=Airport.objects.all(), label="Destination Airport")

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['name', 'document', 'email', 'phone', 'birth_date', 'document_type']

class SegmentForm(forms.Form):
    flight_id = forms.IntegerField()
    seat_id = forms.IntegerField()
    price = forms.DecimalField(max_digits=10, decimal_places=2)

