from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class FleetProTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        token["username"] = user.username
        return token


class FleetProTokenObtainPairView(TokenObtainPairView):
    serializer_class = FleetProTokenObtainPairSerializer
