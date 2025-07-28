from ..models import Airplane
from django.shortcuts import get_object_or_404
from ..models import Seat

def create_airplane(model, rows, columns):
    return Airplane.objects.create(
        model=model,
        rows=rows,
        columns=columns
    )

def get_all_airplanes():
    return Airplane.objects.filter(enabled=True)

def get_airplane_by_id(airplane_id):
    return get_object_or_404(Airplane, id=airplane_id)

def delete_airplane(airplane):
    airplane.enabled = False
    airplane.save()

def get_seats_by_airplane(airplane_id):
    return Seat.objects.filter(airplane_id=airplane_id)

def update_airplane(airplane, data):
    airplane.model = data['model']
    airplane.rows = data['rows']
    airplane.columns = data['columns']
    airplane.save()
    return airplane