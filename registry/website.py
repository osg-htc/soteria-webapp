"""
SOTERIA website.
"""

# NOTE: Each route is handled by the first function declared for it. Thus,
# the default/generic ``show`` handler below must be declared last in this
# file and the blueprint registered last in ``registry.app``.

import json
import pathlib

import flask
import jinja2

import registry.util

__all__ = ["bp"]

bp = flask.Blueprint("website", __name__)


@bp.route("/account")
def index() -> flask.Response:
    user = {
        "name": registry.util.get_name() or "<not available>",
        "orcid_id": registry.util.get_orcid_id() or "<not available>",
    }

    html = flask.render_template("account.html", user=user)
    return flask.make_response(html)


@bp.route("/status")
def status() -> flask.Response:
    """
    Checks the application's health and status.
    """
    return flask.make_response("No-op ok!")


@bp.route("/<page>")
@bp.route("/", defaults={"page": "index"})
def show(page: str) -> flask.Response:
    """
    Renders pages that do not require any special handling.
    """
    try:
        render = flask.render_template(f"{page}.html")
    except jinja2.TemplateNotFound:
        flask.abort(404)
    return flask.make_response(render)
