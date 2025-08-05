from django.contrib import admin
from home.models import CarouselImage
# Register your models here.


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('title',)