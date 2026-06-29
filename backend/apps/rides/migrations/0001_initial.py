import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DriverProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("license_number", models.CharField(max_length=64, unique=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("rating", models.DecimalField(decimal_places=2, default=5, max_digits=3)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="driver_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ride",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("REQUESTED", "Requested"),
                            ("ACCEPTED", "Accepted"),
                            ("IN_PROGRESS", "In progress"),
                            ("COMPLETED", "Completed"),
                            ("CANCELED", "Canceled"),
                        ],
                        default="REQUESTED",
                        max_length=24,
                    ),
                ),
                ("pickup_label", models.CharField(max_length=255)),
                ("pickup_latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("pickup_longitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("dropoff_label", models.CharField(max_length=255)),
                ("dropoff_latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("dropoff_longitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("distance_km", models.DecimalField(decimal_places=2, max_digits=7)),
                ("duration_minutes", models.PositiveIntegerField()),
                ("estimated_fare_cents", models.PositiveIntegerField()),
                ("final_fare_cents", models.PositiveIntegerField(blank=True, null=True)),
                ("requested_at", models.DateTimeField(auto_now_add=True)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("canceled_at", models.DateTimeField(blank=True, null=True)),
                (
                    "driver",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="driver_rides",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "passenger",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="passenger_rides",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-requested_at"]},
        ),
        migrations.CreateModel(
            name="RideStatusEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("REQUESTED", "Requested"),
                            ("ACCEPTED", "Accepted"),
                            ("IN_PROGRESS", "In progress"),
                            ("COMPLETED", "Completed"),
                            ("CANCELED", "Canceled"),
                        ],
                        max_length=24,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "ride",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="rides.ride",
                    ),
                ),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("plate_number", models.CharField(max_length=32, unique=True)),
                ("brand", models.CharField(max_length=64)),
                ("model", models.CharField(max_length=64)),
                ("color", models.CharField(max_length=32)),
                ("seats", models.PositiveSmallIntegerField(default=4)),
                (
                    "driver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vehicles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

