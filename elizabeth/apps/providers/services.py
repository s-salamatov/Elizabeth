from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db import transaction

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
) -> ProviderAccount:
    account, _created = ProviderAccount.objects.get_or_create(
        user=user, provider_name=provider_name
    )
    account.login = login
    account.set_password(password)
    account.save(update_fields=["login", "encrypted_password", "updated_at"])
    return account


def get_provider_account(
    *, user: Any, provider_name: str
) -> Optional[ProviderAccount]:
    try:
        return ProviderAccount.objects.get(user=user, provider_name=provider_name)
    except ProviderAccount.DoesNotExist:
        return None


def resolve_armtek_credentials(
    user: Any | None = None,
) -> Optional[ArmtekCredentials]:
    login = settings.ARMTEK_LOGIN
    password = settings.ARMTEK_PASSWORD
    pin = settings.ARMTEK_PIN
    vkorg = settings.ARMTEK_VKORG
    kunnr_rg = settings.ARMTEK_KUNNR_RG
    program = settings.ARMTEK_PROGRAM
    kunnr_za = settings.ARMTEK_KUNNR_ZA
    incoterms = settings.ARMTEK_INCOTERMS
    vbeln = settings.ARMTEK_VBELN

    if user is not None:
        account = get_provider_account(user=user, provider_name=ProviderName.ARMTEK)
        if account and account.password:
            login = account.login
            password = account.password

    if not login or not password:
        return None

    return ArmtekCredentials(
        login=login,
        password=password,
        pin=pin,
        vkorg=vkorg,
        kunnr_rg=kunnr_rg,
        program=program,
        kunnr_za=kunnr_za,
        incoterms=incoterms,
        vbeln=vbeln,
    )
