from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from backend.apps.accounts.models import UserSettings

User = get_user_model()
if TYPE_CHECKING:  # pragma: no cover - typing only
    from django.contrib.auth.models import AbstractBaseUser as DjangoUser
else:
    DjangoUser = User  # runtime fallback


@dataclass
class AuthTokens:
    access: str
    refresh: str


def _build_tokens(user: DjangoUser) -> AuthTokens:
    refresh = RefreshToken.for_user(user)
    return AuthTokens(access=str(refresh.access_token), refresh=str(refresh))


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    phone_number: str,
    first_name: str = "",
    last_name: str = "",
    country: str,
) -> tuple[DjangoUser, AuthTokens]:
    user = User.objects.create_user(
        email=email,
        password=password,
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name,
    )
    UserSettings.objects.create(
        user=user,
        country=country,
    )
    return user, _build_tokens(user)


def authenticate_user(
    *, email: str, password: str
) -> Optional[tuple[DjangoUser, AuthTokens]]:
    user = authenticate(email=email, password=password)
    if user is None:
        return None
    return user, _build_tokens(user)
