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
from registry.util import get_fresh_desk_api

from .forms import ResearcherApprovalForm, CreateProjectForm

__all__ = ["bp"]

bp = flask.Blueprint("website", __name__)


@bp.route("/account")
def index():
    user = {
        "name": registry.util.get_name() or "<not available>",
        "orcid_id": registry.util.get_orcid_id() or "<not available>",
        "email": registry.util.get_email() or "<not available>",
        'status': registry.util.get_status() or "<not available>",
    }

    return flask.render_template(
        "/user/account.html",
        user=user,
        is_researcher=registry.util.is_soteria_researcher(),
        is_member=registry.util.is_soteria_member(),
        is_affiliate=registry.util.is_soteria_affiliate(),
        registry_url=flask.current_app.config['REGISTRY_HOMEPAGE_URL']
    )


@bp.route("/researcher-registration", methods=["GET", "POST"])
def researcher_registration() -> flask.Response:
    researcher_form = ResearcherApprovalForm(flask.request.form)

    html = None
    if researcher_form.validate_on_submit():
        ticket_created = researcher_form.submit_request()
        html = flask.render_template(
            "researcher-registration.html",
            form=researcher_form,
            ticket_created=ticket_created
        )

    else:
        html = flask.render_template("researcher-registration.html", form=researcher_form)

    return flask.make_response(html)

@bp.route("/projects/create", methods=["GET", "POST"])
def create_project() -> flask.Response:
    projects_creation_form = CreateProjectForm(flask.request.form)

    if projects_creation_form.validate_on_submit():
        project_created = projects_creation_form.submit_request()
        html = flask.render_template(
            "/user/create-project.html",
            form=projects_creation_form,
            project_created=project_created
        )

    else:
        html = flask.render_template("/user/create-project.html", form=projects_creation_form)

    return flask.make_response(html)


@bp.route("/status")
def status() -> flask.Response:
    """
    Checks the application's health and status.
    """
    return flask.make_response("No-op ok!")


@bp.route("/projects")
def user_projects():
    return flask.render_template(
        "/user/projects.html",
        is_researcher=registry.util.is_soteria_researcher(),
        harbor_url=flask.current_app.config['HARBOR_HOMEPAGE_URL']
    )


@bp.route("/<page>")
@bp.route("/", defaults={
    "page": "index"
})
def show(page: str) -> flask.Response:
    """
    Renders pages that do not require any special handling.
    """
    try:
        render = flask.render_template(f"{page}.html")
    except jinja2.TemplateNotFound:
        flask.abort(404)
    return flask.make_response(render)
