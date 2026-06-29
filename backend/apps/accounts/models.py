from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PASSENGER = "PASSENGER", "Passenger"
        DRIVER = "DRIVER", "Driver"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PASSENGER)
    phone_number = models.CharField(max_length=32, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    REQUIRED_FIELDS = ["email"]

    @property
    def is_driver(self) -> bool:
        return self.role == self.Role.DRIVER

