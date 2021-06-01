"""
Web application for managing the users of a Harbor instance.
"""

from flask import Flask

from .account import account_bp
from .api.v1 import api_bp
from .debug import debugging_bp
from .index import index_bp

__all__ = ["create_app"]


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.register_blueprint(index_bp, url_prefix="/")
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    app.register_blueprint(debugging_bp, url_prefix="/debug")

    app.logger.debug("Created!")

    return app
