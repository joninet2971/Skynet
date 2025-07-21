from ..repositories import airplane_repository
from django.core.exceptions import ValidationError

def create_airplane_service(data):
    model = data['model']
    capacity = data['capacity']
    rows = data['rows']
    columns = data['columns']

    if capacity != rows * columns:
        raise ValidationError("La capacidad debe ser igual a filas × columnas.")

    if rows <= 0 or columns <= 0:
        raise ValidationError("Las filas y columnas deben ser números enteros positivos.")

    return airplane_repository.create_airplane(model, capacity, rows, columns)
