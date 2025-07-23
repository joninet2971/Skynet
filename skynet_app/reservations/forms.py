from django import forms
from reservations.models import Passenger, Itinerary, Ticket

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['name', 'document', 'email', 'phone', 'birth_date', 'document_type']

class ItineraryForm(forms.Form):
    reservation_code = forms.CharField(max_length=100)

class SegmentForm(forms.Form):
    flight_id = forms.IntegerField()
    seat_id = forms.IntegerField()
    price = forms.DecimalField(max_digits=10, decimal_places=2)

class TicketForm(forms.Form):
    barcode = forms.CharField(max_length=100)
