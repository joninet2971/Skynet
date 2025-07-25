from django.contrib import admin
from .models import Airplane, Seat

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ('model', 'rows', 'columns')
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('number', 'airplane', 'row', 'column', 'type', 'status')

    def has_delete_permission(self, request, obj=None):
        return False

