from __future__ import annotations

import base64
import hashlib
from functools import lru_cache
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


class ProviderName(models.TextChoices):
    ARMTEK = "armtek", "Armtek"


@lru_cache(maxsize=1)
def _cipher() -> Fernet:
    secret = settings.PROVIDER_SECRET_KEY or settings.SECRET_KEY
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)


def encrypt_secret(value: str) -> str:
    return _cipher().encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> Optional[str]:
    if not value:
        return None
    try:
        return _cipher().decrypt(value.encode()).decode()
    except InvalidToken:
        return None


class ProviderAccount(models.Model):
    """Encrypted credentials for a data provider per user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_accounts",
    )
    provider_name = models.CharField(
        max_length=64, choices=ProviderName.choices, default=ProviderName.ARMTEK
    )
    login = models.CharField(max_length=255)
    encrypted_password = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Unique provider per user."""

        verbose_name = "Provider account"
        verbose_name_plural = "Provider accounts"
        unique_together = ("user", "provider_name")

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.provider_name} credentials for {self.user}"

    @property
    def password(self) -> Optional[str]:
        return decrypt_secret(self.encrypted_password)

    def set_password(self, raw_password: str) -> None:
        self.encrypted_password = encrypt_secret(raw_password)
