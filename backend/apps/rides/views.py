from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Ride
from .matching import RideMatcher
from .serializers import FareQuoteResponseSerializer, FareQuoteSerializer, RideSerializer
from .services import RideLifecycle


class RideViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Ride.objects.all()
        if getattr(user, "is_driver", False):
            requested = Ride.objects.filter(status=Ride.Status.REQUESTED)
            nearby_ids = RideMatcher().nearby_ride_ids(user.id, requested)
            return Ride.objects.filter(Q(driver=user) | Q(id__in=nearby_ids))
        return Ride.objects.filter(passenger=user)

    def create(self, request, *args, **kwargs):
        if getattr(request.user, "is_driver", False):
            return Response({"detail": "Only passengers can request rides."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    def quote(self, request):
        serializer = FareQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quote = serializer.validated_data["quote"]
        return Response(FareQuoteResponseSerializer(quote).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        if not request.user.is_driver:
            return Response({"detail": "Only drivers can accept rides."}, status=status.HTTP_403_FORBIDDEN)
        visible_ride = self.get_object()
        with transaction.atomic():
            ride = Ride.objects.select_for_update().get(pk=visible_ride.pk)
            if ride.status != Ride.Status.REQUESTED:
                return Response({"detail": "Ride is not available."}, status=status.HTTP_409_CONFLICT)
            ride = RideLifecycle().record(ride, Ride.Status.ACCEPTED, request.user)
        return Response(self.get_serializer(ride).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        ride = self.get_object()
        if ride.driver_id != request.user.id:
            return Response({"detail": "Only assigned driver can start this ride."}, status=status.HTTP_403_FORBIDDEN)
        if ride.status != Ride.Status.ACCEPTED:
            return Response({"detail": "Ride must be accepted first."}, status=status.HTTP_409_CONFLICT)
        ride = RideLifecycle().record(ride, Ride.Status.IN_PROGRESS, request.user)
        return Response(self.get_serializer(ride).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        ride = self.get_object()
        if ride.driver_id != request.user.id:
            return Response({"detail": "Only assigned driver can complete this ride."}, status=status.HTTP_403_FORBIDDEN)
        if ride.status != Ride.Status.IN_PROGRESS:
            return Response({"detail": "Ride must be in progress."}, status=status.HTTP_409_CONFLICT)
        ride = RideLifecycle().record(ride, Ride.Status.COMPLETED, request.user)
        return Response(self.get_serializer(ride).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        ride = self.get_object()
        if request.user.id not in {ride.passenger_id, ride.driver_id} and not request.user.is_staff:
            return Response({"detail": "You cannot cancel this ride."}, status=status.HTTP_403_FORBIDDEN)
        if ride.status in {Ride.Status.COMPLETED, Ride.Status.CANCELED}:
            return Response({"detail": "Ride is already closed."}, status=status.HTTP_409_CONFLICT)
        ride = RideLifecycle().record(ride, Ride.Status.CANCELED, request.user)
        return Response(self.get_serializer(ride).data)

    @action(detail=True, methods=["post"])
    def simulate(self, request, pk=None):
        ride = self.get_object()
        if ride.passenger_id != request.user.id:
            return Response({"detail": "Only the passenger can run demo simulation."}, status=status.HTTP_403_FORBIDDEN)
        if ride.status in {Ride.Status.COMPLETED, Ride.Status.CANCELED}:
            return Response(self.get_serializer(ride).data)

        User = get_user_model()
        demo_driver = User.objects.filter(username="driver", role=User.Role.DRIVER).first()
        if not demo_driver:
            return Response({"detail": "Demo driver account is missing."}, status=status.HTTP_409_CONFLICT)

        next_status = {
            Ride.Status.REQUESTED: Ride.Status.ACCEPTED,
            Ride.Status.ACCEPTED: Ride.Status.IN_PROGRESS,
            Ride.Status.IN_PROGRESS: Ride.Status.COMPLETED,
        }[ride.status]
        actor = demo_driver if next_status == Ride.Status.ACCEPTED else ride.driver or demo_driver
        ride = RideLifecycle().record(ride, next_status, actor)
        return Response(self.get_serializer(ride).data)
