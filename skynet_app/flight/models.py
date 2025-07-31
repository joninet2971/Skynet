from django.db import models
from airplane.models import Airplane

class Airport(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)  # Ej: EZE, BRC, etc.
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Route(models.Model):
    origin_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    destination_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    estimated_duration = models.IntegerField(help_text="Duration in minutes")

    def __str__(self):
        return f"{self.origin_airport.code} ➝ {self.destination_airport.code} - {self.estimated_duration}"

class Flight(models.Model):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name='flights')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='flights')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Flight {self.id} - {self.route} "


