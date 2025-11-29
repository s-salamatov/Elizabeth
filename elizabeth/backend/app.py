"""Flask application factory and dependency wiring for Elizabeth backend."""

from __future__ import annotations

import atexit
import os
from pathlib import Path

from flask import Flask, render_template
from flask.typing import ResponseReturnValue

from elizabeth.backend.api.characteristics_api import characteristics_bp
from elizabeth.backend.api.health_api import health_bp
from elizabeth.backend.api.search_api import search_bp
from elizabeth.backend.config import ArmtekConfig
from elizabeth.backend.repositories.characteristics_repository import (
    ArmtekCharacteristicsRepository,
    InMemoryArmtekCharacteristicsRepository,
)
from elizabeth.backend.services.armtek.client import ArmtekClient
from elizabeth.backend.services.armtek.service import ArmtekService
from elizabeth.backend.services.tokens import ArmtekSearchContext
from elizabeth.backend.utils.validation import parse_optional_int

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def _build_default_service() -> ArmtekService:
    """Construct a default ArmtekService from environment variables."""
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
        incoterms=parse_optional_int(os.getenv("ARMTEK_INCOTERMS")),
        vbeln=os.getenv("ARMTEK_VBELN"),
    )


def _build_default_search_context(
    service: ArmtekService | None = None,
) -> ArmtekSearchContext:
    """Create a default search context aligned with the configured service."""
    if service is not None:
        return service.search_context
    return ArmtekSearchContext(
        vkorg=os.getenv("ARMTEK_VKORG", "4000"),
        kunnr_rg=os.getenv("ARMTEK_KUNNR_RG", "43411978"),
        program=os.getenv("ARMTEK_PROGRAM"),
        kunnr_za=os.getenv("ARMTEK_KUNNR_ZA"),
        incoterms=parse_optional_int(os.getenv("ARMTEK_INCOTERMS")),
        vbeln=os.getenv("ARMTEK_VBELN"),
    )


def create_app(
    armtek_service: ArmtekService | None = None,
    search_context: ArmtekSearchContext | None = None,
    characteristics_repository: ArmtekCharacteristicsRepository | None = None,
) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / "templates"),
        static_folder=str(FRONTEND_DIR / "static"),
    )

    service = armtek_service or _build_default_service()
    app.config["armtek_service"] = service
    app.config["armtek_search_context"] = (
        search_context or _build_default_search_context(service)
    )
    app.config["characteristics_repo"] = (
        characteristics_repository or InMemoryArmtekCharacteristicsRepository()
    )
    app.config["BACKEND_BASE_URL"] = os.getenv("ELIZABETH_BACKEND_BASE_URL", "")
    app.config["EXTENSION_ALLOWED_ORIGIN"] = os.getenv(
        "ELIZABETH_EXTENSION_ALLOWED_ORIGIN", "*"
    )

    atexit.register(service.close)

    app.register_blueprint(search_bp)
    app.register_blueprint(characteristics_bp)
    app.register_blueprint(health_bp)

    @app.route("/", methods=["GET"])
    def index() -> ResponseReturnValue:
        """Render the main UI page."""
        return render_template("index.html")

    return app


def create_app_wsgi() -> Flask:
    """Entrypoint used by `flask run`."""
    return create_app()
