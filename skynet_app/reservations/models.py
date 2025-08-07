from django.db import models
from django.core.exceptions import ValidationError
from airplane.models import Seat
from flight.models import Flight
from django.utils import timezone
from datetime import timedelta

class Passenger(models.Model):
    STATUS_CHOICES = [
        ('dni', 'DNI'),
        ('passport', 'Pasaporte'),
    ]

    name = models.CharField(max_length=100)
    document = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    document_type = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.document})"
  
class Itinerary(models.Model): #Este vendria a ser reservation pero para varios vuelos en el caso de tener escalas
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='itineraries')
    reservation_code = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Itinerary {self.reservation_code} - {self.passenger.name}"
    
class FlightSegment(models.Model):#Esta es la tabla intermedia de la que hablamos, donde cargamos varios vuelos a la misma reserva o intinerario
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='segments')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reserved_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.seat and self.flight:
            conflict = FlightSegment.objects.filter(
                seat=self.seat,
                flight=self.flight
            ).exclude(id=self.id)

            if conflict.exists():
                raise ValidationError("Este asiento ya está asignado en este vuelo.")

    def save(self, *args, **kwargs):
        self.clean()
        # Si está reservado, actualizá la marca de tiempo
        if self.status == "reserved" and not self.reserved_at:
            self.reserved_at = timezone.now()
        super().save(*args, **kwargs)
        self.itinerary.total_price = sum(seg.price for seg in self.itinerary.segments.all())
        self.itinerary.save()

    def __str__(self):
        return f"Segment: {self.flight} - Itinerary {self.itinerary.reservation_code}"

class Ticket(models.Model):
    itinerary = models.OneToOneField(Itinerary, on_delete=models.CASCADE, related_name='ticket')
    barcode = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Ticket {self.barcode} - Itinerary {self.itinerary.reservation_code}"

