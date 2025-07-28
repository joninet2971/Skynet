from django import forms
from reservations.models import Passenger
from flight.models import Airport 

class SearchRouteForm(forms.Form):
    origin = forms.ModelChoiceField(queryset=Airport.objects.all())
    destination = forms.ModelChoiceField(queryset=Airport.objects.all())
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    passengers = forms.IntegerField(min_value=1, max_value=10)

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['name', 'document', 'email', 'phone', 'birth_date', 'document_type']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'document': forms.TextInput(attrs={'placeholder': 'Número de documento'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Teléfono'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'document_type': forms.Select(choices=Passenger.STATUS_CHOICES),
        }
        labels = {
            'name': 'Nombre completo',
            'document': 'Documento',
            'email': 'Email',
            'phone': 'Teléfono',
            'birth_date': 'Fecha de nacimiento',
            'document_type': 'Tipo de documento',
        }

class SegmentForm(forms.Form):
    flight_id = forms.IntegerField()
    seat_id = forms.IntegerField()
    price = forms.DecimalField(max_digits=10, decimal_places=2)
