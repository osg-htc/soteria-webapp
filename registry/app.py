"""
Web application for managing the users of a Harbor instance.
"""

from pathlib import Path

from flask import Flask

from .account import account_bp
from .api.v1 import api_bp
from .debug import debugging_bp
from .index import index_bp

__all__ = ["create_app"]


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    instance_config = Path(app.instance_path) / "config.py"

    if instance_config.exists():
        app.config.from_pyfile(instance_config)

    app.register_blueprint(index_bp, url_prefix="/")
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    if app.config.get("REGISTRY_DEBUG"):
        app.register_blueprint(debugging_bp, url_prefix="/debug")

    app.logger.debug("Created!")

    return app
