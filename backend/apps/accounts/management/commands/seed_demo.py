from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create demo passenger and driver accounts."

    def handle(self, *args, **options):
        User = get_user_model()
        demo_users = [
            {
                "username": "passenger",
                "email": "passenger@fleetpro.local",
                "role": User.Role.PASSENGER,
            },
            {
                "username": "driver",
                "email": "driver@fleetpro.local",
                "role": User.Role.DRIVER,
            },
        ]

        for payload in demo_users:
            user, created = User.objects.get_or_create(
                username=payload["username"],
                defaults={
                    "email": payload["email"],
                    "role": payload["role"],
                },
            )
            if created:
                user.set_password("password123")
                user.save(update_fields=["password"])
                self.stdout.write(self.style.SUCCESS(f"Created {user.username}"))
            else:
                self.stdout.write(f"{user.username} already exists")

