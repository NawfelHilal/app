from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import DriverProfile, Ride, Vehicle
from .services import FareCalculator


class FareQuoteSerializer(serializers.Serializer):
    distance_km = serializers.DecimalField(max_digits=7, decimal_places=2)
    duration_minutes = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        quote = FareCalculator().quote(attrs["distance_km"], attrs["duration_minutes"])
        attrs["quote"] = quote
        return attrs


class FareQuoteResponseSerializer(serializers.Serializer):
    distance_km = serializers.DecimalField(max_digits=7, decimal_places=2)
    duration_minutes = serializers.IntegerField()
    fare_cents = serializers.IntegerField()
    commission_cents = serializers.IntegerField()
    driver_earnings_cents = serializers.IntegerField()


class RideSerializer(serializers.ModelSerializer):
    commission_cents = serializers.IntegerField(read_only=True)
    driver_earnings_cents = serializers.IntegerField(read_only=True)
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = [
            "id",
            "passenger",
            "driver",
            "status",
            "pickup_label",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_label",
            "dropoff_latitude",
            "dropoff_longitude",
            "passenger_note",
            "cancellation_reason",
            "distance_km",
            "duration_minutes",
            "estimated_fare_cents",
            "final_fare_cents",
            "commission_cents",
            "driver_earnings_cents",
            "payment_status",
            "cancellation_reason",
            "requested_at",
            "accepted_at",
            "started_at",
            "completed_at",
            "canceled_at",
        ]
        read_only_fields = [
            "id",
            "passenger",
            "driver",
            "status",
            "estimated_fare_cents",
            "final_fare_cents",
            "commission_cents",
            "driver_earnings_cents",
            "payment_status",
            "requested_at",
            "accepted_at",
            "started_at",
            "completed_at",
            "canceled_at",
        ]

    def get_payment_status(self, obj):
        try:
            return obj.payment.status
        except ObjectDoesNotExist:
            return None

    def create(self, validated_data):
        quote = FareCalculator().quote(
            Decimal(validated_data["distance_km"]),
            validated_data["duration_minutes"],
        )
        return Ride.objects.create(
            passenger=self.context["request"].user,
            estimated_fare_cents=quote.fare_cents,
            **validated_data,
        )


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ["id", "user", "license_number", "verified_at", "rating"]
        read_only_fields = ["id", "user", "verified_at", "rating"]


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "driver", "plate_number", "brand", "model", "color", "seats"]
        read_only_fields = ["id", "driver"]
