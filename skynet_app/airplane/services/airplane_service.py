from ..repositories import airplane_repository
from django.core.exceptions import ValidationError

from airplane.models import Seat
from django.core.exceptions import ValidationError
from ..repositories import airplane_repository

def create_airplane_service(data):
    model = data['model']
    rows = data['rows']
    columns = data['columns']

    if rows <= 0 or columns <= 0:
        raise ValidationError("Rows and columns must be positive integers.")

    # Crear el avión
    airplane = airplane_repository.create_airplane(model, rows, columns)

    # Crear los asientos
    for row in range(1, rows + 1):
        for col in range(1, columns + 1):
            column_letter = chr(64 + col)  # A, B, C...
            Seat.objects.create(
                airplane=airplane,
                number=f"{row}{column_letter}",
                row=row,
                column=column_letter
            )

    return airplane


def get_all_airplanes_service():
    return airplane_repository.get_all_airplanes()

def delete_airplane_service(airplane_id):
    airplane = airplane_repository.get_airplane_by_id(airplane_id)

    if not airplane.enabled:
        raise ValidationError("This airplane is already disabled.")

    return airplane_repository.delete_airplane(airplane)

def get_airplane(airplane_id):
    return airplane_repository.get_airplane_by_id(airplane_id)

def update_airplane_service(airplane_id, data):
    airplane = airplane_repository.get_airplane_by_id(airplane_id)

    if data['rows'] <= 0 or data['columns'] <= 0:
        raise ValidationError("Rows and columns must be positive integers.")

    # Actualizar datos del avión
    airplane = airplane_repository.update_airplane(airplane, data)

    # Borrar los asientos existentes
    Seat.objects.filter(airplane=airplane).delete()

    # Crear nuevos asientos
    for row in range(1, airplane.rows + 1):
        for col in range(1, airplane.columns + 1):
            column_letter = chr(64 + col)  # A = 65
            Seat.objects.create(
                airplane=airplane,
                number=f"{row}{column_letter}",
                row=row,
                column=column_letter
            )

    return airplane

def get_airplane_seats(airplane_id):
    return airplane_repository.get_seats_by_airplane(airplane_id)