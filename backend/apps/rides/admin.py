from django.contrib import admin

from .models import DriverProfile, Ride, RideStatusEvent, Vehicle


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "license_number", "verified_at", "rating")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "driver", "brand", "model", "color", "seats")


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("id", "passenger", "driver", "status", "estimated_fare_cents", "requested_at")
    list_filter = ("status",)
    search_fields = ("pickup_label", "dropoff_label", "passenger__username", "driver__username")


@admin.register(RideStatusEvent)
class RideStatusEventAdmin(admin.ModelAdmin):
    list_display = ("ride", "status", "actor", "created_at")

