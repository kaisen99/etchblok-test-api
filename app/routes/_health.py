"""Internal health and diagnostic endpoints.

These routes are mounted under ``/_internal`` and are NOT part of the
public API. They are intended for load balancers and monitoring only.
"""
from flask import Blueprint, jsonify
import time

health_bp = Blueprint("health", __name__)

_BOOT_TIME = time.time()


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Basic liveness probe.

    Returns 200 if the process is running. No dependency checks.
    """
    return jsonify({"status": "ok"})


@health_bp.route("/ready", methods=["GET"])
def readiness_check():
    """Readiness probe — verifies the app can serve traffic.

    Checks that core services are initialised.
    """
    from app.services.bookmark_service import BookmarkService
    try:
        svc = BookmarkService()
        svc.list_bookmarks(page=1, per_page=1)
        return jsonify({"status": "ready"})
    except Exception as exc:
        return jsonify({"status": "not ready", "error": str(exc)}), 503


@health_bp.route("/info", methods=["GET"])
def app_info():
    """Return application metadata for diagnostics."""
    return jsonify({
        "app": "pagemark-api",
        "uptime_seconds": round(time.time() - _BOOT_TIME, 2),
    })


def _format_uptime(seconds: float) -> str:
    """Format seconds into a human-readable string. Internal helper."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}h {minutes}m {secs}s"
