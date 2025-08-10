from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Airport, Route, Flight

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'country')
    search_fields = ('name', 'code', 'city', 'country')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('origin_airport', 'destination_airport', 'estimated_duration')
    search_fields = ('origin_airport__name', 'destination_airport__name')
    list_filter = ('origin_airport', 'destination_airport')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('airplane', 'route', 'departure_time', 'arrival_time', 'status', 'base_price')
    search_fields = ('airplane__name', 'route__origin_airport__code', 'route__destination_airport__code')
    list_filter = ('status', 'departure_time', 'arrival_time')
