"""Pagemark — bookmark management API."""
from flask import Flask

from app.config import DevelopmentConfig
from app.routes.bookmarks import bookmarks_bp
from app.routes.tags import tags_bp
from app.routes.collections import collections_bp
from app.routes._health import health_bp


def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory.

    Creates and configures the Flask application, registers blueprints,
    and initialises the in-memory database.

    Args:
        config_class: Configuration class to use. Defaults to DevelopmentConfig.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(bookmarks_bp, url_prefix="/api/bookmarks")
    app.register_blueprint(tags_bp, url_prefix="/api/tags")
    app.register_blueprint(collections_bp, url_prefix="/api/collections")
    app.register_blueprint(health_bp, url_prefix="/_internal")

    return app
