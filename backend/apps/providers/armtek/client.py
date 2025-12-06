from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Mapping, Optional, Sized

import httpx

from backend.apps.providers.armtek.exceptions import (
    ArmtekCredentialsError,
    ArmtekError,
    ArmtekResponseError,
)
from backend.apps.providers.armtek.types import ArmtekSearchItem

logger = logging.getLogger(__name__)


class ArmtekClient:
    def __init__(
        self,
        *,
        base_url: str,
        login: Optional[str],
        password: Optional[str],
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.login = login
        self.password = password
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
            # Armtek expects HTTP Basic auth in addition to credentials in the body.
            auth=(login, password) if login and password else None,
        )

    def close(self) -> None:
        self._client.close()

    def search(
        self,
        *,
        vkorg: str,
        kunnr_rg: str,
        pin: str,
        brand: str | None = None,
        query_type: int | None = None,
        program: str | None = None,
        kunnr_za: str | None = None,
        incoterms: int | None = None,
        vbeln: str | None = None,
    ) -> list[ArmtekSearchItem]:
        if not self.login or not self.password:
            raise ArmtekCredentialsError("Armtek credentials are not configured")

        payload: Dict[str, Any] = {
            "LOGIN": self.login,
            "PASSWORD": self.password,
            "VKORG": vkorg,
            "KUNNR_RG": kunnr_rg,
            "PIN": pin,
        }
        if brand:
            payload["BRAND"] = brand
        if query_type is None and brand is None:
            payload["QUERY_TYPE"] = 1
        elif query_type is not None:
            payload["QUERY_TYPE"] = query_type
        if program:
            payload["PROGRAM"] = program
        if kunnr_za:
            payload["KUNNR_ZA"] = kunnr_za
        if incoterms is not None:
            payload["INCOTERMS"] = incoterms
        if vbeln:
            payload["VBELN"] = vbeln

        raw = self._post("/api/ws_search/search", data=payload)
        resp = unwrap_resp(raw)
        array = resp.get("ARRAY", [])
        items_count = len(array) if isinstance(array, Sized) else None
        logger.info(
            "Armtek search RESP received",
            extra={
                "pin": pin,
                "brand": brand,
                "items_count": items_count,
            },
        )
        items: list[ArmtekSearchItem] = []
        if not isinstance(array, Iterable):
            raise ArmtekResponseError("RESP.ARRAY must be iterable")
        for entry in array:
            if not isinstance(entry, Mapping):
                raise ArmtekResponseError("RESP.ARRAY entries must be mappings")
            items.append(
                ArmtekSearchItem(
                    pin=str(entry.get("PIN", pin)),
                    brand=str(entry.get("BRAND", brand or "")),
                    name=str(entry.get("NAME", "")),
                    artid=str(entry.get("ARTID", "")),
                    is_analog=_coerce_analog(entry.get("ANALOG")),
                    price=_coerce_float(entry.get("PRICE")),
                    currency=_clean_str(entry.get("WAERS")),
                    warehouse_partner=_clean_str(entry.get("PARNR")),
                    warehouse_code=_clean_str(entry.get("KEYZAK")),
                    available_quantity=_coerce_int(entry.get("RVALUE")),
                    return_days=_coerce_int(entry.get("RETDAYS")),
                    multiplicity=_coerce_int(entry.get("RDPRF")),
                    minimum_order=_coerce_int(entry.get("MINBM")),
                    supply_probability=_coerce_float(
                        entry.get("VENSEL") or entry.get("VENSL")
                    ),
                    delivery_date=_clean_str(entry.get("DLVDT")),
                    warranty_date=_clean_str(entry.get("WRNTDT")),
                    import_flag=_clean_str(entry.get("TYPEB")),
                    special_flag=_clean_str(entry.get("DSPEC")),
                    max_retail_price=_coerce_float(entry.get("RCOST")),
                    markup=_coerce_float(entry.get("MRKBY")),
                    note=_clean_str(entry.get("PNOTE")),
                    importer_markup=_coerce_float(entry.get("IMP_ADD")),
                    producer_price=_coerce_float(entry.get("SELLP")),
                    markup_rest_rub=_coerce_float(entry.get("REST_ADD")),
                    markup_rest_percent=_coerce_float(entry.get("REST_ADD_P")),
                    raw=entry,
                )
            )
        return items

    def _post(self, path: str, *, data: Dict[str, Any]) -> Mapping[str, Any]:
        try:
            response = self._client.post(path, data=data)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:  # pragma: no cover - http guard
            raise ArmtekError(
                f"Armtek responded with HTTP {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:  # pragma: no cover - network guard
            raise ArmtekError(f"Network error contacting Armtek: {exc}") from exc
        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - parsing guard
            raise ArmtekResponseError("Armtek returned non-JSON payload") from exc
        if not isinstance(payload, Mapping):
            raise ArmtekResponseError("Armtek response must be a mapping")
        return payload

    def __enter__(self) -> "ArmtekClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        self.close()


def unwrap_resp(raw: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        raise ArmtekResponseError("Armtek response must be a mapping")
    status = raw.get("STATUS")
    if status != 200:
        raise ArmtekResponseError("Armtek returned error status", status=status)
    resp = raw.get("RESP")
    if resp is None:
        raise ArmtekResponseError("Armtek response missing RESP")
    if isinstance(resp, list):
        return {"ARRAY": resp}
    if not isinstance(resp, Mapping):
        raise ArmtekResponseError("Armtek RESP must be a mapping")
    return resp


def _coerce_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _clean_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    value_str = str(value).strip()
    return value_str or None


def _coerce_analog(value: Any) -> Optional[bool]:
    """Armtek ANALOG flag comes as 0/1 or sometimes 'X'."""
    if value is None or value == "":
        return None
    if isinstance(value, str):
        stripped = value.strip().upper()
        if stripped == "X":
            return True
        if stripped.isdigit():
            try:
                return bool(int(stripped))
            except ValueError:
                return None
    coerced_int = _coerce_int(value)
    if coerced_int is None:
        return None
    return bool(coerced_int)
