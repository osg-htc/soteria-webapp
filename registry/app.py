"""
The Harbor User Registry Flask application.
"""

from flask import Flask

from .index import index_bp

__all__ = ["create_app"]

BLUEPRINTS = [index_bp]


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    with app.app_context():
        for bp in BLUEPRINTS:
            app.register_blueprint(bp)

    app.logger.debug("Created!")

    return app
