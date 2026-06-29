from django.conf import settings

from .models import DeviceToken


class PushNotificationGateway:
    def send_to_user(self, user, title: str, body: str, data: dict[str, str] | None = None) -> int:
        tokens = list(DeviceToken.objects.filter(user=user, enabled=True).values_list("token", flat=True))
        if not tokens:
            return 0
        if not settings.FIREBASE_CREDENTIALS_PATH:
            return 0

        import firebase_admin
        from firebase_admin import credentials, messaging

        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)

        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        response = messaging.send_each_for_multicast(message)
        return response.success_count


class RideNotificationService:
    messages = {
        "ACCEPTED": ("Chauffeur trouvé", "Votre chauffeur a accepté la course."),
        "IN_PROGRESS": ("Course démarrée", "Votre trajet vers la destination commence."),
        "COMPLETED": ("Course terminée", "Le trajet est terminé et le paiement a été traité."),
        "CANCELED": ("Course annulée", "La course a été annulée."),
    }

    def __init__(self, gateway: PushNotificationGateway | None = None):
        self.gateway = gateway or PushNotificationGateway()

    def notify_status(self, ride, status: str, actor) -> None:
        message = self.messages.get(status)
        if not message:
            return
        recipients = [ride.passenger]
        if ride.driver and ride.driver_id != actor.id:
            recipients.append(ride.driver)
        for recipient in recipients:
            if recipient.id == actor.id and status != "COMPLETED":
                continue
            self.gateway.send_to_user(
                recipient,
                message[0],
                message[1],
                {"ride_id": str(ride.id), "status": status},
            )
