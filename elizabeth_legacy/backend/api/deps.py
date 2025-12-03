from __future__ import annotations

from typing import cast

from flask import current_app

from backend.backend.repositories.characteristics_repository import (
    ArmtekCharacteristicsRepository,
)
from backend.backend.services.armtek.service import ArmtekService
from backend.backend.services.tokens import ArmtekSearchContext


def get_armtek_service() -> ArmtekService:
    service = cast(ArmtekService | None, current_app.config.get("armtek_service"))
    if service is None:
        raise RuntimeError("Armtek service is not configured")
    return service


def get_search_context() -> ArmtekSearchContext:
    context = cast(
        ArmtekSearchContext | None, current_app.config.get("armtek_search_context")
    )
    if context is None:
        raise RuntimeError("Armtek search context is not configured")
    return context


def get_characteristics_repo() -> ArmtekCharacteristicsRepository:
    repo = cast(
        ArmtekCharacteristicsRepository | None,
        current_app.config.get("characteristics_repo"),
    )
    if repo is None:
        raise RuntimeError("Characteristics repository is not configured")
    return repo
