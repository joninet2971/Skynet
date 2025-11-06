from django.urls import path
from api.views.airplane.views import AirplaneAPIView

urlpatterns = [
    path('airplanes/', AirplaneAPIView.as_view()),          # GET lista / POST crear
    path('airplanes/<int:pk>/', AirplaneAPIView.as_view()), # GET detalle / PUT / PATCH / DELETE
]