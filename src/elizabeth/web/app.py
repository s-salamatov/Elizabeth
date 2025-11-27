"""Flask application exposing a simple Armtek search UI."""

from __future__ import annotations

import atexit
import logging
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from flask import Flask, current_app, jsonify, render_template, request

from elizabeth.domain.armtek_models import ProductHtmlDetails, SearchItem
from elizabeth.infra.armtek.client import ArmtekClient
from elizabeth.infra.armtek.config import ArmtekConfig
from elizabeth.infra.armtek.exceptions import ArmtekError, ArmtekInteractiveLoginRequired
from elizabeth.infra.armtek.html_session import ArmtekHtmlSession, ArmtekSessionStore
from elizabeth.infra.armtek.interactive_login import (
    ArmtekInteractiveLoginConfig,
    ArmtekInteractiveLoginFlow,
)
from elizabeth.parsers.armtek_parser import ArmtekHtmlParser
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


def _get_armtek_html_parser() -> ArmtekHtmlParser:
    parser = current_app.config.get("armtek_html_parser")
    if parser is None:
        raise RuntimeError("Armtek HTML parser is not configured")
    return parser


def _get_interactive_login_flow() -> ArmtekInteractiveLoginFlow:
    flow = current_app.config.get("armtek_login_flow")
    if flow is None:
        raise RuntimeError("Armtek interactive login flow is not configured")
    return flow


def create_app(
    armtek_service: ArmtekService | None = None,
    html_parser: ArmtekHtmlParser | None = None,
    login_flow: ArmtekInteractiveLoginFlow | None = None,
) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    service = armtek_service or _build_default_service()
    app.config["armtek_service"] = service

    session_store = ArmtekSessionStore(Path("data/armtek_session.json"))
    html_session = ArmtekHtmlSession(store=session_store, base_url="https://etp.armtek.ru")
    login_config = ArmtekInteractiveLoginConfig()
    flow = login_flow or ArmtekInteractiveLoginFlow(config=login_config, store=session_store)
    parser = html_parser or ArmtekHtmlParser(session=html_session, login_flow=flow)

    app.config["armtek_html_parser"] = parser
    app.config["armtek_login_flow"] = flow

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

    @app.route("/api/product/details", methods=["POST"])
    def api_product_details():
        payload = request.get_json(silent=True) or {}
        artid = str(payload.get("artid", "")).strip()
        if not artid:
            return jsonify({"status": "error", "message": "Поле artid обязательно"}), 400

        parser = _get_armtek_html_parser()
        try:
            details: ProductHtmlDetails = parser.get_product_details(artid)
        except (ArmtekInteractiveLoginRequired, FileNotFoundError, ValueError):
            return jsonify(
                {
                    "status": "interactive_login_required",
                    "message": "Требуется авторизация или прохождение капчи на сайте Armtek",
                }
            ), 200
        except Exception as exc:  # pragma: no cover - unexpected path # pylint: disable=broad-exception-caught
            logger.exception("Failed to fetch product details: %s", exc)
            return jsonify({"status": "error", "message": "Не удалось получить данные товара"}), 500

        return jsonify({"status": "ok", "artid": details.artid, "image_url": details.image_url}), 200

    @app.route("/api/product/interactive-login", methods=["POST"])
    def api_product_interactive_login():
        payload = request.get_json(silent=True) or {}
        artid_value = payload.get("artid")
        artid = str(artid_value).strip() if artid_value else None
        flow = _get_interactive_login_flow()
        try:
            flow.run(artid=artid or None)
        except Exception as exc:  # pragma: no cover - unexpected path # pylint: disable=broad-exception-caught
            logger.exception("Interactive login failed: %s", exc)
            return jsonify({"status": "error", "message": "Не удалось выполнить интерактивный логин"}), 500

        return jsonify(
            {
                "status": "ok",
                "message": "Интерактивная авторизация выполнена. Повторите запрос получения данных товара.",
            }
        ), 200


# Compatibility entrypoint for `flask run`
def create_app_wsgi() -> Flask:
    return create_app()
