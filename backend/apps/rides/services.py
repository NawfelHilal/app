from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from .models import Ride, RideStatusEvent


@dataclass(frozen=True)
class FareQuote:
    distance_km: Decimal
    duration_minutes: int
    fare_cents: int
    commission_cents: int
    driver_earnings_cents: int


class FareCalculator:
    base_cents = 350
    per_km_cents = 145
    per_minute_cents = 35
    minimum_cents = 850
    commission_rate = Decimal("0.15")

    def quote(self, distance_km: Decimal, duration_minutes: int) -> FareQuote:
        raw_fare = self.base_cents + int(distance_km * self.per_km_cents) + duration_minutes * self.per_minute_cents
        fare_cents = max(raw_fare, self.minimum_cents)
        commission = Decimal(fare_cents) * self.commission_rate
        commission_cents = int(commission.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return FareQuote(
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            fare_cents=fare_cents,
            commission_cents=commission_cents,
            driver_earnings_cents=fare_cents - commission_cents,
        )


class RideLifecycle:
    def record(self, ride: Ride, status: str, actor) -> Ride:
        ride.status = status
        now = timezone.now()
        if status == Ride.Status.ACCEPTED:
            ride.accepted_at = now
            ride.driver = actor
        elif status == Ride.Status.IN_PROGRESS:
            ride.started_at = now
        elif status == Ride.Status.COMPLETED:
            ride.completed_at = now
            ride.final_fare_cents = ride.estimated_fare_cents
        elif status == Ride.Status.CANCELED:
            ride.canceled_at = now
        ride.save()
        RideStatusEvent.objects.create(ride=ride, status=status, actor=actor)
        if status == Ride.Status.COMPLETED:
            from apps.payments.services import PaymentCaptureService

            PaymentCaptureService().capture_ride(ride)
        from apps.notifications.services import RideNotificationService

        RideNotificationService().notify_status(ride, status, actor)
        return ride
