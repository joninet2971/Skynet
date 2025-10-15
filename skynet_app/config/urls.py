from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('airplanes/', include('airplane.urls')),
    path('reservations/', include('reservations.urls')),
    path('flight/', include('flight.urls')),
    
    # APIs
    path('api/flight/', include('api.urls.flight.urls')),
    path('api/airplane/', include('api.urls.airplane.urls')),
)


