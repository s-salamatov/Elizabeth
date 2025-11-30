from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional

import httpx

from elizabeth.apps.providers.armtek.exceptions import (
    ArmtekCredentialsError,
    ArmtekError,
    ArmtekResponseError,
)
from elizabeth.apps.providers.armtek.types import ArmtekSearchItem


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
            base_url=self.base_url, timeout=timeout, transport=transport
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
                    is_analog=(
                        bool(entry.get("ANALOG"))
                        if entry.get("ANALOG") is not None
                        else None
                    ),
                    price=_coerce_float(entry.get("PRICE")),
                    currency=str(entry.get("WAERS")) if entry.get("WAERS") else None,
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
