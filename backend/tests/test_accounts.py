from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APITestCase

from apps.accounts.tokens import FleetProTokenObtainPairSerializer

from .factories import create_user


class AccountApiTests(APITestCase):
    def test_public_registration_creates_passenger(self):
        response = self.client.post(
            "/api/v1/accounts/",
            {
                "username": "new-passenger",
                "email": "new-passenger@example.com",
                "password": "strong-pass-123",
                "role": "PASSENGER",
                "phone_number": "+33123456789",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(username="new-passenger")
        self.assertEqual(user.role, get_user_model().Role.PASSENGER)
        self.assertTrue(user.check_password("strong-pass-123"))

    def test_public_registration_rejects_admin_role(self):
        response = self.client.post(
            "/api/v1/accounts/",
            {"username": "admin-user", "email": "admin@example.com", "password": "strong-pass-123", "role": "ADMIN"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.filter(username="admin-user").exists())

    def test_profile_cannot_change_role(self):
        user = get_user_model().objects.create_user(
            username="passenger-test",
            email="passenger-test@example.com",
            password="strong-pass-123",
        )
        self.client.force_authenticate(user)

        response = self.client.patch("/api/v1/accounts/me/", {"role": "ADMIN", "first_name": "Nora"}, format="json")

        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.role, get_user_model().Role.PASSENGER)
        self.assertEqual(user.first_name, "Nora")

    def test_profile_get_returns_current_user(self):
        user = create_user("me-passenger")
        self.client.force_authenticate(user)

        response = self.client.get("/api/v1/accounts/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "me-passenger")

    def test_change_password_validates_current_password(self):
        user = create_user("password-user")
        self.client.force_authenticate(user)

        bad_response = self.client.post(
            "/api/v1/accounts/change-password/",
            {"current_password": "wrong-password", "new_password": "new-password-123"},
            format="json",
        )
        ok_response = self.client.post(
            "/api/v1/accounts/change-password/",
            {"current_password": "password123", "new_password": "new-password-123"},
            format="json",
        )

        user.refresh_from_db()
        self.assertEqual(bad_response.status_code, 400)
        self.assertEqual(ok_response.status_code, 204)
        self.assertTrue(user.check_password("new-password-123"))

    def test_token_contains_fleetpro_claims(self):
        user = create_user("token-driver", role=get_user_model().Role.DRIVER)

        token = FleetProTokenObtainPairSerializer.get_token(user)

        self.assertEqual(token["role"], get_user_model().Role.DRIVER)
        self.assertEqual(token["email"], "token-driver@example.com")
        self.assertEqual(token["username"], "token-driver")

    def test_seed_demo_creates_and_resets_demo_accounts(self):
        call_command("seed_demo")
        call_command("seed_demo")

        User = get_user_model()
        passenger = User.objects.get(username="passenger")
        driver = User.objects.get(username="driver")
        self.assertEqual(passenger.role, User.Role.PASSENGER)
        self.assertEqual(driver.role, User.Role.DRIVER)
        self.assertTrue(passenger.check_password("password123"))
        self.assertTrue(driver.check_password("password123"))
