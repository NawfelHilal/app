from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rides", "0002_ride_notes_and_cancellation"),
    ]

    operations = [
        migrations.AddField(
            model_name="driverprofile",
            name="company_name",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="driverprofile",
            name="gender",
            field=models.CharField(
                choices=[
                    ("FEMALE", "Female"),
                    ("MALE", "Male"),
                    ("OTHER", "Other"),
                    ("UNDISCLOSED", "Undisclosed"),
                ],
                default="UNDISCLOSED",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="driverprofile",
            name="insurance_policy_number",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="driverprofile",
            name="professional_card_number",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="driverprofile",
            name="siret_number",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="ride",
            name="service_type",
            field=models.CharField(
                choices=[
                    ("STANDARD", "Standard"),
                    ("FLEETHER", "FleetHer"),
                    ("FLEET_PMR", "Fleet PMR"),
                ],
                default="STANDARD",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="vehicle",
            name="is_pmr_adapted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="vehicle",
            name="pmr_certification_reference",
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
