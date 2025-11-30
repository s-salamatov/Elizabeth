from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable


def _hash_parts(prefix: str, parts: Iterable[object]) -> str:
    joined = ":".join("" if part is None else str(part) for part in parts)
    raw = f"{prefix}:{joined}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ArmtekSearchContext:
    vkorg: str
    kunnr_rg: str
    program: str | None = None
    kunnr_za: str | None = None
    incoterms: int | None = None
    vbeln: str | None = None


def generate_api_token(
    *,
    artid: str,
    pin: str,
    brand: str | None,
    context: ArmtekSearchContext,
) -> str:
    """Детерминированный токен для запроса к API Armtek."""
    parts = (
        context.vkorg,
        context.kunnr_rg,
        pin,
        brand or "",
        artid,
        context.program or "",
        context.kunnr_za or "",
        context.incoterms if context.incoterms is not None else "",
        context.vbeln or "",
    )
    return _hash_parts("api", parts)


def generate_characteristics_token(*, artid: str) -> str:
    """Детерминированный токен характеристик для конкретного artid."""
    return _hash_parts("char", (artid,))
