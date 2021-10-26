"""
SOTERIA website.
"""

# NOTE: Each route is handled by the first function declared for it. Thus,
# the default/generic ``show`` handler below must be declared last in this
# file and the blueprint registered last in ``registry.app``.

import json
import pathlib
from .forms import ResearcherApprovalForm
import flask
import jinja2
from registry.util import get_fresh_desk_api

__all__ = ["bp"]

bp = flask.Blueprint("website", __name__)

@bp.route("/account")
def index() -> flask.Response:

    try:
        sample_data_path = (
            pathlib.Path(flask.current_app.instance_path).resolve().parent
            / "data-templates/TEMPLATE-user.json"
        )

        flask.current_app.logger.debug(sample_data_path)

        with open(sample_data_path) as fp:
            user = json.load(fp)
    except:
        user = {
            "name": "First Last",
            "orcid_id": 11235813,
            "status": "Affiliate/Member/Researcher",
            "email": "hello@world.org",
            "days_remaining": "Days Left (int)",
        }


    html = flask.render_template("account.html", user=user)
    return flask.make_response(html)

@bp.route("/researcher-registration", methods=["GET", "POST"])
def researcher_registration() -> flask.Response:
    researcher_form = ResearcherApprovalForm(flask.request.form)

    if researcher_form.validate_on_submit():
        researcher_form.submit_request()

    html = flask.render_template("researcher-registration.html", form=researcher_form)
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
