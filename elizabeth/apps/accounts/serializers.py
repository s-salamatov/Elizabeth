from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from elizabeth.apps.accounts.models import UserSettings

User = get_user_model()
if TYPE_CHECKING:  # pragma: no cover - typing only
    from django.contrib.auth.models import AbstractBaseUser as UserModel
else:
    UserModel = Any


class UserSerializer(serializers.ModelSerializer[UserModel]):
    """Serialize public user fields."""

    class Meta:
        """Expose basic user fields."""

        model = User
        fields = ["id", "username", "email"]


class UserSettingsSerializer(serializers.ModelSerializer[UserSettings]):
    class Meta:
        """Settings fields exposed to the API."""

        model = UserSettings
        fields = ["default_search_source", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class UserUpdateSerializer(serializers.ModelSerializer[UserModel]):
    class Meta:
        """Mutable user profile fields."""

        model = User
        fields = ["email"]


class RegisterSerializer(serializers.Serializer[dict[str, object]]):
    """Registration payload."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value


class LoginSerializer(serializers.Serializer[dict[str, str]]):
    """Login payload."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
