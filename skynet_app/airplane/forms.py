from django import forms
from .models import Airplane

class AirplaneForm(forms.ModelForm):
    class Meta:
        model = Airplane
        fields = ['model', 'capacity', 'rows', 'columns']
