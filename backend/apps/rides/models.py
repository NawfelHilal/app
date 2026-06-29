from django.conf import settings
from django.db import models


class DriverProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_profile")
    license_number = models.CharField(max_length=64, unique=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5)

    def __str__(self) -> str:
        return f"DriverProfile({self.user_id})"


class Vehicle(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles")
    plate_number = models.CharField(max_length=32, unique=True)
    brand = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    color = models.CharField(max_length=32)
    seats = models.PositiveSmallIntegerField(default=4)

    def __str__(self) -> str:
        return f"{self.plate_number} - {self.brand} {self.model}"


class Ride(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        ACCEPTED = "ACCEPTED", "Accepted"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELED = "CANCELED", "Canceled"

    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="passenger_rides")
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="driver_rides",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.REQUESTED)
    pickup_label = models.CharField(max_length=255)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    dropoff_label = models.CharField(max_length=255)
    dropoff_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    dropoff_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    passenger_note = models.CharField(max_length=500, blank=True)
    cancellation_reason = models.CharField(max_length=255, blank=True)
    distance_km = models.DecimalField(max_digits=7, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    estimated_fare_cents = models.PositiveIntegerField()
    final_fare_cents = models.PositiveIntegerField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]

    @property
    def fare_cents(self) -> int:
        return self.final_fare_cents or self.estimated_fare_cents

    @property
    def commission_cents(self) -> int:
        return round(self.fare_cents * settings.FLEETPRO_COMMISSION_RATE)

    @property
    def driver_earnings_cents(self) -> int:
        return self.fare_cents - self.commission_cents


class RideStatusEvent(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=24, choices=Ride.Status.choices)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
