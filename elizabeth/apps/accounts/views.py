from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from apps.accounts.services import authenticate_user, register_user


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
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

    def post(self, request: Request, *args, **kwargs) -> Response:
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
