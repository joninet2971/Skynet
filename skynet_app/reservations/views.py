# Django imports
from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from collections import namedtuple
import uuid

# Formularios y Repositorios
from reservations.forms import PassengerForm, SearchRouteForm
from reservations.repositories.reservations import (
    PassengerRepository, FlightSegmentRepository, TicketRepository
)

# Modelos
from flight.models import Flight, Route
from airplane.models import Seat
from reservations.models import Itinerary, Passenger, FlightSegment

# Servicios
from reservations.services.reservations import (
    ItineraryService, FlightSegmentService, TicketService
)

# Algoritmo para encontrar rutas
from reservations.services.route_finder import find_route_chain

    
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
            document = request.POST.get(f'document_{i}')
            passenger = Passenger.objects.filter(document=document).first()

            if passenger:
                passengers.append(passenger)
            else:
                form = PassengerForm(form_data)
                if form.is_valid():
                    passenger = PassengerRepository.create(**form.cleaned_data)
                    passengers.append(passenger)
                else:
                    return render(request, self.template_name, {
                        "form": form,
                        "count": passenger_count,
                        "range": range(passenger_count),
                        "error": f"Error en el pasajero {i + 1}"
                    })



        request.session['passenger_ids'] = [p.id for p in passengers]
        return redirect('choose_seat_view')


# Vista para buscar rutas posibles y guardar los datos en sesión
class SearchAndCreateItineraryView(FormView):
    template_name = 'search_route.html'
    form_class = SearchRouteForm

    def form_valid(self, form):
        origin = form.cleaned_data['origin']
        destination = form.cleaned_data['destination']

        route_chains = find_route_chain(origin.code, destination.code)

        if not route_chains:
            form.add_error(None, "No se encontró una ruta válida entre esos aeropuertos.")
            return self.form_invalid(form)

        fecha = form.cleaned_data['date']
        rutas_validas = []

        for chain in route_chains:
            vuelos = []
            for tramo in chain:
                vuelo = Flight.objects.filter(
                    route=tramo,
                    departure_time__date=fecha,
                    status="active"
                ).first()
                if vuelo:
                    vuelos.append(vuelo)
                else:
                    break

            if len(vuelos) == len(chain):
                rutas_validas.append([r.id for r in chain])

        if not rutas_validas:
            form.add_error(None, "No hay vuelos disponibles en esa fecha.")
            return self.form_invalid(form)
        print('route_chains',route_chains)
        print('rutas_validas',rutas_validas)
        self.request.session["route_chain_ids_list"] = rutas_validas
        self.request.session["search_date"] = str(fecha)
        self.request.session["passenger_count"] = form.cleaned_data['passengers']

        return redirect("choose_itinerary")



# Objeto que representa un itinerario posible
ItineraryOption = namedtuple("ItineraryOption", ["id", "route_summary", "duration", "total_price"])

# Vista para mostrar las opciones de itinerario posibles
class ChooseItineraryView(TemplateView):
    template_name = "choose_itinerary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_chains_ids = self.request.session.get("route_chain_ids_list", [])
        options = []
        rutas_completas = []

        for idx, chain_ids in enumerate(route_chains_ids, 1):
            duration = 0
            total_price = 0
            routes = Route.objects.filter(id__in=chain_ids).select_related("origin_airport", "destination_airport")
            if not routes:
                continue
            flight = Flight.objects.filter(route__in=chain_ids)
           
            rutas_completas.append(routes)  # Guardamos todas las rutas reales

            summary = " → ".join([r.origin_airport.code for r in routes] + [routes.last().destination_airport.code])
            
            duration = sum(r.duration for r in flight)
            total_price = sum(a.base_price for a in flight)
            options.append(ItineraryOption(idx, summary, duration, total_price))
         

        context["itineraries"] = options
        context["route_options"] = route_chains_ids
        context["rutas_completas"] = rutas_completas  # lo agregamos al contexto
        context["origin"] = options[0].route_summary.split(" → ")[0] if options else None
        context["destination"] = options[0].route_summary.split(" → ")[-1] if options else None
        context["date"] = self.request.session.get("search_date")
        context["passengers"] = self.request.session.get("passenger_count")
        return context


# Vista que se ejecuta cuando se selecciona el itinerario

class SelectItineraryView(View):    
    def get(self, request):
        # Redirigimos a la vista de elección de itinerario si se accede por GET
        return redirect("choose_itinerary")
    def post(self, request):
        option_idx = int(request.POST.get("option_idx", 0))

        print(option_idx)
        print(self.request.session["route_chain_ids_list"])
        select_route = self.request.session["route_chain_ids_list"]
        
        request.session["route_chain"] = select_route[option_idx]
        print(request.session["route_chain"])
        return redirect("load_passengers")  # Paso siguiente: cargar pasajeros
    
