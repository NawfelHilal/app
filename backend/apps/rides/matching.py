import json
from math import asin, cos, radians, sin, sqrt

from django.conf import settings
from redis import Redis
from redis.exceptions import RedisError


class RideMatcher:
    def __init__(self, redis_client: Redis | None = None):
        self.redis = redis_client or Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def nearby_ride_ids(self, driver_id: int, rides) -> list[int]:
        position = self._driver_position(driver_id)
        if position is None:
            return []

        radius_km = settings.GPS_MATCH_RADIUS_KM
        return [
            ride.id
            for ride in rides.only("id", "pickup_latitude", "pickup_longitude")
            if distance_km(
                position[0],
                position[1],
                float(ride.pickup_latitude),
                float(ride.pickup_longitude),
            )
            <= radius_km
        ]

    def _driver_position(self, driver_id: int) -> tuple[float, float] | None:
        try:
            payload = self.redis.get(f"fleetpro:gps:driver:{driver_id}")
        except RedisError:
            return None
        if not payload:
            return None

        try:
            position = json.loads(payload)
            return float(position["latitude"]), float(position["longitude"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None


def distance_km(latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
    latitude_delta = radians(latitude_b - latitude_a)
    longitude_delta = radians(longitude_b - longitude_a)
    start_latitude = radians(latitude_a)
    end_latitude = radians(latitude_b)
    haversine = (
        sin(latitude_delta / 2) ** 2
        + cos(start_latitude) * cos(end_latitude) * sin(longitude_delta / 2) ** 2
    )
    return 6371 * 2 * asin(sqrt(haversine))
