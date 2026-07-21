from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.rides.models import Ride


def create_user(username: str, role: str | None = None):
    User = get_user_model()
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="password123",
    )
    if role:
        user.role = role
        user.save(update_fields=["role"])
    return user


def ride_payload(**overrides):
    payload = {
        "pickup_label": "Paris Centre",
        "pickup_latitude": "48.856600",
        "pickup_longitude": "2.352200",
        "dropoff_label": "Tour Eiffel",
        "dropoff_latitude": "48.858400",
        "dropoff_longitude": "2.294500",
        "distance_km": "10.00",
        "duration_minutes": 20,
        "passenger_note": "Test recette Bloc 2",
    }
    payload.update(overrides)
    return payload


def create_ride(passenger, driver=None, status=Ride.Status.REQUESTED, **overrides):
    payload = ride_payload(**overrides)
    return Ride.objects.create(
        passenger=passenger,
        driver=driver,
        status=status,
        pickup_label=payload["pickup_label"],
        pickup_latitude=Decimal(payload["pickup_latitude"]),
        pickup_longitude=Decimal(payload["pickup_longitude"]),
        dropoff_label=payload["dropoff_label"],
        dropoff_latitude=Decimal(payload["dropoff_latitude"]),
        dropoff_longitude=Decimal(payload["dropoff_longitude"]),
        passenger_note=payload["passenger_note"],
        distance_km=Decimal(payload["distance_km"]),
        duration_minutes=payload["duration_minutes"],
        estimated_fare_cents=2500,
    )