# Vista que permite al usuario seleccionar manualmente los asientos
class ChooseSeatView(View):
    template_name = "choose_seat.html"

    def get(self, request):
        passenger_ids = request.session.get("passenger_ids", [])
        route_ids = request.session.get("route_chain", [])
        print('pasajeros',passenger_ids)
        print('routes',route_ids)

        passengers = Passenger.objects.filter(id__in=passenger_ids)
        routes = Route.objects.filter(id__in=route_ids)
        flights = [Flight.objects.filter(route=route, status="active").first() for route in routes]
        print("passengers",passengers)
        print('routes',routes)
        print('flights',flights)
        seat_data = []

        for p_index, passenger in enumerate(passengers):
            print('p_index',p_index)
            for f_index, flight in enumerate(flights):
                print('f_index',f_index)
                # Detectar asientos ya asignados en este vuelo
                assigned_seat_ids = FlightSegment.objects.filter(
                    flight=flight,
                    seat__isnull=False
                ).values_list("seat_id", flat=True)

                available_seats = Seat.objects.filter(
                    airplane=flight.airplane
                ).exclude(id__in=assigned_seat_ids)

                key = f"{p_index}_{f_index}"
                seat_data.append({
                    "key": key,
                    "passenger": passenger,
                    "flight": flight,
                    "seats": available_seats
                })

        return render(request, self.template_name, {"seat_data": seat_data})

    def post(self, request):
        passenger_ids = request.session.get("passenger_ids", [])
        route_ids = request.session.get("route_chain_ids", [])

        passengers = Passenger.objects.filter(id__in=passenger_ids)
        routes = Route.objects.filter(id__in=route_ids)
        flights = [Flight.objects.filter(route=route, status="active").first() for route in routes]

        errores = []
        last_itinerary = None

        for p_index, passenger in enumerate(passengers):
            # Crear el itinerario por pasajero
            reservation_code = str(uuid.uuid4())[:8].upper()
            while Itinerary.objects.filter(reservation_code=reservation_code).exists():
                reservation_code = str(uuid.uuid4())[:8].upper()

            itinerary = ItineraryService.create(
                passenger=passenger,
                reservation_code=reservation_code
            )
            last_itinerary = itinerary

            for f_index, flight in enumerate(flights):
                key = f"{p_index}_{f_index}"
                seat_id = request.POST.get(f"seat_{key}")
                seat = Seat.objects.filter(id=seat_id).first() if seat_id else None

                if not seat:
                    errores.append(f"No se seleccionó asiento para {passenger.name} en vuelo {flight}")
                    continue

                # Verificamos que el asiento no esté ocupado
                if FlightSegment.objects.filter(seat=seat).exists():
                    errores.append(f"El asiento {seat.row}{seat.column} ya fue asignado")
                    continue

                FlightSegmentRepository.create(
                    itinerary=itinerary,
                    flight=flight,
                    seat=seat,
                    price=flight.base_price,
                    status="confirmed"
                )

        if errores:
            return render(request, "error.html", {"message": errores})

        return redirect("view_summary", itinerary_id=last_itinerary.id)



class GenerateItineraryView(View):
    def get(self, request):
        route_ids = request.session.get("route_chain_ids", [])
        passenger_ids = request.session.get("passenger_ids", [])

        passengers = Passenger.objects.filter(id__in=passenger_ids)
        routes = Route.objects.filter(id__in=route_ids).select_related("origin_airport", "destination_airport")

        last_itinerary = None
        for passenger in passengers:
            # Generar un código único (puede ser random, UUID, o incremental si preferís)
            reservation_code = str(uuid.uuid4())[:8].upper()

            # Asegurarse de que sea único (en caso de que haya colisiones)
            while Itinerary.objects.filter(reservation_code=reservation_code).exists():
                reservation_code = str(uuid.uuid4())[:8].upper()

            itinerary = ItineraryService.create(
                passenger=passenger,
                reservation_code=reservation_code
            )
            last_itinerary = itinerary

            for route in routes:
                flight = Flight.objects.filter(route=route, status="active").first()
                seat = Seat.objects.filter(airplane=flight.airplane).first()
                FlightSegmentRepository.create(
                    itinerary=itinerary,
                    flight=flight,
                    seat=seat,
                    price=flight.base_price,
                    status="confirmed"
                )

        return redirect("view_summary", itinerary_id=last_itinerary.id)




# Vista que genera un ticket (código de barras) asociado a un itinerario
class CreateTicketView(View):
    def get(self, request, itinerary_id):
        itinerary = get_object_or_404(Itinerary, id=itinerary_id)
        barcode = str(uuid.uuid4())[:10].upper()
        TicketRepository.create(itinerary=itinerary, barcode=barcode)
        return redirect('view_summary', itinerary_id=itinerary.id)

# Vista que muestra el resumen completo del itinerario reservado
class ViewSummary(TemplateView):
    template_name = "view_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        itinerary = get_object_or_404(Itinerary, id=self.kwargs["itinerary_id"])

        context["itinerary"] = itinerary
        context["passenger"] = itinerary.passenger
        context["segments"] = FlightSegmentService.list_by_itinerary(itinerary)
        context["ticket"] = TicketService.get_by_itinerary(itinerary)

        return context
