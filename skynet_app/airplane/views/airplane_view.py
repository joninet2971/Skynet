from django.shortcuts import render, redirect
from ..forms import AirplaneForm
from ..services import airplane_service
from ..repositories import airplane_repository
from django.core.exceptions import ValidationError
from django.contrib import messages

def create_airplane_view(request):
    if request.method == 'POST':
        form = AirplaneForm(request.POST)
        if form.is_valid():
            try:
                airplane_service.create_airplane_service(form.cleaned_data)
                messages.success(request, "Airplane created successfully!")
                return redirect('create_airplane')
            except ValidationError as e:
                form.add_error(None, e.message)
                messages.error(request, f"Error creating airplane: {e.message}")
    else:
        form = AirplaneForm()

    return render(request, 'airplane/airplane_create.html', {'form': form})

def list_airplanes_view(request):
    airplanes = airplane_service.get_all_airplanes_service()
    return render(request, 'airplane/airplane_list.html', {'airplanes': airplanes})

def delete_airplane_view(request, airplane_id):
    try:
        airplane_service.delete_airplane_service(airplane_id)
        messages.success(request, "Airplane deleted successfully!")
    except ValidationError as e:
        messages.error(request, f"Error deleting airplane: {e.message}")
    return redirect('airplane_list')

def edit_airplane_view(request, airplane_id):
    airplane = airplane_service.get_airplane(airplane_id)

    if request.method == 'POST':
        form = AirplaneForm(request.POST, instance=airplane)
        if form.is_valid():
            try:
                airplane_service.update_airplane_service(airplane_id, form.cleaned_data)
                messages.success(request, "Airplane updated successfully!")
                return redirect('airplane_list')
            except ValidationError as e:
                form.add_error(None, e.message)
                messages.error(request, f"Error updating airplane: {e.message}")
    else:
        form = AirplaneForm(instance=airplane)

    return render(request, 'airplane/airplane_create.html', {
        'form': form,
        'edit_mode': True
    })
def view_airplane_view(request, airplane_id):
    airplane = airplane_service.get_airplane(airplane_id)
    seats = airplane_service.get_airplane_seats(airplane_id)
    
    row_range = range(1, airplane.rows + 1)
    col_range = range(1, airplane.columns + 1)

    return render(request, 'airplane/airplane_detail.html', {
        'airplane': airplane,
        'seats': seats,
        'row_range': row_range,
        'col_range': col_range
    })

def get_seats_by_airplane(airplane_id):
    return Seat.objects.filter(airplane_id=airplane_id)