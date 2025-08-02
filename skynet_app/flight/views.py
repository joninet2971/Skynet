from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import redirect
from .models import Airport, Route, Flight
from .forms import AirportForm, RouteForm, FlightForm
from .services.flight import AirportService, RouteService, FlightService


# --- AIRPORT VIEWS ---

class AirportList(ListView):
    model = Airport
    template_name = 'airports_list.html'
    context_object_name = 'airports'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return AirportService.get_all()


class AirportCreate(CreateView):
    model = Airport
    form_class = AirportForm
    template_name = 'airport_form.html'
    success_url = reverse_lazy('airport_list')


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            AirportService.create(form.cleaned_data)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        messages.success(self.request, "Aeropuerto creado correctamente.")
        return redirect(self.success_url)


class AirportUpdate(UpdateView):
    model = Airport
    form_class = AirportForm
    template_name = 'airport_form.html'
    success_url = reverse_lazy('airport_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            airport = self.get_object()
            AirportService.update(airport, **form.cleaned_data)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        messages.success(self.request, "Aeropuerto actualizado correctamente.")
        return redirect(self.success_url)


class AirportDelete(DeleteView):
    model = Airport
    template_name = 'airport_confirm_delete.html'
    success_url = reverse_lazy('airport_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Aeropuerto eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


# --- ROUTE VIEWS ---

class RouteList(ListView):
    model = Route
    template_name = 'routes_list.html'
    context_object_name = 'routes'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return RouteService.get_all()


class RouteCreate(CreateView):
    model = Route
    form_class = RouteForm
    template_name = 'route_form.html'
    success_url = reverse_lazy('route_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            RouteService.create(form.cleaned_data)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        messages.success(self.request, "Ruta creada correctamente.")
        return redirect(self.success_url)


class RouteUpdate(UpdateView):
    model = Route
    form_class = RouteForm
    template_name = 'route_form.html'
    success_url = reverse_lazy('route_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            route = self.get_object()
            RouteService.update(route, **form.cleaned_data)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        messages.success(self.request, "Ruta actualizada correctamente.")
        return redirect(self.success_url)


class RouteDelete(DeleteView):
    model = Route
    template_name = 'route_confirm_delete.html'
    success_url = reverse_lazy('routes_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Ruta eliminada correctamente.")
        return super().delete(request, *args, **kwargs)


# --- FLIGHT VIEWS ---

class FlightList(ListView):
    model = Flight
    template_name = 'flights_list.html'
    context_object_name = 'flights'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return FlightService.get_all()


class FlightCreate(CreateView):
    model = Flight
    form_class = FlightForm
    template_name = 'flight_form.html'
    success_url = reverse_lazy('flight_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            FlightService.create(form.cleaned_data)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        messages.success(self.request, "Vuelo creado correctamente.")
        return redirect(self.success_url)


class FlightUpdate(UpdateView):
    model = Flight
    form_class = FlightForm
    template_name = 'flight_form.html'
    success_url = reverse_lazy('flight_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            flight = self.get_object()
            FlightService.update(flight, **form.cleaned_data)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        messages.success(self.request, "Vuelo actualizado correctamente.")
        return redirect(self.success_url)


class FlightDelete(DeleteView):
    model = Flight
    template_name = 'flight_confirm_delete.html'
    success_url = reverse_lazy('flight_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Solo para administradores.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Vuelo eliminado correctamente.")
        return super().delete(request, *args, **kwargs)
