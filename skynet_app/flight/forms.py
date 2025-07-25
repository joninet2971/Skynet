from django import forms
from .models import Airport, Route, Flight

class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del aeropuerto'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código (ej: EZE)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'}),
        }

    def clean_code(self):
        code = self.cleaned_data['code'].upper()
        if not code.isalpha():
            raise forms.ValidationError("El código debe contener solo letras.")
        if len(code) > 5:
            raise forms.ValidationError("El código no puede superar 5 caracteres.")
        return code

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = '__all__'
        widgets = {
            'origin_airport': forms.Select(attrs={'class': 'form-select'}),
            'destination_airport': forms.Select(attrs={'class': 'form-select'}),
            'estimated_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin_airport')
        destination = cleaned_data.get('destination_airport')
        if origin and destination and origin == destination:
            raise forms.ValidationError("El aeropuerto de origen y destino deben ser diferentes.")
        return cleaned_data

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'
        widgets = {
            'airplane': forms.Select(attrs={'class': 'form-select'}),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'departure_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get('departure_time')
        arrival = cleaned_data.get('arrival_time')
        if departure and arrival and arrival <= departure:
            raise forms.ValidationError("La hora de llegada debe ser posterior a la de salida.")
        return cleaned_data
