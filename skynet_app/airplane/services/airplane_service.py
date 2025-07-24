from ..repositories import airplane_repository
from django.core.exceptions import ValidationError

def create_airplane_service(data):
    model = data['model']
    capacity = data['capacity']
    rows = data['rows']
    columns = data['columns']

    if capacity != rows * columns:
        raise ValidationError("The capacity must be equal to rows × columns.")

    if rows <= 0 or columns <= 0:
        raise ValidationError("Rows and columns must be positive integers.")

    return airplane_repository.create_airplane(model, capacity, rows, columns)


def get_all_airplanes_service():
    return airplane_repository.get_all_airplanes()

def delete_airplane_service(airplane_id):
    airplane = airplane_repository.get_airplane_by_id(airplane_id)

    if airplane.capacity <= 0:
        raise ValidationError("Cannot delete airplane with invalid capacity.")

    airplane_repository.delete_airplane(airplane)

def get_airplane(airplane_id):
    return airplane_repository.get_airplane_by_id(airplane_id)

def update_airplane_service(airplane_id, data):
    airplane = airplane_repository.get_airplane_by_id(airplane_id)

    if data['capacity'] != data['rows'] * data['columns']:
        raise ValidationError("The capacity must be equal to rows × columns.")

    if data['rows'] <= 0 or data['columns'] <= 0:
        raise ValidationError("Rows and columns must be positive integers.")

    return airplane_repository.update_airplane(airplane, data)

def get_airplane_seats(airplane_id):
    return airplane_repository.get_seats_by_airplane(airplane_id)