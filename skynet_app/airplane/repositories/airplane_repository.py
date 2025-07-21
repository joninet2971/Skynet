from ..models import Airplane

def create_airplane(model, capacity, rows, columns):
    return Airplane.objects.create(
        model=model,
        capacity=capacity,
        rows=rows,
        columns=columns
    )