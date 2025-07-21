from django.db import models

class Airplane(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.IntegerField()
    rows = models.IntegerField()
    columns = models.IntegerField()

    def __str__(self):
        return f"{self.model} ({self.capacity} passengers)"

class Seat(models.Model): #Asiento
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name='seats')
    number = models.CharField(max_length=10)
    row = models.IntegerField()
    column = models.IntegerField()
    type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Seat {self.number} - Airplane {self.airplane.model}"
