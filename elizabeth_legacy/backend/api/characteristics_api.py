from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify, request
from flask.typing import ResponseReturnValue

from elizabeth.backend.api.deps import get_characteristics_repo
from elizabeth.backend.utils.validation import parse_optional_str

characteristics_bp = Blueprint("characteristics_api", __name__)


def _with_cors_headers(response: Response) -> Response:
    origin = current_app.config.get("EXTENSION_ALLOWED_ORIGIN", "*")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@characteristics_bp.after_request
def add_cors_headers(response: Response) -> Response:
    return _with_cors_headers(response)


@characteristics_bp.route("/api/armtek/characteristics", methods=["OPTIONS"])
def api_characteristics_options() -> ResponseReturnValue:
    response = current_app.make_default_options_response()
    return _with_cors_headers(response)


@characteristics_bp.route("/api/armtek/characteristics", methods=["POST"])
def api_characteristics_callback() -> ResponseReturnValue:
    payload = request.get_json(silent=True) or {}
    try:
        token = parse_optional_str(payload.get("token")) or ""
        artid = parse_optional_str(payload.get("artid"))
        image_url = parse_optional_str(payload.get("image_url"))
        weight = parse_optional_str(payload.get("weight"))
        length = parse_optional_str(payload.get("length"))
        height = parse_optional_str(payload.get("height"))
        width = parse_optional_str(payload.get("width"))
        analog_code = parse_optional_str(payload.get("analog_code"))
    except ValueError:
        return (
            _with_cors_headers(
                jsonify({"status": "error", "message": "Invalid payload"}),
            ),
            400,
        )

    if not token:
        return (
            _with_cors_headers(
                jsonify({"status": "error", "message": "Invalid payload"})
            ),
            400,
        )

    repo = get_characteristics_repo()
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


@characteristics_bp.route("/api/armtek/characteristics", methods=["GET"])
def api_characteristics_get() -> ResponseReturnValue:
    token = str(request.args.get("token", "")).strip()
    if not token:
        return _with_cors_headers(jsonify({"status": "not_found"})), 200

    repo = get_characteristics_repo()
    record = repo.get_by_token(token)
    if record is None:
        return _with_cors_headers(jsonify({"status": "not_found"})), 200

    if not record.ready:
        return _with_cors_headers(jsonify({"status": "pending"})), 200

    return (
        _with_cors_headers(
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
                    "received_at": (
                        record.received_at.isoformat() if record.received_at else None
                    ),
                }
            )
        ),
        200,
    )


__all__ = ["characteristics_bp"]
