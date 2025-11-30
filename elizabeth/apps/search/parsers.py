from __future__ import annotations

import re
from typing import List, Optional, Tuple

SEPARATORS_PATTERN = re.compile(r"[\n,;]+")


def split_bulk_input(raw: str) -> List[str]:
    parts = SEPARATORS_PATTERN.split(raw)
    return [part.strip() for part in parts if part.strip()]


def split_pin_and_brand(query: str) -> Tuple[str, Optional[str]]:
    text = query.strip()
    # Accept formats: PIN_BRAND, PIN BRAND, PIN
    if "_" in text:
        pin, brand = text.split("_", 1)
    elif " " in text:
        pin, brand = text.split(" ", 1)
    else:
        pin, brand = text, None
    return pin.strip(), brand.strip() if brand else None
