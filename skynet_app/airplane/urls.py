from django.urls import path
from airplane.views.airplane_view import create_airplane_view, list_airplanes_view, delete_airplane_view, edit_airplane_view, view_airplane_view

urlpatterns = [
    path('create/', create_airplane_view, name='create_airplane'),
    path('', list_airplanes_view, name='airplane_list'),
    path('delete/<int:airplane_id>/', delete_airplane_view, name='delete_airplane'),
    path('edit/<int:airplane_id>/', edit_airplane_view, name='edit_airplane'),
    path('<int:airplane_id>/', view_airplane_view, name='view_airplane'),
]
