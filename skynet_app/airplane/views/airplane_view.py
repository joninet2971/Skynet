from django.shortcuts import render, redirect
from ..forms import AirplaneForm
from ..services import airplane_service
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

