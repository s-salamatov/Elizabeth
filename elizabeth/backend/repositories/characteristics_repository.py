from __future__ import annotations

from typing import Dict, Optional

from elizabeth.backend.models.characteristics import CharacteristicsRecord


class ArmtekCharacteristicsRepository:
    def register(self, token: str, artid: str) -> None:
        raise NotImplementedError

    def save(
        self,
        token: str,
        artid: str | None,
        image_url: str | None,
        *,
        weight: str | None = None,
        length: str | None = None,
        height: str | None = None,
        width: str | None = None,
        analog_code: str | None = None,
    ) -> None:
        raise NotImplementedError

    def get_by_token(self, token: str) -> Optional[CharacteristicsRecord]:
        raise NotImplementedError


class InMemoryArmtekCharacteristicsRepository(ArmtekCharacteristicsRepository):
    """Простое in-memory хранилище характеристик."""

    def __init__(self) -> None:
        self._store: Dict[str, CharacteristicsRecord] = {}

    def register(self, token: str, artid: str) -> None:
        if not token:
            return
        if token in self._store:
            return
        self._store[token] = CharacteristicsRecord(token=token, artid=artid)

    def save(
        self,
        token: str,
        artid: str | None,
        image_url: str | None,
        *,
        weight: str | None = None,
        length: str | None = None,
        height: str | None = None,
        width: str | None = None,
        analog_code: str | None = None,
    ) -> None:
        record = self._store.get(token)
        if record is None:
            record = CharacteristicsRecord(token=token, artid=artid)
            self._store[token] = record
        record.mark_ready(
            artid=artid,
            image_url=image_url,
            weight=weight,
            length=length,
            height=height,
            width=width,
            analog_code=analog_code,
        )

    def get_by_token(self, token: str) -> Optional[CharacteristicsRecord]:
        return self._store.get(token)
