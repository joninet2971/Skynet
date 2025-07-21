from django.urls import path
from .views import create_airplane_view

urlpatterns = [
    path('create/', create_airplane_view, name='create_airplane'),
]