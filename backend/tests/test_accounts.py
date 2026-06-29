from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class AccountApiTests(APITestCase):
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
