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

