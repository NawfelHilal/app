from types import SimpleNamespace
from django.test import SimpleTestCase

from apps.notifications.services import RideNotificationService


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
