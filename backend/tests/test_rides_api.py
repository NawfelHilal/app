import json
from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase

from apps.rides.models import DriverProfile, Ride, RideStatusEvent, Vehicle

from .factories import create_ride, create_user, ride_payload


class RideApiTests(APITestCase):
    def test_health_endpoint_checks_database(self):
        response = self.client.get("/api/v1/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "ok", "service": "fleetpro-core"})

    def test_quote_endpoint_returns_server_side_fare(self):
        passenger = create_user("quote-passenger")
        self.client.force_authenticate(passenger)

        response = self.client.post("/api/v1/rides/quote/", {"distance_km": "10.00", "duration_minutes": 20}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["fare_cents"], 2500)
        self.assertEqual(response.data["commission_cents"], 375)

    def test_passenger_creates_ride_with_server_side_fare(self):
        passenger = create_user("ride-passenger")
        self.client.force_authenticate(passenger)

        response = self.client.post("/api/v1/rides/", ride_payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], Ride.Status.REQUESTED)
        self.assertEqual(response.data["estimated_fare_cents"], 2500)
        self.assertEqual(response.data["commission_cents"], 375)
        self.assertEqual(response.data["driver_earnings_cents"], 2125)
        self.assertIn("self", response.data["_links"])
        self.assertIn("cancel", response.data["_links"])
        self.assertIn("payment_intent", response.data["_links"])

    def test_driver_cannot_request_ride(self):
        driver = create_user("driver-cannot-create", role="DRIVER")
        self.client.force_authenticate(driver)

        response = self.client.post("/api/v1/rides/", ride_payload(), format="json")

        self.assertEqual(response.status_code, 403)

    def test_list_is_scoped_by_role(self):
        passenger = create_user("list-passenger")
        other = create_user("list-other")
        staff = create_user("list-staff")
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])
        driver = create_user("list-driver", role="DRIVER")
        own_ride = create_ride(passenger)
        create_ride(other)

        self.client.force_authenticate(passenger)
        passenger_response = self.client.get("/api/v1/rides/")
        self.client.force_authenticate(staff)
        staff_response = self.client.get("/api/v1/rides/")
        self.client.force_authenticate(driver)
        with patch("apps.rides.views.RideMatcher.nearby_ride_ids", return_value=[own_ride.id]):
            driver_response = self.client.get("/api/v1/rides/")

        self.assertEqual(len(passenger_response.data), 1)
        self.assertEqual(len(staff_response.data), 2)
        self.assertEqual(len(driver_response.data), 1)

    def test_driver_accepts_nearby_ride_and_conflict_on_closed_ride(self):
        passenger = create_user("accept-passenger")
        driver = create_user("accept-driver", role="DRIVER")
        ride = create_ride(passenger)
        closed_ride = create_ride(passenger, status=Ride.Status.CANCELED)
        self.client.force_authenticate(driver)

        with patch("apps.rides.views.RideMatcher.nearby_ride_ids", return_value=[ride.id, closed_ride.id]):
            accepted = self.client.post(f"/api/v1/rides/{ride.id}/accept/", {}, format="json")
            conflict = self.client.post(f"/api/v1/rides/{closed_ride.id}/accept/", {}, format="json")

        ride.refresh_from_db()
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(ride.driver_id, driver.id)
        self.assertEqual(ride.status, Ride.Status.ACCEPTED)
        self.assertIn("start", accepted.data["_links"])
        self.assertEqual(conflict.status_code, 404)

    def test_fleether_and_pmr_rides_are_visible_only_to_eligible_drivers(self):
        passenger = create_user("service-passenger")
        female_driver = create_user("female-driver", role="DRIVER")
        male_driver = create_user("male-driver", role="DRIVER")
        pmr_driver = create_user("pmr-driver", role="DRIVER")
        DriverProfile.objects.create(
            user=female_driver,
            license_number="FEMALE-LICENSE",
            gender=DriverProfile.Gender.FEMALE,
        )
        DriverProfile.objects.create(
            user=male_driver,
            license_number="MALE-LICENSE",
            gender=DriverProfile.Gender.MALE,
        )
        DriverProfile.objects.create(
            user=pmr_driver,
            license_number="PMR-LICENSE",
            gender=DriverProfile.Gender.MALE,
        )
        Vehicle.objects.create(
            driver=pmr_driver,
            plate_number="PMR-1",
            brand="Peugeot",
            model="Rifter",
            color="Blue",
            is_pmr_adapted=True,
            pmr_certification_reference="PMR-CERT",
        )
        fleether_ride = create_ride(passenger, service_type=Ride.ServiceType.FLEETHER)
        pmr_ride = create_ride(passenger, service_type=Ride.ServiceType.FLEET_PMR)

        with patch("apps.rides.views.RideMatcher.nearby_ride_ids", return_value=[fleether_ride.id, pmr_ride.id]):
            self.client.force_authenticate(female_driver)
            female_response = self.client.get("/api/v1/rides/")
            self.client.force_authenticate(male_driver)
            male_response = self.client.get("/api/v1/rides/")
            self.client.force_authenticate(pmr_driver)
            pmr_response = self.client.get("/api/v1/rides/")

        self.assertEqual([ride["id"] for ride in female_response.data], [fleether_ride.id])
        self.assertEqual(male_response.data, [])
        self.assertEqual([ride["id"] for ride in pmr_response.data], [pmr_ride.id])

    def test_ineligible_driver_cannot_accept_special_service(self):
        passenger = create_user("special-passenger")
        driver = create_user("special-driver", role="DRIVER")
        DriverProfile.objects.create(user=driver, license_number="SPECIAL-LICENSE", gender=DriverProfile.Gender.MALE)
        ride = create_ride(passenger, service_type=Ride.ServiceType.FLEETHER)
        self.client.force_authenticate(driver)

        with patch("apps.rides.views.RideMatcher.nearby_ride_ids", return_value=[ride.id]):
            response = self.client.post(f"/api/v1/rides/{ride.id}/accept/", {}, format="json")

        self.assertEqual(response.status_code, 404)

    def test_passenger_cannot_accept_ride(self):
        passenger = create_user("accept-not-driver")
        ride = create_ride(passenger)
        self.client.force_authenticate(passenger)

        response = self.client.post(f"/api/v1/rides/{ride.id}/accept/", {}, format="json")

        self.assertEqual(response.status_code, 403)

    def test_start_and_complete_validate_assigned_driver_and_status(self):
        passenger = create_user("lifecycle-passenger")
        driver = create_user("lifecycle-driver", role="DRIVER")
        other_driver = create_user("lifecycle-other-driver", role="DRIVER")
        accepted_ride = create_ride(passenger, driver=driver, status=Ride.Status.ACCEPTED)
        requested_ride = create_ride(passenger, driver=driver, status=Ride.Status.REQUESTED)
        in_progress_ride = create_ride(passenger, driver=driver, status=Ride.Status.IN_PROGRESS)

        self.client.force_authenticate(other_driver)
        forbidden_start = self.client.post(f"/api/v1/rides/{accepted_ride.id}/start/", {}, format="json")
        self.client.force_authenticate(driver)
        conflict_start = self.client.post(f"/api/v1/rides/{requested_ride.id}/start/", {}, format="json")
        started = self.client.post(f"/api/v1/rides/{accepted_ride.id}/start/", {}, format="json")
        conflict_complete = self.client.post(f"/api/v1/rides/{requested_ride.id}/complete/", {}, format="json")
        completed = self.client.post(f"/api/v1/rides/{in_progress_ride.id}/complete/", {}, format="json")
        self.client.force_authenticate(other_driver)
        forbidden_complete = self.client.post(f"/api/v1/rides/{in_progress_ride.id}/complete/", {}, format="json")

        self.assertEqual(forbidden_start.status_code, 404)
        self.assertEqual(conflict_start.status_code, 409)
        self.assertEqual(started.status_code, 200)
        self.assertEqual(started.data["status"], Ride.Status.IN_PROGRESS)
        self.assertEqual(conflict_complete.status_code, 409)
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.data["status"], Ride.Status.COMPLETED)
        self.assertNotIn("complete", completed.data["_links"])
        self.assertEqual(forbidden_complete.status_code, 404)

    def test_passenger_cancel_persists_reason_and_event(self):
        passenger = create_user("cancel-passenger")
        ride = create_ride(passenger)
        self.client.force_authenticate(passenger)

        response = self.client.post(f"/api/v1/rides/{ride.id}/cancel/", {"reason": "Erreur adresse"}, format="json")

        ride.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ride.status, Ride.Status.CANCELED)
        self.assertEqual(ride.cancellation_reason, "Erreur adresse")
        self.assertTrue(RideStatusEvent.objects.filter(ride=ride, status=Ride.Status.CANCELED).exists())

    def test_cancel_rejects_unrelated_user_and_closed_ride(self):
        passenger = create_user("cancel-owner")
        stranger = create_user("cancel-stranger")
        open_ride = create_ride(passenger)
        closed_ride = create_ride(passenger, status=Ride.Status.COMPLETED)

        self.client.force_authenticate(stranger)
        forbidden = self.client.post(f"/api/v1/rides/{open_ride.id}/cancel/", {}, format="json")
        self.client.force_authenticate(passenger)
        conflict = self.client.post(f"/api/v1/rides/{closed_ride.id}/cancel/", {}, format="json")

        self.assertEqual(forbidden.status_code, 404)
        self.assertEqual(conflict.status_code, 409)

    @override_settings(ENABLE_DEMO_SIMULATION=True)
    def test_demo_simulation_advances_ride_to_completed(self):
        passenger = create_user("demo-passenger")
        create_user("driver", role="DRIVER")
        ride = create_ride(passenger)
        self.client.force_authenticate(passenger)

        accepted = self.client.post(f"/api/v1/rides/{ride.id}/simulate/", {}, format="json")
        in_progress = self.client.post(f"/api/v1/rides/{ride.id}/simulate/", {}, format="json")
        completed = self.client.post(f"/api/v1/rides/{ride.id}/simulate/", {}, format="json")

        self.assertEqual(accepted.data["status"], Ride.Status.ACCEPTED)
        self.assertEqual(in_progress.data["status"], Ride.Status.IN_PROGRESS)
        self.assertEqual(completed.data["status"], Ride.Status.COMPLETED)
        self.assertEqual(RideStatusEvent.objects.filter(ride=ride).count(), 3)

    @override_settings(ENABLE_DEMO_SIMULATION=False)
    def test_demo_simulation_can_be_disabled(self):
        passenger = create_user("demo-disabled")
        ride = create_ride(passenger)
        self.client.force_authenticate(passenger)

        response = self.client.post(f"/api/v1/rides/{ride.id}/simulate/", {}, format="json")

        self.assertEqual(response.status_code, 404)

    @override_settings(ENABLE_DEMO_SIMULATION=True)
    def test_demo_simulation_rejects_non_owner_missing_driver_and_closed_ride(self):
        passenger = create_user("demo-owner")
        stranger = create_user("demo-stranger")
        open_ride = create_ride(passenger)
        closed_ride = create_ride(passenger, status=Ride.Status.CANCELED)

        self.client.force_authenticate(stranger)
        forbidden = self.client.post(f"/api/v1/rides/{open_ride.id}/simulate/", {}, format="json")
        self.client.force_authenticate(passenger)
        missing_driver = self.client.post(f"/api/v1/rides/{open_ride.id}/simulate/", {}, format="json")
        closed = self.client.post(f"/api/v1/rides/{closed_ride.id}/simulate/", {}, format="json")

        self.assertEqual(forbidden.status_code, 404)
        self.assertEqual(missing_driver.status_code, 409)
        self.assertEqual(closed.status_code, 200)
        self.assertEqual(closed.data["status"], Ride.Status.CANCELED)


