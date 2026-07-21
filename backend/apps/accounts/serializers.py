from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    _links = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "phone_number", "_links"]
        read_only_fields = ["id", "username", "email", "role"]

    def get__links(self, obj):
        request = self.context.get("request")

        def uri(path: str) -> str:
            if request:
                return request.build_absolute_uri(path)
            return path

        links = {
            "self": {"href": uri("/api/v1/accounts/me/"), "method": "GET"},
            "update": {"href": uri("/api/v1/accounts/me/"), "method": "PATCH"},
            "change_password": {"href": uri("/api/v1/accounts/change-password/"), "method": "POST"},
            "rides": {"href": uri("/api/v1/rides/"), "method": "GET"},
            "device_tokens": {"href": uri("/api/v1/notifications/devices/"), "method": "GET"},
        }
        if obj.is_driver:
            links["driver_profile"] = {"href": uri("/api/v1/driver-profiles/"), "method": "GET"}
            links["vehicles"] = {"href": uri("/api/v1/vehicles/"), "method": "GET"}
        return links


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, password):
        if not self.context["request"].user.check_password(password):
            raise serializers.ValidationError("Current password is incorrect.")
        return password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "phone_number"]
        read_only_fields = ["id"]

    def validate_role(self, role):
        if role == User.Role.ADMIN:
            raise serializers.ValidationError("Admin accounts must be created by staff.")
        return role

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
