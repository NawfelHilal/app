from rest_framework import serializers

from .models import DeviceToken


class DeviceTokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(validators=[])

    class Meta:
        model = DeviceToken
        fields = ["id", "token", "platform", "enabled", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        token = validated_data.pop("token")
        device, _ = DeviceToken.objects.update_or_create(token=token, defaults=validated_data)
        return device
