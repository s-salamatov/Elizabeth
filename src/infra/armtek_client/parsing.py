from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Iterable, Mapping, Sequence

from .exceptions import ArmtekResponseFormatError


def ensure_mapping(name: str, value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ArmtekResponseFormatError(f"{name} section must be a mapping")
    return value


def ensure_sequence(name: str, value: Any) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ArmtekResponseFormatError(f"{name} section must be a list")
    return value


def first_value(data: Mapping[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in data:
            val = data[key]
            if val is not None:
                return val
    return None


def require_value(data: Mapping[str, Any], keys: Iterable[str], field_name: str) -> Any:
    value = first_value(data, keys)
    if value is None or value == "":
        raise ArmtekResponseFormatError(f"Missing required field {field_name}")
    return value


def parse_bool_flag(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"1", "y", "yes", "true", "x", "on"}


def parse_datetime_value(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    text = str(value)
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise ArmtekResponseFormatError(f"Invalid datetime value: {text}") from exc


def parse_decimal_value(value: Any) -> Decimal:
    text = str(value).strip()
    if text and text[0] in {">", "<"}:
        text = text[1:].strip()
    # Remove grouping separators
    text = text.replace(" ", "").replace(",", "")
    try:
        return Decimal(text)
    except Exception as exc:
        raise ArmtekResponseFormatError(f"Invalid decimal value: {value}") from exc
