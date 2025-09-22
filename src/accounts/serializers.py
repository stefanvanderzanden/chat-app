from typing import Any, TypedDict, Union

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserPayload(TypedDict):
    id: int
    username: str
    email: str

class TokenResponse(TypedDict, total=False):
    refresh: str
    access: str
    user: UserPayload


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Union[str, dict[str, str]]]:
        data  = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.email,
            "email": self.user.email,
        }
        return data