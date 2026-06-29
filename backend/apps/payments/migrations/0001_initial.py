import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("rides", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount_cents", models.PositiveIntegerField()),
                ("currency", models.CharField(default="eur", max_length=3)),
                ("stripe_payment_intent_id", models.CharField(max_length=255, unique=True)),
                ("client_secret", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("REQUIRES_PAYMENT_METHOD", "Requires payment method"),
                            ("REQUIRES_CONFIRMATION", "Requires confirmation"),
                            ("SUCCEEDED", "Succeeded"),
                            ("FAILED", "Failed"),
                        ],
                        default="REQUIRES_PAYMENT_METHOD",
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "ride",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment",
                        to="rides.ride",
                    ),
                ),
            ],
        ),
    ]

