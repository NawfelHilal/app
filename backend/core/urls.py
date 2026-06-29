from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.tokens import FleetProTokenObtainPairView
from apps.accounts.views import AccountViewSet
from apps.notifications.views import DeviceTokenViewSet
from apps.payments.views import PaymentViewSet
from apps.rides.views import DriverProfileViewSet, RideViewSet, VehicleViewSet
from apps.rides.health import health

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename="accounts")
router.register("rides", RideViewSet, basename="rides")
router.register("driver-profiles", DriverProfileViewSet, basename="driver-profiles")
router.register("vehicles", VehicleViewSet, basename="vehicles")
router.register("payments", PaymentViewSet, basename="payments")
router.register("notifications/devices", DeviceTokenViewSet, basename="device-tokens")

urlpatterns = [
    path("api/v1/health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("api/v1/auth/token/", FleetProTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/", include(router.urls)),
]
