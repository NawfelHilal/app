from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "phone_number"]
        read_only_fields = ["id", "username", "email", "role"]


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
