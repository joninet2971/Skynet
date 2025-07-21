from django.shortcuts import render, redirect
from .forms import AirplaneForm
from .services import airplane_service

def create_airplane_view(request):
    if request.method == 'POST':
        form = AirplaneForm(request.POST)
        if form.is_valid():
            airplane_service.create_airplane_service(form.cleaned_data)
            return redirect('airplane_list')  
    else:
        form = AirplaneForm()
    return render(request, 'airplane/airplane_create.html', {'form': form})
