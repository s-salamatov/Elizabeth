from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.accounts.models import UserSettings
from backend.apps.accounts.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    UserSettingsSerializer,
    UserUpdateSerializer,
)
from backend.apps.accounts.services import authenticate_user, register_user


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        timezone_value = data.pop("timezone", "browser")
        user, tokens = register_user(**data)
        request.session["timezone"] = timezone_value
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {"access": tokens.access, "refresh": tokens.refresh},
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = authenticate_user(**serializer.validated_data)
        if result is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user, tokens = result
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {"access": tokens.access, "refresh": tokens.refresh},
            }
        )


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        settings_obj, _ = UserSettings.objects.get_or_create(
            user=user,
            defaults={
                "country": UserSettings._meta.get_field("country").default,
                "default_search_source": UserSettings._meta.get_field(
                    "default_search_source"
                ).default,
            },
        )
        return Response(
            {
                "user": UserSerializer(user).data,
                "settings": UserSettingsSerializer(settings_obj).data,
            }
        )

    def patch(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)
        data = request.data.copy()
        timezone_value = data.pop("timezone", None)
        if timezone_value:
            request.session["timezone"] = timezone_value
        user_serializer = UserUpdateSerializer(user, data=data, partial=True)
        settings_serializer = UserSettingsSerializer(
            settings_obj, data=data, partial=True
        )
        user_serializer.is_valid(raise_exception=True)
        settings_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        settings_serializer.save()
        return Response(
            {
                "user": UserSerializer(user).data,
                "settings": UserSettingsSerializer(settings_obj).data,
            }
        )


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
