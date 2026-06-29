from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("payments", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[
                    ("REQUIRES_PAYMENT_METHOD", "Requires payment method"),
                    ("REQUIRES_CONFIRMATION", "Requires confirmation"),
                    ("REQUIRES_ACTION", "Requires action"),
                    ("REQUIRES_CAPTURE", "Requires capture"),
                    ("PROCESSING", "Processing"),
                    ("SUCCEEDED", "Succeeded"),
                    ("CANCELED", "Canceled"),
                    ("FAILED", "Failed"),
                ],
                default="REQUIRES_PAYMENT_METHOD",
                max_length=32,
            ),
        )
    ]
