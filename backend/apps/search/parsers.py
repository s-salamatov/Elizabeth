from __future__ import annotations

import re
from typing import List, Tuple

SEPARATORS_PATTERN = re.compile(r"[\n,;.]+", re.MULTILINE)


def split_bulk_input(raw: str) -> List[str]:
    cleaned = raw.replace("\r", "\n")
    parts = SEPARATORS_PATTERN.split(cleaned)
    return [part.strip() for part in parts if part.strip()]


def split_pin_and_brand(query: str) -> Tuple[str, str]:
    text = query.strip()
    if " " in text:
        raise ValueError("Используйте формат PIN_BRAND без пробелов")
    if "_" not in text:
        raise ValueError("Укажите бренд через подчёркивание: PIN_BRAND")
    pin, brand = text.split("_", 1)
    if not pin.strip() or not brand.strip():
        raise ValueError("И артикул, и бренд обязательны: PIN_BRAND")
    return pin.strip(), brand.strip()
