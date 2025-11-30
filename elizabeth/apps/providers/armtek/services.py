from __future__ import annotations

from typing import Iterable, List, Optional

from django.conf import settings

from apps.providers.armtek.client import ArmtekClient
from apps.providers.armtek.exceptions import ArmtekCredentialsError
from apps.providers.armtek.types import ArmtekSearchItem
from apps.providers.services import ArmtekCredentials


class ArmtekSearchService:
    def __init__(
        self,
        credentials: Optional[ArmtekCredentials],
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        enable_stub: bool | None = None,
    ) -> None:
        self.credentials = credentials
        self.base_url = base_url or settings.ARMTEK_BASE_URL
        self.timeout = timeout or float(settings.ARMTEK_TIMEOUT)
        self.enable_stub = (
            enable_stub
            if enable_stub is not None
            else getattr(settings, "ARMTEK_ENABLE_STUB", False)
        )

    def search(self, *, pin: str, brand: str | None = None) -> List[ArmtekSearchItem]:
        if self.credentials is None:
            if self.enable_stub:
                return [self._build_stub_item(pin=pin, brand=brand)]
            raise ArmtekCredentialsError("Armtek credentials are not configured")

        if not self.credentials.vkorg or not self.credentials.kunnr_rg:
            raise ArmtekCredentialsError("Armtek VKORG and KUNNR_RG are required")

        with ArmtekClient(
            base_url=self.base_url,
            login=self.credentials.login,
            password=self.credentials.password,
            timeout=self.timeout,
        ) as client:
            return client.search(
                vkorg=self.credentials.vkorg,
                kunnr_rg=self.credentials.kunnr_rg,
                pin=pin,
                brand=brand,
                program=self.credentials.program,
                kunnr_za=self.credentials.kunnr_za,
                incoterms=self.credentials.incoterms,
                vbeln=self.credentials.vbeln,
            )

    def _build_stub_item(self, *, pin: str, brand: str | None) -> ArmtekSearchItem:
        label = brand or "STUB"
        artid = f"{pin.upper()}-{label.upper()}"
        return ArmtekSearchItem(
            pin=pin,
            brand=label,
            name=f"{pin} {label} (stub)",
            artid=artid,
            is_analog=False,
            price=None,
            currency=None,
            raw={"stub": True},
        )
