from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

import httpx

from elizabeth.apps.providers.armtek.client import unwrap_resp
from elizabeth.apps.providers.armtek.exceptions import (
    ArmtekCredentialsError,
    ArmtekError,
)


@dataclass
class ArmtekProfile:
    """Minimal set of Armtek fields required for search requests."""

    vkorg: str
    kunnr_rg: str
    program: Optional[str] = None
    kunnr_za: Optional[str] = None
    incoterms: Optional[int] = None
    vbeln: Optional[str] = None


def _normalize_bool(value: Any) -> bool:
    return str(value).lower() in {"1", "true", "t", "yes", "y", "on", "default"}


def _pick_default(entry_list: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    for entry in entry_list:
        if _normalize_bool(
            entry.get("DEFAULT") or entry.get("IS_DEFAULT") or entry.get("DEF")
        ):
            return entry
    return entry_list[0]


def fetch_armtek_profile(
    *,
    base_url: str,
    timeout: float,
    login: str,
    password: str,
) -> ArmtekProfile:
    """Fetch vkorg/kunnr_rg/etc for the user via Armtek user APIs."""
    if not login or not password:
        raise ArmtekCredentialsError("Armtek login and password are required")

    try:
        with httpx.Client(
            base_url=base_url.rstrip("/"),
            auth=(login, password),
            timeout=timeout,
        ) as client:
            vkorg_resp = client.get(
                "/api/ws_user/getUserVkorgList", params={"format": "json"}
            )
            vkorg_data = unwrap_resp(_parse_json_mapping(vkorg_resp))
            vkorg_array = vkorg_data.get("ARRAY") or []
            if not isinstance(vkorg_array, list) or not vkorg_array:
                raise ArmtekError("Armtek did not return VKORG list")
            vkorg_entry = _pick_default(
                [_ensure_mapping(item, "VKORG entry") for item in vkorg_array]
            )
            vkorg = str(
                vkorg_entry.get("VKORG") or vkorg_entry.get("vkorg") or ""
            ).strip()
            program = (
                vkorg_entry.get("PROGRAM_NAME") or vkorg_entry.get("PROGRAM") or None
            ) and str(vkorg_entry.get("PROGRAM_NAME") or vkorg_entry.get("PROGRAM"))
            if not vkorg:
                raise ArmtekError("Armtek VKORG is missing in response")

            info_resp = client.post(
                "/api/ws_user/getUserInfo",
                params={"format": "json"},
                data={"VKORG": vkorg, "STRUCTURE": "1"},
            )
            info_data = unwrap_resp(_parse_json_mapping(info_resp))
            structure = info_data.get("STRUCTURE")
            if isinstance(structure, list) and structure:
                structure = structure[0]
            structure_map = _ensure_mapping(structure, "RESP.STRUCTURE")

            kunnr_rg = _extract_default_id(structure_map.get("RG_TAB"), "RG_TAB")
            if not kunnr_rg:
                raise ArmtekError("Armtek response missing KUNNR_RG")
            kunnr_rg = str(kunnr_rg)
            kunnr_za = _extract_default_id(structure_map.get("ZA_TAB"), "ZA_TAB")
            vbeln = _extract_default_vbeln(structure_map.get("DOGOVOR_TAB"))

            return ArmtekProfile(
                vkorg=vkorg,
                kunnr_rg=kunnr_rg,
                program=program,
                kunnr_za=kunnr_za,
                incoterms=None,
                vbeln=vbeln,
            )
    except httpx.TimeoutException as exc:
        raise ArmtekError("Armtek user API timed out") from exc
    except httpx.RequestError as exc:  # pragma: no cover - network guard
        raise ArmtekError(f"Armtek user API request failed: {exc}") from exc


def _parse_json_mapping(response: httpx.Response) -> Mapping[str, Any]:
    payload = response.json()
    if not isinstance(payload, Mapping):
        raise ArmtekError("Armtek user API returned invalid payload")
    return payload


def _ensure_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ArmtekError(f"{label} must be an object")
    return value


def _extract_default_id(raw: Any, label: str) -> Optional[str]:
    if raw is None:
        return None
    if isinstance(raw, list) and raw and not isinstance(raw[0], (str, bytes)):
        entries = [_ensure_mapping(item, f"{label} item") for item in raw]
    elif isinstance(raw, Mapping):
        entries = [_ensure_mapping(raw, f"{label} item")]
    else:
        return None
    chosen = _pick_default(entries)
    val = (
        chosen.get("ID")
        or chosen.get("KUNNR")
        or chosen.get("KUNRG")
        or chosen.get("KUNNR_RG")
    )
    return str(val).strip() if val else None


def _extract_default_vbeln(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    if isinstance(raw, list):
        entries = raw
    elif isinstance(raw, Mapping):
        entries = [raw]
    else:
        return None
    entries = [_ensure_mapping(item, "DOGOVOR_TAB item") for item in entries if item]
    if not entries:
        return None
    chosen = _pick_default(entries)
    vbeln = chosen.get("VBELN")
    return str(vbeln).strip() if vbeln else None