class DriverProfileAndVehicleApiTests(APITestCase):
    def test_non_driver_cannot_manage_driver_resources(self):
        passenger = create_user("profile-passenger")
        self.client.force_authenticate(passenger)

        profile_response = self.client.get("/api/v1/driver-profiles/")
        vehicle_response = self.client.get("/api/v1/vehicles/")

        self.assertEqual(profile_response.status_code, 403)
        self.assertEqual(vehicle_response.status_code, 403)

    def test_driver_profile_and_vehicle_are_scoped_to_driver(self):
        driver = create_user("profile-driver", role="DRIVER")
        other_driver = create_user("profile-other-driver", role="DRIVER")
        staff = create_user("profile-staff")
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])
        DriverProfile.objects.create(user=other_driver, license_number="OTHER-LICENSE")
        Vehicle.objects.create(driver=other_driver, plate_number="OTHER-1", brand="Tesla", model="Y", color="Black")
        self.client.force_authenticate(driver)

        profile_created = self.client.post("/api/v1/driver-profiles/", {"license_number": "DRIVER-LICENSE"}, format="json")
        vehicle_created = self.client.post(
            "/api/v1/vehicles/",
            {"plate_number": "DRIVER-1", "brand": "Toyota", "model": "Prius", "color": "White", "seats": 4},
            format="json",
        )
        profile_list = self.client.get("/api/v1/driver-profiles/")
        vehicle_list = self.client.get("/api/v1/vehicles/")
        self.client.force_authenticate(staff)
        staff_profiles = self.client.get("/api/v1/driver-profiles/")
        staff_vehicles = self.client.get("/api/v1/vehicles/")

        self.assertEqual(profile_created.status_code, 201)
        self.assertEqual(vehicle_created.status_code, 201)
        self.assertFalse(profile_created.data["is_fleether_eligible"])
        self.assertFalse(profile_created.data["is_fleet_pmr_eligible"])
        self.assertEqual(len(profile_list.data), 1)
        self.assertEqual(len(vehicle_list.data), 1)
        self.assertEqual(len(staff_profiles.data), 2)
        self.assertEqual(len(staff_vehicles.data), 2)
