from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence, cast

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from backend.apps.accounts.models import UserSettings

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
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
        ]


class UserSettingsSerializer(serializers.ModelSerializer[UserSettings]):
    class Meta:
        """Settings fields exposed to the API."""

        model = UserSettings
        fields = [
            "default_search_source",
            "country",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class UserUpdateSerializer(serializers.ModelSerializer[UserModel]):
    class Meta:
        """Mutable user profile fields."""

        model = User
        fields = ["email", "first_name", "last_name", "phone_number"]


class RegisterSerializer(serializers.Serializer[dict[str, object]]):
    """Registration payload."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")
    country = serializers.ChoiceField(
        choices=cast(Sequence[Any], UserSettings._meta.get_field("country").choices)
    )
    timezone = serializers.CharField(
        required=False, allow_blank=True, default="browser"
    )

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_phone_number(self, value: str) -> str:
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists")
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer[dict[str, str]]):
    """Login payload."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
