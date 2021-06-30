"""
Web application for managing the users of a Harbor instance.
"""

import logging.config
import os
import glob
from pathlib import Path

from flask import Flask
from flask_assets import Environment, Bundle

from .registration import registration_bp
from .account import account_bp
from .api.test import api_bp_test
from .api.v1 import api_bp
from .debug import debugging_bp
from .index import index_bp

__all__ = ["create_app"]

THIS_FILE = Path(__file__)
INSTANCE_DIR = THIS_FILE.parent.parent / "instance"
LOG_DIR = INSTANCE_DIR / "log"

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(module)s:%(lineno)s ~ %(message)s"


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {"format": LOG_FORMAT},
            },
            "handlers": {
                "stream": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "default",
                    "filename": LOG_DIR / "wsgi.log",
                    "backupCount": 5,
                    "maxBytes": 10 * 1024 * 1024,  # 10 MiB
                },
            },
            "root": {"level": "DEBUG", "handlers": ["stream", "file"]},
        }
    )


def load_config(app: Flask) -> None:
    pyfiles = Path(app.instance_path).glob("*.py")

    for p in sorted(pyfiles):
        app.config.from_pyfile(p)

    for key in [
        "HARBOR_ADMIN_USERNAME",
        "HARBOR_ADMIN_PASSWORD",
        "HARBOR_ROBOT_USERNAME",
        "HARBOR_ROBOT_PASSWORD",
    ]:
        val = os.environ.get(key)

        if val:
            app.config[key] = val


def create_app() -> Flask:
    setup_logging()

    app = Flask(__name__, instance_relative_config=True)

    # Compile the static files
    assets = Environment(app)
    assets.url = app.static_url_path

    # Set-up compression based on env
    if app.config["DEBUG"]:
        assets.config["LIBSASS_STYLE"] = "nested"
        js = Bundle('main.js', 'bootstrap.js', output='gen/packed.js')
    else:
        assets.config["LIBSASS_STYLE"] = "compressed"
        js = Bundle('main.js', 'bootstrap.js', filters="jsmin", output='gen/packed.js')

    #Scss
    assets.config['LIBSASS_INCLUDES'] = glob.glob("./registry/static/*/**")
    scss = Bundle('style.scss', filters='libsass',  output='gen/style.css')
    assets.register('scss_all', scss)

    #js
    assets.register('js_all', js)

    load_config(app)

    app.register_blueprint(index_bp, url_prefix="/")
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(registration_bp, url_prefix="/registration")
    app.register_blueprint(api_bp_test, url_prefix="/api/test")
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    if app.config.get("REGISTRY_DEBUG"):
        app.register_blueprint(debugging_bp, url_prefix="/debug")

    app.logger.debug("Created!")

    return app
