from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserSettings

User = get_user_model()


@dataclass
class AuthTokens:
    access: str
    refresh: str


def _build_tokens(user: User) -> AuthTokens:
    refresh = RefreshToken.for_user(user)
    return AuthTokens(access=str(refresh.access_token), refresh=str(refresh))


@transaction.atomic
def register_user(*, username: str, password: str, email: Optional[str] = None) -> tuple[User, AuthTokens]:
    user = User.objects.create_user(username=username, password=password, email=email)
    UserSettings.objects.create(user=user)
    return user, _build_tokens(user)


def authenticate_user(*, username: str, password: str) -> Optional[tuple[User, AuthTokens]]:
    user = authenticate(username=username, password=password)
    if user is None:
        return None
    return user, _build_tokens(user)
