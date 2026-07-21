from types import SimpleNamespace
from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase
import stripe

from apps.payments.models import Payment
from apps.payments.services import PaymentCaptureService, SimulatedPaymentGateway, StripePaymentGateway
from apps.rides.models import Ride

from .factories import create_ride, create_user


class PaymentTests(APITestCase):
    def test_stripe_gateway_requires_secret_key(self):
        passenger = create_user("stripe-no-secret")
        ride = create_ride(passenger)

        with self.assertRaisesMessage(RuntimeError, "STRIPE_SECRET_KEY is required"):
            StripePaymentGateway().create_payment_intent(ride)

    @override_settings(STRIPE_SECRET_KEY="sk_test_123")
    @patch("apps.payments.services.stripe.PaymentIntent.create")
    def test_stripe_gateway_creates_payment_intent_and_reuses_existing(self, create_intent):
        create_intent.return_value = SimpleNamespace(id="pi_123", client_secret="secret_123", status="requires_capture")
        passenger = create_user("stripe-passenger")
        ride = create_ride(passenger)

        payment = StripePaymentGateway().create_payment_intent(ride)
        reused = StripePaymentGateway().create_payment_intent(ride)

        self.assertEqual(payment.stripe_payment_intent_id, "pi_123")
        self.assertEqual(payment.status, Payment.Status.REQUIRES_CAPTURE)
        self.assertEqual(reused.id, payment.id)
        create_intent.assert_called_once()

    @override_settings(STRIPE_SECRET_KEY="sk_test_123")
    @patch("apps.payments.services.stripe.PaymentIntent.capture")
    def test_capture_stripe_payment_success_and_failure(self, capture):
        passenger = create_user("capture-passenger")
        ride = create_ride(passenger)
        payment = Payment.objects.create(
            ride=ride,
            amount_cents=ride.fare_cents,
            stripe_payment_intent_id="pi_real_123",
            client_secret="secret",
            status=Payment.Status.REQUIRES_CAPTURE,
        )
        capture.return_value = SimpleNamespace(status="succeeded")

        captured = PaymentCaptureService().capture_ride(ride)

        self.assertEqual(captured.status, Payment.Status.SUCCEEDED)

        payment.status = Payment.Status.REQUIRES_CAPTURE
        payment.save(update_fields=["status"])
        capture.side_effect = stripe.StripeError("boom")

        failed = PaymentCaptureService().capture_ride(ride)

        self.assertEqual(failed.status, Payment.Status.FAILED)

    def test_capture_returns_none_without_payment_and_reuses_succeeded(self):
        passenger = create_user("capture-none")
        no_payment_ride = create_ride(passenger)

        self.assertIsNone(PaymentCaptureService().capture_ride(no_payment_ride))

        paid_ride = create_ride(passenger, passenger_note="paid")
        payment = Payment.objects.create(
            ride=paid_ride,
            amount_cents=paid_ride.fare_cents,
            stripe_payment_intent_id="pi_real_succeeded",
            client_secret="secret",
            status=Payment.Status.SUCCEEDED,
        )

        self.assertEqual(PaymentCaptureService().capture_ride(paid_ride).id, payment.id)

    def test_simulated_payment_authorize_and_capture_updates_status(self):
        passenger = create_user("pay-passenger")
        ride = create_ride(passenger)

        payment = SimulatedPaymentGateway().authorize_ride(ride)

        self.assertEqual(payment.status, Payment.Status.REQUIRES_CONFIRMATION)
        self.assertTrue(payment.stripe_payment_intent_id.startswith("pi_simulated_"))

        captured = PaymentCaptureService().capture_ride(ride)

        self.assertIsNotNone(captured)
        self.assertEqual(captured.status, Payment.Status.SUCCEEDED)
        self.assertEqual(captured.amount_cents, ride.fare_cents)

    @override_settings(ENABLE_DEMO_SIMULATION=False)
    def test_simulate_intent_is_hidden_when_demo_mode_disabled(self):
        passenger = create_user("disabled-demo-passenger")
        ride = create_ride(passenger)
        self.client.force_authenticate(passenger)

        response = self.client.post("/api/v1/payments/simulate-intent/", {"ride_id": ride.id}, format="json")

        self.assertEqual(response.status_code, 404)

    @override_settings(ENABLE_DEMO_SIMULATION=True)
    def test_simulate_intent_creates_payment_for_owner(self):
        passenger = create_user("simulate-owner")
        ride = create_ride(passenger)
        self.client.force_authenticate(passenger)

        response = self.client.post("/api/v1/payments/simulate-intent/", {"ride_id": ride.id}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], Payment.Status.REQUIRES_CONFIRMATION)

    @override_settings(ENABLE_DEMO_SIMULATION=True)
    def test_passenger_cannot_prepare_payment_for_another_passenger_ride(self):
        owner = create_user("payment-owner")
        attacker = create_user("payment-attacker")
        ride = create_ride(owner)
        self.client.force_authenticate(attacker)

        response = self.client.post("/api/v1/payments/simulate-intent/", {"ride_id": ride.id}, format="json")

        self.assertEqual(response.status_code, 404)

    @override_settings(STRIPE_SECRET_KEY="sk_test_123")
    @patch("apps.payments.views.StripePaymentGateway.create_payment_intent")
    def test_create_intent_success_and_conflict(self, create_intent):
        passenger = create_user("intent-owner")
        requested_ride = create_ride(passenger)
        accepted_ride = create_ride(passenger, status=Ride.Status.ACCEPTED)
        payment = Payment.objects.create(
            ride=requested_ride,
            amount_cents=requested_ride.fare_cents,
            stripe_payment_intent_id="pi_intent",
            client_secret="secret",
            status=Payment.Status.REQUIRES_CAPTURE,
        )
        create_intent.return_value = payment
        self.client.force_authenticate(passenger)

        created = self.client.post("/api/v1/payments/create-intent/", {"ride_id": requested_ride.id}, format="json")
        conflict = self.client.post("/api/v1/payments/create-intent/", {"ride_id": accepted_ride.id}, format="json")

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["client_secret"], "secret")
        self.assertIn("ride", created.data["payment"]["_links"])
        self.assertEqual(conflict.status_code, 409)

    def test_payment_list_is_scoped_to_passenger_and_staff_sees_all(self):
        passenger = create_user("payment-list-owner")
        other = create_user("payment-list-other")
        staff = create_user("payment-list-staff")
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])
        owner_ride = create_ride(passenger)
        other_ride = create_ride(other)
        Payment.objects.create(
            ride=owner_ride,
            amount_cents=owner_ride.fare_cents,
            stripe_payment_intent_id="pi_owner",
            client_secret="secret",
            status=Payment.Status.SUCCEEDED,
        )
        Payment.objects.create(
            ride=other_ride,
            amount_cents=other_ride.fare_cents,
            stripe_payment_intent_id="pi_other",
            client_secret="secret",
            status=Payment.Status.SUCCEEDED,
        )

        self.client.force_authenticate(passenger)
        passenger_response = self.client.get("/api/v1/payments/")
        self.client.force_authenticate(staff)
        staff_response = self.client.get("/api/v1/payments/")

        self.assertEqual(len(passenger_response.data), 1)
        self.assertEqual(len(staff_response.data), 2)

    def test_webhook_handles_unconfigured_invalid_and_success_events(self):
        passenger = create_user("webhook-owner")
        ride = create_ride(passenger)
        payment = Payment.objects.create(
            ride=ride,
            amount_cents=ride.fare_cents,
            stripe_payment_intent_id="pi_webhook",
            client_secret="secret",
            status=Payment.Status.PROCESSING,
        )

        unconfigured = self.client.post("/api/v1/payments/webhook/", b"{}", content_type="application/json")

        with override_settings(STRIPE_WEBHOOK_SECRET="whsec_test"):
            with patch("apps.payments.views.stripe.Webhook.construct_event", side_effect=ValueError):
                invalid = self.client.post(
                    "/api/v1/payments/webhook/",
                    b"{}",
                    content_type="application/json",
                    HTTP_STRIPE_SIGNATURE="bad",
                )
            with patch(
                "apps.payments.views.stripe.Webhook.construct_event",
                return_value={
                    "type": "payment_intent.succeeded",
                    "data": {"object": {"id": "pi_webhook", "status": "succeeded"}},
                },
            ):
                success = self.client.post(
                    "/api/v1/payments/webhook/",
                    b"{}",
                    content_type="application/json",
                    HTTP_STRIPE_SIGNATURE="good",
                )

        payment.refresh_from_db()
        self.assertEqual(unconfigured.status_code, 503)
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(success.status_code, 200)
        self.assertEqual(payment.status, Payment.Status.SUCCEEDED)
