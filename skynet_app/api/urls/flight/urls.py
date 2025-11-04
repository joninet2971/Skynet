from rest_framework.routers import DefaultRouter
from api.views.flight.views import AirportViewSet, RouteViewSet, FlightViewSet

router = DefaultRouter()
router.register(r'airports', AirportViewSet, basename='airport')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'flights', FlightViewSet, basename='flight')

urlpatterns = router.urls
