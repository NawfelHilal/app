from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "ride",
            "amount_cents",
            "currency",
            "stripe_payment_intent_id",
            "client_secret",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CreatePaymentIntentSerializer(serializers.Serializer):
    ride_id = serializers.IntegerField()

