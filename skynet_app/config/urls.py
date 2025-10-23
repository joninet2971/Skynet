from django.contrib import admin
<<<<<<< HEAD

from django.urls import path, include


#def trigger_error(request):
#    division_by_zero = 1 / 0

urlpatterns = [
=======
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # JWT Authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + i18n_patterns(
>>>>>>> api-joni-001
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('airplanes/', include('airplane.urls')),
    path('reservations/', include('reservations.urls')),
    path('flight/', include('flight.urls')),
<<<<<<< HEAD

    #API
    path("api/", include("api.urls.reservations.urls")),

]




=======
    
    # APIs
    path('api/airplane/', include('api.urls.airplane.urls')),
)
>>>>>>> api-joni-001


