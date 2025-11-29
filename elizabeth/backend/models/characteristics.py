from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from pydantic import BaseModel


class ProductHtmlDetails(BaseModel):
    artid: str
    image_url: str | None = None
    # в будущем могут добавляться другие поля (описание, атрибуты и т.п.)


@dataclass
class CharacteristicsRecord:
    token: str
    artid: str | None
    image_url: str | None = None
    weight: str | None = None
    length: str | None = None
    height: str | None = None
    width: str | None = None
    analog_code: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    received_at: datetime | None = None
    ready: bool = False

    def mark_ready(
        self,
        *,
        artid: str | None,
        image_url: str | None,
        weight: str | None,
        length: str | None,
        height: str | None,
        width: str | None,
        analog_code: str | None,
    ) -> None:
        self.artid = artid
        self.image_url = image_url
        self.weight = weight
        self.length = length
        self.height = height
        self.width = width
        self.analog_code = analog_code
        self.received_at = datetime.now(timezone.utc)
        self.ready = True
