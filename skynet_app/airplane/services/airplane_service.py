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