from django.db import models

class Airplane(models.Model):
    model = models.CharField(max_length=100)
    rows = models.IntegerField()
    columns = models.IntegerField()
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.model} "


class Seat(models.Model):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name='seats')
    number = models.CharField(max_length=10)
    row = models.IntegerField()
    column = models.CharField(max_length=1)
    type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Seat {self.number} - Airplane {self.airplane.model}"
