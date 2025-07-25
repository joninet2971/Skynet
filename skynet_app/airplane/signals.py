from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Airplane, Seat

@receiver(post_save, sender=Airplane)
def create_seats_for_airplane(sender, instance, created, **kwargs):
    if created:
        for row in range(1, instance.rows + 1):
            for col_num in range(1, instance.columns + 1):
                column_letter = chr(64 + col_num)  # 1=A, 2=B, ..., 26=Z
                Seat.objects.create(
                    airplane=instance,
                    number=f"{row}{column_letter}",
                    row=row,
                    column=column_letter,
                    type="Economy",         # Podés ajustar según fila si querés
                    status="available"
                )
