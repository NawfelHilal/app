from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.rides.models import Ride

from .models import Payment
from .serializers import CreatePaymentIntentSerializer, PaymentSerializer
from .services import SimulatedPaymentGateway, StripePaymentGateway


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(ride__passenger=user)

    @action(detail=False, methods=["post"], url_path="create-intent")
    def create_intent(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ride = get_object_or_404(Ride, id=serializer.validated_data["ride_id"], passenger=request.user)
        payment = StripePaymentGateway().create_payment_intent(ride)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="simulate-intent")
    def simulate_intent(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ride = get_object_or_404(Ride, id=serializer.validated_data["ride_id"], passenger=request.user)
        payment = SimulatedPaymentGateway().authorize_ride(ride)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
