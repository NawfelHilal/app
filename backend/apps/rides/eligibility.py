from django.core.exceptions import ObjectDoesNotExist

from .models import Ride


def driver_is_eligible_for_service(driver, service_type: str) -> bool:
    if not getattr(driver, "is_driver", False):
        return False
    if service_type in {Ride.ServiceType.STANDARD, Ride.ServiceType.FLEET_LUXE}:
        return True
    if service_type == Ride.ServiceType.FLEETHER:
        try:
            return driver.driver_profile.is_fleether_eligible
        except ObjectDoesNotExist:
            return False
    if service_type == Ride.ServiceType.FLEET_PMR:
        return driver.vehicles.filter(is_pmr_adapted=True).exists()
    return False
