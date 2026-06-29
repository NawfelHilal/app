from django.conf import settings
import stripe

from apps.rides.models import Ride

from .models import Payment


class StripePaymentGateway:
    def create_payment_intent(self, ride: Ride) -> Payment:
        if not settings.STRIPE_SECRET_KEY:
            raise RuntimeError("STRIPE_SECRET_KEY is required to create payment intents.")

        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=ride.fare_cents,
            currency="eur",
            automatic_payment_methods={"enabled": True},
            metadata={
                "ride_id": str(ride.id),
                "passenger_id": str(ride.passenger_id),
                "commission_cents": str(ride.commission_cents),
            },
        )
        payment, _ = Payment.objects.update_or_create(
            ride=ride,
            defaults={
                "amount_cents": ride.fare_cents,
                "currency": "eur",
                "stripe_payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status.upper(),
            },
        )
        return payment


class SimulatedPaymentGateway:
    def authorize_ride(self, ride: Ride) -> Payment:
        payment, _ = Payment.objects.update_or_create(
            ride=ride,
            defaults={
                "amount_cents": ride.fare_cents,
                "currency": "eur",
                "stripe_payment_intent_id": f"pi_simulated_fleetpro_{ride.id}",
                "client_secret": f"pi_simulated_fleetpro_{ride.id}_secret_demo",
                "status": Payment.Status.REQUIRES_CONFIRMATION,
            },
        )
        return payment

    def capture_ride(self, ride: Ride) -> Payment | None:
        try:
            payment = ride.payment
        except Payment.DoesNotExist:
            return None

        payment.amount_cents = ride.fare_cents
        payment.status = Payment.Status.SUCCEEDED
        payment.save(update_fields=["amount_cents", "status", "updated_at"])
        return payment
