from types import SimpleNamespace
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APITestCase

from apps.notifications.models import DeviceToken
from apps.notifications.services import PushNotificationGateway, RideNotificationService

from .factories import create_user


class FakeGateway:
    def __init__(self):
        self.sent = []

    def send_to_user(self, user, title, body, data):
        self.sent.append((user.id, title, data))
        return 1


class RideNotificationTests(SimpleTestCase):
    def test_acceptance_notifies_the_passenger(self):
        gateway = FakeGateway()
        passenger = SimpleNamespace(id=1)
        driver = SimpleNamespace(id=2)
        ride = SimpleNamespace(id=9, passenger=passenger, driver=driver, driver_id=2)

        RideNotificationService(gateway).notify_status(ride, "ACCEPTED", driver)

        self.assertEqual(gateway.sent, [(1, "Chauffeur trouvé", {"ride_id": "9", "status": "ACCEPTED"})])

    def test_completed_notifies_actor_passenger_and_driver(self):
        gateway = FakeGateway()
        passenger = SimpleNamespace(id=1)
        driver = SimpleNamespace(id=2)
        ride = SimpleNamespace(id=9, passenger=passenger, driver=driver, driver_id=2)

        RideNotificationService(gateway).notify_status(ride, "COMPLETED", passenger)

        self.assertEqual(
            gateway.sent,
            [
                (1, "Course terminée", {"ride_id": "9", "status": "COMPLETED"}),
                (2, "Course terminée", {"ride_id": "9", "status": "COMPLETED"}),
            ],
        )

    def test_unknown_status_and_gateway_errors_are_ignored(self):
        class BrokenGateway:
            def send_to_user(self, user, title, body, data):
                raise RuntimeError("firebase down")

        passenger = SimpleNamespace(id=1)
        ride = SimpleNamespace(id=9, passenger=passenger, driver=None, driver_id=None)

        RideNotificationService(BrokenGateway()).notify_status(ride, "UNKNOWN", passenger)
        RideNotificationService(BrokenGateway()).notify_status(ride, "CANCELED", SimpleNamespace(id=2))


class DeviceTokenApiTests(APITestCase):
    def test_device_token_create_update_and_list_are_scoped_to_user(self):
        user = create_user("device-owner")
        other = create_user("device-other")
        DeviceToken.objects.create(user=other, token="other-token", platform=DeviceToken.Platform.IOS)
        self.client.force_authenticate(user)

        created = self.client.post(
            "/api/v1/notifications/devices/",
            {"token": "expo-token", "platform": DeviceToken.Platform.IOS, "enabled": True},
            format="json",
        )
        updated = self.client.post(
            "/api/v1/notifications/devices/",
            {"token": "expo-token", "platform": DeviceToken.Platform.ANDROID, "enabled": False},
            format="json",
        )
        listed = self.client.get("/api/v1/notifications/devices/")

        self.assertEqual(created.status_code, 201)
        self.assertEqual(updated.status_code, 201)
        self.assertEqual(DeviceToken.objects.get(token="expo-token").platform, DeviceToken.Platform.ANDROID)
        self.assertEqual(len(listed.data), 1)
        self.assertEqual(listed.data[0]["token"], "expo-token")

    @override_settings(FIREBASE_CREDENTIALS_PATH="")
    def test_push_gateway_returns_zero_without_tokens_or_firebase_config(self):
        user = create_user("push-user")

        self.assertEqual(PushNotificationGateway().send_to_user(user, "Title", "Body"), 0)

        DeviceToken.objects.create(user=user, token="expo-token", platform=DeviceToken.Platform.IOS)

        self.assertEqual(PushNotificationGateway().send_to_user(user, "Title", "Body"), 0)
