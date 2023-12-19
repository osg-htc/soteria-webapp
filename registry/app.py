"""
SOTERIA web application.
"""

import os
import pathlib
from typing import Any, Dict

import flask
import flask_assets  # type: ignore[import]

import registry.api.debug
import registry.api.harbor
import registry.api.v1
import registry.cli
import registry.public
import registry.util
import registry.website
from registry.cache import cache

__all__ = ["create_app"]

THIS_FILE = pathlib.Path(__file__)
INSTANCE_DIR = THIS_FILE.parent.parent / "instance"
LOG_DIR = INSTANCE_DIR / "log"


def load_config(app: flask.Flask) -> None:
    pyfiles = pathlib.Path(app.instance_path).glob("*.py")

    for p in sorted(pyfiles):
        app.config.from_pyfile(os.fspath(p))

    for key in [
        "FRESHDESK_API_KEY",
        "HARBOR_ADMIN_PASSWORD",
        "HARBOR_ADMIN_USERNAME",
        "REGISTRY_API_USERNAME",
        "REGISTRY_API_PASSWORD",
        "LDAP_BASE_DN",
        "LDAP_PASSWORD",
        "LDAP_URL",
        "LDAP_USERNAME",
        "SECRET_KEY",
        "WEBHOOKS_HARBOR_BEARER_TOKEN",
    ]:
        if (val := os.environ.get(key)) is not None:
            app.config[key] = val


def register_blueprints(app: flask.Flask) -> None:
    app.register_blueprint(registry.api.v1.bp, url_prefix="/api/v1")
    app.register_blueprint(registry.website.bp, url_prefix="/")
    app.register_blueprint(registry.cli.bp, cli_group="soteria")
    app.register_blueprint(registry.api.harbor.bp, url_prefix="/harbor")
    app.register_blueprint(registry.public.bp, url_prefix="/public")

    if app.config.get("SOTERIA_DEBUG"):
        app.register_blueprint(registry.api.debug.bp, url_prefix="/api/debug")


def define_assets(app: flask.Flask) -> None:
    assets = flask_assets.Environment(app)
    assets.url = app.static_url_path

    if app.config["DEBUG"]:
        assets.config["LIBSASS_STYLE"] = "nested"
        js_registration = flask_assets.Bundle(
            "js/registration.js",
            output="assets/js/registration.js",
        )
        js_account = flask_assets.Bundle(
            "js/account.js",
            output="assets/js/account.js",
        )
    else:
        ## Assume that a production webserver cannot write these files.
        assets.auto_build = False
        assets.cache = False
        assets.manifest = False

        assets.config["LIBSASS_STYLE"] = "compressed"
        js_registration = flask_assets.Bundle(
            "js/registration.js",
            filters="rjsmin",
            output="assets/js/registration.min.js",
        )
        js_account = flask_assets.Bundle(
            "js/account.js",
            filters="rjsmin",
            output="assets/js/account.min.js",
        )

    css = flask_assets.Bundle(
        "style.scss",
        filters="libsass",
        output="assets/css/style.css",
    )

    assets.register("soteria_js_registration", js_registration)
    assets.register("soteria_js_account", js_account)
    assets.register("soteria_css", css)


def add_context_processor(app: flask.Flask) -> None:
    @app.context_processor
    def add_globals() -> Dict[str, Any]:
        root_url = flask.request.root_url
        cookie_name = app.config["MOD_AUTH_OPENIDC_SESSION_COOKIE_NAME"]
        cookie = flask.request.cookies.get(cookie_name)

        flask.g.has_session_cookie = bool(cookie)
        flask.g.logout_url = f"{root_url}callback?logout={root_url}"

        return {
            "is_researcher": registry.util.is_soteria_researcher(),
            "is_registered": registry.util.is_registered(),
            "is_admin": registry.util.is_soteria_admin(),
            "has_starter_project": registry.util.has_starter_project(),
        }


def create_app() -> flask.Flask:
    registry.util.configure_logging(LOG_DIR / "soteria.log")

    app = flask.Flask(
        __name__.split(".", maxsplit=1)[0],
        instance_path=os.fspath(INSTANCE_DIR),
        instance_relative_config=True,
    )

    load_config(app)
    register_blueprints(app)
    define_assets(app)
    add_context_processor(app)

    cache.init_app(app)

    app.logger.info("Created and configured app!")

    return app


# Use to test locally
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=True, port=9876)
