from rest_framework.routers import DefaultRouter
from api.views.airplane.views import AirplaneViewSet

# Router para el ViewSet
router = DefaultRouter()
router.register(r'airplanes', AirplaneViewSet, basename='airplane')

urlpatterns = router.urls