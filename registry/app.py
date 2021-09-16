"""
SOTERIA web application.
"""

import os
import pathlib
from typing import Any, Callable, Dict, Optional

import flask
import flask_assets  # type: ignore[import]

import registry.api.debug
import registry.api.v1
import registry.util
import registry.website
from registry.api.test import api_bp_test
from registry.repositories import repositories_bp
from registry.repository import repository_bp

__all__ = ["create_app"]

THIS_FILE = pathlib.Path(__file__)
INSTANCE_DIR = THIS_FILE.parent.parent / "instance"
LOG_DIR = INSTANCE_DIR / "log"


def load_config(app: flask.Flask) -> None:
    """
    Loads the application's configuration.
    """

    pyfiles = pathlib.Path(app.instance_path).glob("*.py")

    for p in sorted(pyfiles):
        app.config.from_pyfile(os.fspath(p))

    for key in [
        "HARBOR_ADMIN_USERNAME",
        "HARBOR_ADMIN_PASSWORD",
        "HARBOR_ROBOT_USERNAME",
        "HARBOR_ROBOT_PASSWORD",
    ]:
        val = os.environ.get(key)

        if val is not None:
            app.config[key] = val


def register_blueprints(app: flask.Flask) -> None:
    """
    Registers the application's blueprints.
    """

    app.register_blueprint(repositories_bp, url_prefix="/repositories")
    app.register_blueprint(repository_bp, url_prefix="/repository")
    app.register_blueprint(api_bp_test, url_prefix="/api/test")
    app.register_blueprint(registry.api.v1.bp, url_prefix="/api/v1")
    app.register_blueprint(registry.website.bp, url_prefix="/")

    if app.config.get("SOTERIA_DEBUG"):
        app.register_blueprint(registry.api.debug.bp, url_prefix="/debug")


def define_assets(app: flask.Flask) -> None:
    """
    Defines the application's CSS and JavaScript assets.
    """

    assets = flask_assets.Environment(app)
    assets.url = app.static_url_path

    if app.config["DEBUG"]:
        assets.config["LIBSASS_STYLE"] = "nested"
        js = flask_assets.Bundle("main.js", "bootstrap.js", output="gen/packed.js")
    else:
        ## Assume that a production webserver cannot write these files.

        assets.auto_build = False
        assets.cache = False
        assets.manifest = False

        assets.config["LIBSASS_STYLE"] = "compressed"
        js = flask_assets.Bundle(
            "main.js", "bootstrap.js", filters="rjsmin", output="gen/packed.js"
        )

    scss = flask_assets.Bundle("style.scss", filters="libsass", output="gen/style.css")

    assets.register("js_all", js)
    assets.register("scss_all", scss)


def add_context(app: flask.Flask) -> None:
    @app.context_processor
    def utility_processor() -> Dict[str, Callable[[], Any]]:
        def get_idp_name() -> Optional[str]:
            return flask.request.environ.get("OIDC_CLAIM_idp_name")

        def get_path() -> str:
            return flask.request.url_root + "callback?logout=" + flask.request.url_root

        def get_soteria_enrollment_url() -> Optional[str]:
            if registry.util.has_organizational_identity():
                return app.config.get("SOTERIA_ENROLLMENT_FOR_EXISTING_ORG_ID_URL")
            return app.config.get("SOTERIA_ENROLLMENT_FOR_NEW_ORG_ID_URL")

        return {
            "get_idp_name": get_idp_name,
            "get_path": get_path,
            "get_soteria_enrollment_url": get_soteria_enrollment_url,
        }


def create_app() -> flask.Flask:
    """
    Creates the main application.
    """

    registry.util.configure_logging(LOG_DIR / "soteria.log")

    app = flask.Flask(
        __name__.split(".", maxsplit=1)[0],
        instance_path=os.fspath(INSTANCE_DIR),
        instance_relative_config=True,
    )

    load_config(app)
    register_blueprints(app)
    define_assets(app)
    add_context(app)

    app.logger.debug("Created app!")

    return app
