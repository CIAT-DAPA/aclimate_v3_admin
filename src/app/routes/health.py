from flask import Blueprint, jsonify, request
from config import Config

bp = Blueprint("health", __name__)


def _validate_token():
    """Validate optional X-Health-Token header against configured HEALTH_TOKEN."""
    if not Config.HEALTH_TOKEN:
        return True
    return request.headers.get("X-Health-Token") == Config.HEALTH_TOKEN


@bp.route("/health", methods=["GET"])
def health_check():
    """Liveness probe - no external dependencies, immediate response."""
    if not _validate_token():
        return jsonify(None), 404
    return jsonify({"status": "ok"}), 200


@bp.route("/ready", methods=["GET"])
def readiness_check():
    """Readiness probe - verifies database connectivity."""
    if not _validate_token():
        return jsonify(None), 404

    checks = {"database": "disconnected"}
    try:
        import psycopg2

        dsn = Config.SQLALCHEMY_DATABASE_URI
        if dsn:
            conn = psycopg2.connect(dsn, connect_timeout=3)
            conn.close()
            checks["database"] = "connected"
    except Exception:
        checks["database"] = "disconnected"

    all_healthy = all(v == "connected" for v in checks.values())
    return jsonify(checks), 200 if all_healthy else 503