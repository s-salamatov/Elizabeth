"""Flask application exposing Armtek search UI with browser-extension callbacks."""

from __future__ import annotations

import atexit
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Any

from flask import Flask, current_app, jsonify, render_template, request

from elizabeth.domain.armtek_models import SearchItem
from elizabeth.domain.tokens import ArmtekSearchContext, generate_api_token, generate_characteristics_token
from elizabeth.infra.armtek.client import ArmtekClient
from elizabeth.infra.armtek.config import ArmtekConfig
from elizabeth.infra.armtek.exceptions import ArmtekError
from elizabeth.services.armtek_service import ArmtekService
from elizabeth.services.characteristics_repository import (
    ArmtekCharacteristicsRepository,
    InMemoryArmtekCharacteristicsRepository,
)

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


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid integer for INCOTERMS: %s", value)
        return None


def _parse_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Expected string or null")
    cleaned = value.strip()
    return cleaned or None


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


def _build_default_search_context(service: ArmtekService | None = None) -> ArmtekSearchContext:
    if service is not None:
        return service.search_context
    return ArmtekSearchContext(
        vkorg=os.getenv("ARMTEK_VKORG", "4000"),
        kunnr_rg=os.getenv("ARMTEK_KUNNR_RG", "43411978"),
        program=os.getenv("ARMTEK_PROGRAM"),
        kunnr_za=os.getenv("ARMTEK_KUNNR_ZA"),
        incoterms=_parse_optional_int(os.getenv("ARMTEK_INCOTERMS")),
        vbeln=os.getenv("ARMTEK_VBELN"),
    )


def _get_armtek_service() -> ArmtekService:
    service = current_app.config.get("armtek_service")
    if service is None:
        raise RuntimeError("Armtek service is not configured")
    return service


def _get_search_context() -> ArmtekSearchContext:
    context = current_app.config.get("armtek_search_context")
    if context is None:
        raise RuntimeError("Armtek search context is not configured")
    return context


def _get_characteristics_repo() -> ArmtekCharacteristicsRepository:
    repo = current_app.config.get("characteristics_repo")
    if repo is None:
        raise RuntimeError("Characteristics repository is not configured")
    return repo


def _with_cors_headers(response):
    if request.path.startswith("/api/armtek/characteristics"):
        origin = current_app.config.get("EXTENSION_ALLOWED_ORIGIN", "*")
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def create_app(
    armtek_service: ArmtekService | None = None,
    search_context: ArmtekSearchContext | None = None,
    characteristics_repository: ArmtekCharacteristicsRepository | None = None,
) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    service = armtek_service or _build_default_service()
    app.config["armtek_service"] = service
    app.config["armtek_search_context"] = search_context or _build_default_search_context(service)
    app.config["characteristics_repo"] = characteristics_repository or InMemoryArmtekCharacteristicsRepository()
    # Use explicit base URL if provided, otherwise default to same-origin (relative paths).
    app.config["BACKEND_BASE_URL"] = os.getenv("ELIZABETH_BACKEND_BASE_URL", "")
    app.config["EXTENSION_ALLOWED_ORIGIN"] = os.getenv("ELIZABETH_EXTENSION_ALLOWED_ORIGIN", "*")

    atexit.register(service.close)

    register_routes(app)

    @app.after_request
    def add_cors_headers(response):  # type: ignore[override]
        return _with_cors_headers(response)

    return app


def _serialize_with_tokens(
    item: SearchItem, *, context: ArmtekSearchContext, repo: ArmtekCharacteristicsRepository
) -> dict[str, Any]:
    api_token = generate_api_token(artid=item.artid, pin=item.pin, brand=item.brand, context=context)
    elizabeth_token = generate_characteristics_token(artid=item.artid)
    repo.register(elizabeth_token, item.artid)
    payload = serialize_search_item(item)
    payload["api_token"] = api_token
    payload["elizabeth_token"] = elizabeth_token
    return payload


def register_routes(app: Flask) -> None:
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/api/search", methods=["POST"])
    @app.route("/api/armtek/search", methods=["POST"])
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
        context = _get_search_context()
        repo = _get_characteristics_repo()
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

        serialized = _serialize_with_tokens(item, context=context, repo=repo)
        return jsonify({"status": "ok", "items": [serialized]}), 200

    @app.route("/api/armtek/characteristics", methods=["OPTIONS"])
    def api_characteristics_options():
        response = current_app.make_default_options_response()
        return _with_cors_headers(response)

    @app.route("/api/armtek/characteristics", methods=["POST"])
    def api_characteristics_callback():
        payload = request.get_json(silent=True) or {}
        try:
            token = _parse_optional_str(payload.get("token")) or ""
            artid = _parse_optional_str(payload.get("artid"))
            image_url = _parse_optional_str(payload.get("image_url"))
            weight = _parse_optional_str(payload.get("weight"))
            length = _parse_optional_str(payload.get("length"))
            height = _parse_optional_str(payload.get("height"))
            width = _parse_optional_str(payload.get("width"))
            analog_code = _parse_optional_str(payload.get("analog_code"))
        except ValueError:
            return _with_cors_headers(
                jsonify({"status": "error", "message": "Invalid payload"}),
            ), 400

        if not token:
            return _with_cors_headers(jsonify({"status": "error", "message": "Invalid payload"})), 400

        repo = _get_characteristics_repo()
        repo.save(
            token=token,
            artid=artid,
            image_url=image_url,
            weight=weight,
            length=length,
            height=height,
            width=width,
            analog_code=analog_code,
        )

        return _with_cors_headers(jsonify({"status": "ok"})), 200

    @app.route("/api/armtek/characteristics", methods=["GET"])
    def api_characteristics_get():
        token = str(request.args.get("token", "")).strip()
        if not token:
            return _with_cors_headers(jsonify({"status": "not_found"})), 200

        repo = _get_characteristics_repo()
        record = repo.get_by_token(token)
        if record is None:
            return _with_cors_headers(jsonify({"status": "not_found"})), 200

        if not record.ready:
            return _with_cors_headers(jsonify({"status": "pending"})), 200

        return _with_cors_headers(
            jsonify(
                {
                    "status": "ok",
                    "token": record.token,
                    "artid": record.artid,
                    "image_url": record.image_url,
                    "weight": record.weight,
                    "length": record.length,
                    "height": record.height,
                    "width": record.width,
                    "analog_code": record.analog_code,
                    "received_at": record.received_at.isoformat() if record.received_at else None,
                }
            )
        ), 200


# Compatibility entrypoint for `flask run`
def create_app_wsgi() -> Flask:
    return create_app()
