from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('airplanes/', include('airplane.urls')),
    path('reservations/', include('reservations.urls')),
    path('flight/', include('flight.urls')),
]




