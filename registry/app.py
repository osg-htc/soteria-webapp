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
        "LDAP_URL",
        "LDAP_USERNAME",
        "LDAP_PASSWORD",
        "LDAP_BASE_DN",
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

        # Early "development" versions of the application:
        #
        #   1. Put various pages at "/<page>/"
        #   2. Redirected "/<page>" to "/<page>/"
        #
        # Some browsers have cached the redirect, which is no longer correct.

        @app.before_request
        def strip_trailing_slash_from_path():
            rp = flask.request.path

            if rp in [
                "/about/",
                "/account/",
                "/registration/",
            ]:
                return flask.redirect(rp[:-1], code=302)
            return None


def define_assets(app: flask.Flask) -> None:
    """
    Defines the application's CSS and JavaScript assets.
    """

    assets = flask_assets.Environment(app)
    assets.url = app.static_url_path

    if app.config["DEBUG"]:
        assets.config["LIBSASS_STYLE"] = "nested"
        js = flask_assets.Bundle(
            "bootstrap.js",
            "registration.js",
            output="assets/soteria.js",
        )
    else:
        ## Assume that a production webserver cannot write these files.
        assets.auto_build = False
        assets.cache = False
        assets.manifest = False

        assets.config["LIBSASS_STYLE"] = "compressed"
        js = flask_assets.Bundle(
            "bootstrap.js",
            "registration.js",
            filters="rjsmin",
            output="assets/soteria.min.js",
        )

    scss = flask_assets.Bundle("style.scss", filters="libsass", output="assets/style.css")

    assets.register("js_all", js)
    assets.register("scss_all", scss)


def add_context_processors(app: flask.Flask) -> None:
    @app.context_processor
    def populate_context() -> Dict[str, Any]:
        root_url = flask.request.root_url

        cookie_name = app.config.get("MOD_AUTH_OPENIDC_SESSION_COOKIE_NAME")
        cookie = flask.request.cookies.get(cookie_name)

        flask.g.has_session_cookie = bool(cookie)
        flask.g.logout_url = f"{root_url}callback?logout={root_url}"

        def get_idp_name() -> Optional[str]:
            return flask.request.environ.get("OIDC_CLAIM_idp_name")

        def get_soteria_enrollment_url() -> Optional[str]:
            if registry.util.has_organizational_identity():
                return app.config.get(
                    "SOTERIA_ENROLLMENT_FOR_EXISTING_ORG_ID_URL"
                )
            return app.config.get("SOTERIA_ENROLLMENT_FOR_NEW_ORG_ID_URL")

        return {
            "get_idp_name": get_idp_name,
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
    add_context_processors(app)

    app.logger.debug("Created app!")

    return app
