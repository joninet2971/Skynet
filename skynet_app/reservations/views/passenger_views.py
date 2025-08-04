from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from reservations.forms import PassengerForm
from reservations.services.reservations import PassengerService

# Vista para cargar múltiples pasajeros en base a la cantidad seleccionada
class LoadPassengersView(View):
    template_name = "create_passenger.html"

    def get(self, request):
        passenger_count = int(request.session.get("passenger_count", 1))
        return render(request, self.template_name, {
            "form": PassengerForm(),
            "count": passenger_count,
            "range": range(passenger_count)
        })

    def post(self, request):
        passenger_count = int(request.session.get("passenger_count", 1))
        passengers = []

        for i in range(passenger_count):
            form_data = {
                'name': request.POST.get(f'name_{i}'),
                'document': request.POST.get(f'document_{i}'),
                'email': request.POST.get(f'email_{i}'),
                'phone': request.POST.get(f'phone_{i}') or None,
                'birth_date': request.POST.get(f'birth_date_{i}') or None,
                'document_type': request.POST.get(f'document_type_{i}') or None,
            }
            document = form_data["document"]
            
            # Buscar pasajero existente usando el servicio
            existing_passenger = PassengerService.get_by_document(document)

            if existing_passenger:
                passengers.append(existing_passenger)
            else:
                form = PassengerForm(form_data)
                if form.is_valid():
                    try:
                        passenger = PassengerService.create(form.cleaned_data)
                        passengers.append(passenger)
                    except Exception as e:
                        messages.error(request, f"Error creando pasajero {i + 1}: {str(e)}")
                        return render(request, self.template_name, {
                            "form": form,
                            "count": passenger_count,
                            "range": range(passenger_count)
                        })
                else:
                    messages.error(request, f"Error en el pasajero {i + 1}. Verifica los datos.")
                    return render(request, self.template_name, {
                        "form": form,
                        "count": passenger_count,
                        "range": range(passenger_count)
                    })
      
        request.session['passenger_ids'] = [p.id for p in passengers]
        messages.success(request, f"{len(passengers)} pasajero(s) cargado(s) correctamente.")
        return redirect('choose_seat_view')
