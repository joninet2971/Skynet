from django.urls import path
from . import views

urlpatterns = [
    # ejemplo de vista básica
    path('', views.index, name='home'),
]