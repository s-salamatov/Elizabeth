from __future__ import annotations

from flask import Blueprint, jsonify

health_bp = Blueprint("health_api", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


__all__ = ["health_bp"]
