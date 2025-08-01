# Generated by Django 5.2.4 on 2025-07-28 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flight", "0002_alter_flight_airplane"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flight",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("cancelled", "Cancelled"),
                    ("delayed", "Delayed"),
                ],
                max_length=20,
            ),
        ),
    ]
