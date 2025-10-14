from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include

<<<<<<< HEAD:skynet_app/skynet_app/urls.py
urlpatterns = i18n_patterns(
=======

#def trigger_error(request):
#    division_by_zero = 1 / 0

urlpatterns = [
>>>>>>> 1cd4108 (iniciar proyecto con api):skynet_app/config/urls.py
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('airplanes/', include('airplane.urls')),
    path('reservations/', include('reservations.urls')),
    path('flight/', include('flight.urls')),
<<<<<<< HEAD:skynet_app/skynet_app/urls.py
)
=======
    #API
    path("api/", include("api.urls.reservations.urls")),

]
>>>>>>> 1cd4108 (iniciar proyecto con api):skynet_app/config/urls.py





