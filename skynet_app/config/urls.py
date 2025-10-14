from django.contrib import admin
<<<<<<< HEAD
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include

<<<<<<< HEAD:skynet_app/skynet_app/urls.py
urlpatterns = i18n_patterns(
=======
=======
from django.urls import path, include

>>>>>>> main-api

#def trigger_error(request):
#    division_by_zero = 1 / 0

urlpatterns = [
<<<<<<< HEAD
>>>>>>> 1cd4108 (iniciar proyecto con api):skynet_app/config/urls.py
=======
>>>>>>> main-api
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('airplanes/', include('airplane.urls')),
    path('reservations/', include('reservations.urls')),
    path('flight/', include('flight.urls')),
<<<<<<< HEAD
<<<<<<< HEAD:skynet_app/skynet_app/urls.py
)
=======
=======
>>>>>>> main-api
    #API
    path("api/", include("api.urls.reservations.urls")),

]
<<<<<<< HEAD
>>>>>>> 1cd4108 (iniciar proyecto con api):skynet_app/config/urls.py
=======
>>>>>>> main-api





