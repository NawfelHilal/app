import json

from django.test import SimpleTestCase, override_settings
from redis.exceptions import RedisError

from apps.rides.matching import RideMatcher, distance_km


class FakeRedis:
    def __init__(self, payload):
        self.payload = payload

    def get(self, key):
        return self.payload


class BrokenRedis:
    def get(self, key):
        raise RedisError("redis down")


class RideMatcherTests(SimpleTestCase):
    def test_distance_uses_geographic_coordinates(self):
        self.assertAlmostEqual(distance_km(48.8566, 2.3522, 48.8584, 2.2945), 4.2, delta=0.2)

    @override_settings(GPS_MATCH_RADIUS_KM=5)
    def test_filters_rides_outside_matching_radius(self):
        position = json.dumps({"latitude": 48.8566, "longitude": 2.3522})
        rides = FakeRideQuerySet(
            [
                FakeRide(1, 48.8584, 2.2945),
                FakeRide(2, 48.7000, 2.1000),
            ]
        )

        ids = RideMatcher(FakeRedis(position)).nearby_ride_ids(42, rides)

        self.assertEqual(ids, [1])

    def test_missing_invalid_and_broken_driver_position_returns_no_rides(self):
        rides = FakeRideQuerySet([FakeRide(1, 48.8584, 2.2945)])

        self.assertEqual(RideMatcher(FakeRedis(None)).nearby_ride_ids(42, rides), [])
        self.assertEqual(RideMatcher(FakeRedis("{bad-json")).nearby_ride_ids(42, rides), [])
        self.assertEqual(RideMatcher(FakeRedis(json.dumps({"latitude": "bad"}))).nearby_ride_ids(42, rides), [])
        self.assertEqual(RideMatcher(BrokenRedis()).nearby_ride_ids(42, rides), [])


class FakeRide:
    def __init__(self, ride_id, latitude, longitude):
        self.id = ride_id
        self.pickup_latitude = latitude
        self.pickup_longitude = longitude


class FakeRideQuerySet(list):
    def only(self, *fields):
        return self
