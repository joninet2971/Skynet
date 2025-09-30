from django.contrib import admin
from django.urls import path, include


#def trigger_error(request):
#    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('airplanes/', include('airplane.urls')),
    path('reservations/', include('reservations.urls')),
    path('flight/', include('flight.urls')),
    #API
    path("api/", include("api.urls.reservations.urls")),

]





