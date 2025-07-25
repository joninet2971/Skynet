from django.contrib import admin
from .models import Airport, Route, Flight

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "country")
    search_fields = ("name", "code", "city")

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("origin_airport", "destination_airport", "estimated_duration")
    list_filter = ("origin_airport", "destination_airport")

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "airplane", "route", "departure_time", "arrival_time", "status", "base_price")
    list_filter = ("airplane", "route", "status")
    search_fields = ("id", "airplane__model")
    date_hierarchy = "departure_time"
