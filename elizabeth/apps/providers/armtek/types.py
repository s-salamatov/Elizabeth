from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass
class ArmtekSearchItem:
    pin: str
    brand: str
    name: str
    artid: str
    is_analog: Optional[bool] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    raw: Optional[Mapping[str, Any]] = None


@dataclass
class ArmtekProductDetails:
    artid: str
    analog_code: Optional[str] = None
    image_url: Optional[str] = None
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    raw: Optional[Mapping[str, Any]] = None
