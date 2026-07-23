from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rides", "0003_driver_services_and_ride_service_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ride",
            name="service_type",
            field=models.CharField(
                choices=[
                    ("STANDARD", "Standard"),
                    ("FLEETHER", "FleetHer"),
                    ("FLEET_PMR", "Fleet PMR"),
                    ("FLEET_LUXE", "FleetLuxe"),
                ],
                default="STANDARD",
                max_length=24,
            ),
        ),
    ]
