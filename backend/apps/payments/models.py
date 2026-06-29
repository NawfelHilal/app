from django.db import models

from apps.rides.models import Ride


class Payment(models.Model):
    class Status(models.TextChoices):
        REQUIRES_PAYMENT_METHOD = "REQUIRES_PAYMENT_METHOD", "Requires payment method"
        REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION", "Requires confirmation"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED = "FAILED", "Failed"

    ride = models.OneToOneField(Ride, on_delete=models.PROTECT, related_name="payment")
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="eur")
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    client_secret = models.CharField(max_length=255)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUIRES_PAYMENT_METHOD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

