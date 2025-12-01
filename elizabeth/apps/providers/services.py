from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction

from elizabeth.apps.providers.armtek.profile import ArmtekProfile, fetch_armtek_profile
from elizabeth.apps.providers.models import ProviderAccount, ProviderName

if TYPE_CHECKING:
    from django.contrib.auth.models import User as DjangoUser  # runtime alias
else:
    DjangoUser = AbstractBaseUser


@dataclass
class ArmtekCredentials:
    login: str
    password: str
    pin: Optional[str]
    vkorg: Optional[str]
    kunnr_rg: Optional[str]
    program: Optional[str]
    kunnr_za: Optional[str]
    incoterms: Optional[int]
    vbeln: Optional[str]


@transaction.atomic
def save_provider_account(
    *,
    user: Any,
    provider_name: str,
    login: str,
    password: str,
    pin: str | None = None,
    vkorg: str | None = None,
    kunnr_rg: str | None = None,
    program: str | None = None,
    kunnr_za: str | None = None,
    incoterms: int | None = None,
    vbeln: str | None = None,
) -> ProviderAccount:
    account, _created = ProviderAccount.objects.get_or_create(
        user=user, provider_name=provider_name
    )
    account.login = login
    account.set_password(password)
    account.pin = pin
    account.vkorg = vkorg
    account.kunnr_rg = kunnr_rg
    account.program = program
    account.kunnr_za = kunnr_za
    account.incoterms = incoterms
    account.vbeln = vbeln
    account.save(
        update_fields=[
            "login",
            "encrypted_password",
            "pin",
            "vkorg",
            "kunnr_rg",
            "program",
            "kunnr_za",
            "incoterms",
            "vbeln",
            "updated_at",
        ]
    )
    return account


def update_armtek_account_context(account: ProviderAccount) -> ArmtekProfile:
    """Fetch vkorg/kunnr/etc from Armtek and persist on the account."""
    profile = fetch_armtek_profile(
        base_url=settings.ARMTEK_BASE_URL,
        timeout=float(settings.ARMTEK_TIMEOUT),
        login=account.login,
        password=account.password or "",
    )
    account.vkorg = profile.vkorg
    account.kunnr_rg = profile.kunnr_rg
    account.program = profile.program
    account.kunnr_za = profile.kunnr_za
    account.incoterms = profile.incoterms
    account.vbeln = profile.vbeln
    account.save(
        update_fields=[
            "vkorg",
            "kunnr_rg",
            "program",
            "kunnr_za",
            "incoterms",
            "vbeln",
            "updated_at",
        ]
    )
    return profile


def get_provider_account(*, user: Any, provider_name: str) -> Optional[ProviderAccount]:
    try:
        return ProviderAccount.objects.get(user=user, provider_name=provider_name)
    except ProviderAccount.DoesNotExist:
        return None


def resolve_armtek_credentials(
    user: Any | None = None,
) -> Optional[ArmtekCredentials]:
    if user is None:
        return None

    account = get_provider_account(user=user, provider_name=ProviderName.ARMTEK)
    if account is None or not account.password:
        return None

    return ArmtekCredentials(
        login=account.login,
        password=account.password,
        pin=account.pin,
        vkorg=account.vkorg,
        kunnr_rg=account.kunnr_rg,
        program=account.program,
        kunnr_za=account.kunnr_za,
        incoterms=account.incoterms,
        vbeln=account.vbeln,
    )
