from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from elizabeth.backend.api.deps import (
    get_armtek_service,
    get_characteristics_repo,
    get_search_context,
)
from elizabeth.backend.models.search_result import SearchItem
from elizabeth.backend.repositories.characteristics_repository import (
    ArmtekCharacteristicsRepository,
)
from elizabeth.backend.services.armtek.exceptions import ArmtekError
from elizabeth.backend.services.tokens import (
    ArmtekSearchContext,
    generate_api_token,
    generate_characteristics_token,
)
from elizabeth.backend.utils.logger import get_logger

logger = get_logger(__name__)

search_bp = Blueprint("search_api", __name__)


def parse_query(query: str) -> tuple[str, str | None]:
    """Parse user input into article and optional brand."""
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("Введите артикул для поиска")

    article: str
    brand: str | None = None

    if "_" in cleaned:
        left, right = cleaned.split("_", 1)
        article, brand = left.strip(), right.strip()
    elif " " in cleaned:
        left, right = cleaned.split(" ", 1)
        article, brand = left.strip(), right.strip()
    else:
        article = cleaned

    if not article:
        raise ValueError("Артикул не должен быть пустым")

    if brand:
        brand = brand.upper()
    else:
        brand = None

    return article, brand


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def serialize_search_item(item: SearchItem) -> dict[str, Any]:
    payload: dict[str, Any] = item.model_dump()
    return {key: _serialize_value(value) for key, value in payload.items()}


def _serialize_with_tokens(
    item: SearchItem,
    *,
    context: ArmtekSearchContext,
    repo: ArmtekCharacteristicsRepository,
) -> dict[str, Any]:
    api_token = generate_api_token(
        artid=item.artid, pin=item.pin, brand=item.brand, context=context
    )
    elizabeth_token = generate_characteristics_token(artid=item.artid)
    repo.register(elizabeth_token, item.artid)
    payload = serialize_search_item(item)
    payload["api_token"] = api_token
    payload["elizabeth_token"] = elizabeth_token
    return payload


@search_bp.route("/api/search", methods=["POST"])
@search_bp.route("/api/armtek/search", methods=["POST"])
def api_search() -> ResponseReturnValue:
    payload = request.get_json(silent=True) or {}
    if "query" not in payload:
        return jsonify({"error": "Поле query обязательно"}), 400

    raw_query = str(payload.get("query", ""))
    try:
        pin, brand = parse_query(raw_query)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    service = get_armtek_service()
    context = get_search_context()
    repo = get_characteristics_repo()
    try:
        item = service.get_main_search_item(pin=pin, brand=brand)
    except ArmtekError as exc:
        logger.exception("Armtek search failed: %s", exc)
        return jsonify({"error": "Не удалось выполнить запрос к Armtek"}), 500

    if item is None:
        return jsonify({"error": "Товар не найден"}), 404

    serialized = _serialize_with_tokens(item, context=context, repo=repo)
    return jsonify({"status": "ok", "items": [serialized]}), 200


__all__ = ["parse_query", "search_bp", "serialize_search_item"]
