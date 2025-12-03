from __future__ import annotations

from typing import List, Optional

from django.conf import settings

from backend.apps.providers.armtek.client import ArmtekClient
from backend.apps.providers.armtek.exceptions import ArmtekCredentialsError
from backend.apps.providers.armtek.types import ArmtekSearchItem
from backend.apps.providers.services import ArmtekCredentials


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
        # Armtek PROGRAM sometimes comes back as a human label (e.g. "Russia") and
        # can filter results down to zero; we treat empty/meaningless values as absent.
        self.program = (
            credentials.program.strip() if credentials and credentials.program else None
        )
        if self.program and self.program.lower() == "russia":
            self.program = None
        self.base_url = base_url or settings.ARMTEK_BASE_URL
        self.timeout = timeout or float(settings.ARMTEK_TIMEOUT)
        self.enable_stub = (
            enable_stub
            if enable_stub is not None
            else getattr(settings, "ARMTEK_ENABLE_STUB", False)
        )

    def search(self, *, pin: str, brand: str | None = None) -> List[ArmtekSearchItem]:
        if self.enable_stub:
            return [self._build_stub_item(pin=pin, brand=brand)]

        if self.credentials is None:
            raise ArmtekCredentialsError("Armtek credentials are not configured")

        if not self.credentials.vkorg or not self.credentials.kunnr_rg:
            raise ArmtekCredentialsError("Armtek VKORG and KUNNR_RG are required")

        with ArmtekClient(
            base_url=self.base_url,
            login=self.credentials.login,
            password=self.credentials.password,
            timeout=self.timeout,
        ) as client:
            items = client.search(
                vkorg=self.credentials.vkorg,
                kunnr_rg=self.credentials.kunnr_rg,
                pin=pin,
                brand=brand,
                query_type=1,  # Only direct matches (exclude analogs) per Armtek API
                program=self.program,
                kunnr_za=self.credentials.kunnr_za,
                incoterms=self.credentials.incoterms,
                vbeln=self.credentials.vbeln,
            )
        main = self._pick_first_non_analog(items)
        return [main] if main else []

    def _build_stub_item(self, *, pin: str, brand: str | None) -> ArmtekSearchItem:
        label = brand or "STUB"
        artid = f"{pin.upper()}-{label.upper()}"
        return ArmtekSearchItem(
            pin=pin,
            brand=label,
            name=f"{pin} {label} (stub)",
            artid=artid,
            is_analog=False,
            price=0.0,
            currency="RUB",
            warehouse_partner="STUB",
            warehouse_code="STB",
            available_quantity=10,
            return_days=7,
            multiplicity=1,
            minimum_order=1,
            supply_probability=0.99,
            delivery_date=None,
            warranty_date=None,
            import_flag=None,
            special_flag=None,
            max_retail_price=0.0,
            markup=0.0,
            note="stub data",
            importer_markup=0.0,
            producer_price=0.0,
            markup_rest_rub=0.0,
            markup_rest_percent=0.0,
            raw={"stub": True},
        )

    @staticmethod
    def _pick_first_non_analog(
        items: list[ArmtekSearchItem],
    ) -> ArmtekSearchItem | None:
        """Return the first item that is not explicitly marked as analog."""
        for item in items:
            if item.is_analog is not True:
                return item
        return None
