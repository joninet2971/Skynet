from django.contrib import admin
from .models import Airplane, Seat

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ('model', 'capacity', 'rows', 'columns')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('number', 'airplane', 'row', 'column', 'type', 'status')
