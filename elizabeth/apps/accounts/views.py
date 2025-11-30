from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from elizabeth.apps.accounts.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    UserSettingsSerializer,
    UserUpdateSerializer,
)
from elizabeth.apps.accounts.services import authenticate_user, register_user
from elizabeth.apps.accounts.models import UserSettings


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, tokens = register_user(**serializer.validated_data)
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
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        return Response(
            {
                "user": UserSerializer(request.user).data,
                "settings": UserSettingsSerializer(settings_obj).data,
            }
        )

    def patch(self, request: Request, *args: object, **kwargs: object) -> Response:
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        user_serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        settings_serializer = UserSettingsSerializer(
            settings_obj, data=request.data, partial=True
        )
        user_serializer.is_valid(raise_exception=True)
        settings_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        settings_serializer.save()
        return Response(
            {
                "user": UserSerializer(request.user).data,
                "settings": UserSettingsSerializer(settings_obj).data,
            }
        )
