"""Flask application exposing a simple Armtek search UI."""

from __future__ import annotations

import atexit
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Any

from flask import Flask, current_app, jsonify, render_template, request

from elizabeth.domain.armtek_models import SearchItem
from elizabeth.infra.armtek.client import ArmtekClient
from elizabeth.infra.armtek.config import ArmtekConfig
from elizabeth.infra.armtek.exceptions import ArmtekError
from elizabeth.services.armtek_service import ArmtekService

logger = logging.getLogger(__name__)


def parse_query(query: str) -> tuple[str, str | None]:
    """
    Parse user input into article and optional brand.

    Examples:
    - "332101_KYB" -> ("332101", "KYB")
    - "332101 KYB" -> ("332101", "KYB")
    - "332101" -> ("332101", None)
    """

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


def _build_default_service() -> ArmtekService:
    config = ArmtekConfig(
        base_url=os.getenv("ARMTEK_BASE_URL", "https://ws.armtek.ru"),
        login=os.getenv("ARMTEK_LOGIN", "demo_login"),
        password=os.getenv("ARMTEK_PASSWORD", "demo_password"),
        timeout=float(os.getenv("ARMTEK_TIMEOUT", "5.0")),
    )

    client = ArmtekClient(config=config)
    return ArmtekService(
        client,
        vkorg=os.getenv("ARMTEK_VKORG", "4000"),
        kunnr_rg=os.getenv("ARMTEK_KUNNR_RG", "43411978"),
        program=os.getenv("ARMTEK_PROGRAM"),
        kunnr_za=os.getenv("ARMTEK_KUNNR_ZA"),
        incoterms=_parse_optional_int(os.getenv("ARMTEK_INCOTERMS")),
        vbeln=os.getenv("ARMTEK_VBELN"),
    )


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid integer for INCOTERMS: %s", value)
        return None


def _get_armtek_service() -> ArmtekService:
    service = current_app.config.get("armtek_service")
    if service is None:
        raise RuntimeError("Armtek service is not configured")
    return service


def create_app(armtek_service: ArmtekService | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    service = armtek_service or _build_default_service()
    app.config["armtek_service"] = service

    atexit.register(service.close)

    register_routes(app)
    return app


def register_routes(app: Flask) -> None:
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/api/search", methods=["POST"])
    def api_search():
        payload = request.get_json(silent=True) or {}
        if "query" not in payload:
            return jsonify({"error": "Поле query обязательно"}), 400

        raw_query = str(payload.get("query", ""))
        try:
            pin, brand = parse_query(raw_query)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        service = _get_armtek_service()
        try:
            item = service.get_main_search_item(pin=pin, brand=brand)
        except ArmtekError as exc:
            logger.exception("Armtek search failed: %s", exc)
            return jsonify({"error": "Не удалось выполнить запрос к Armtek"}), 500
        except Exception as exc:  # pragma: no cover - unexpected path # pylint: disable=broad-exception-caught
            logger.exception("Unexpected error during search: %s", exc)
            return jsonify({"error": "Внутренняя ошибка сервера"}), 500

        if item is None:
            return jsonify({"error": "Товар не найден"}), 404

        return jsonify(serialize_search_item(item)), 200


# Compatibility entrypoint for `flask run`
def create_app_wsgi() -> Flask:
    return create_app()
