from ..models import Airplane
from django.shortcuts import get_object_or_404
from ..models import Seat

def create_airplane(model, capacity, rows, columns):
    return Airplane.objects.create(
        model=model,
        capacity=capacity,
        rows=rows,
        columns=columns
    )

def get_all_airplanes():
    return Airplane.objects.all()

def get_airplane_by_id(airplane_id):
    return get_object_or_404(Airplane, id=airplane_id)

def delete_airplane(airplane):
    airplane.delete()

def get_seats_by_airplane(airplane_id):
    return Seat.objects.filter(airplane_id=airplane_id)

def update_airplane(airplane, data):
    airplane.model = data['model']
    airplane.capacity = data['capacity']
    airplane.rows = data['rows']
    airplane.columns = data['columns']
    airplane.save()
    return airplane