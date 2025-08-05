from django.db import models

# Create your models here.

from django.db import models

class CarouselImage(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='carousel/')

    def __str__(self):
        return self.title if self.title else f"Imagen {self.id}"

