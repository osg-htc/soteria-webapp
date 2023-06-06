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
from registry.util import is_soteria_affiliate, has_organizational_identity
from registry.security import researcher_required, registration_required

from .forms import CreateProjectForm, ResearcherApprovalForm, CreateStarterProjectForm

__all__ = ["bp"]

bp = flask.Blueprint("website", __name__)


def affiliate_required(f):
    def wrapper():
        if not is_soteria_affiliate():
            return flask.make_response(flask.render_template("error.html"), 403)

        return f()

    return wrapper



@bp.route("/account")
def index():
    user = {
        "name": registry.util.get_name() or "<not available>",
        "orcid_id": registry.util.get_orcid_id() or "<not available>",
        "email": registry.util.get_email() or "<not available>",
        "status": registry.util.get_status() or "<not available>",
    }

    starter_project = registry.util.get_admin_harbor_api().get_project(registry.util.get_starter_project_name())
    has_starter_project = not ('errors' in starter_project and starter_project['errors'][0]['code'] == 'NOT_FOUND')

    return flask.render_template(
        "/user/account.html",
        user=user,
        is_researcher=registry.util.is_soteria_researcher(),
        is_member=registry.util.is_soteria_member(),
        is_affiliate=registry.util.is_soteria_affiliate(),
        is_registered=registry.util.is_registered(),
        has_starter_project=has_starter_project,
        registry_url=flask.current_app.config["REGISTRY_HOMEPAGE_URL"],
    )


@bp.route("/researcher-registration", methods=["GET", "POST"])
@registration_required
def researcher_registration() -> flask.Response:
    researcher_form = ResearcherApprovalForm(flask.request.form)

    html = None
    if researcher_form.validate_on_submit():
        ticket_created = researcher_form.submit_request()
        html = flask.render_template(
            "user/researcher-registration.html",
            form=researcher_form,
            ticket_created=ticket_created,
        )

    else:
        html = flask.render_template(
            "user/researcher-registration.html", form=researcher_form
        )

    return flask.make_response(html)


@bp.route("/projects/create", methods=["GET", "POST"])
@researcher_required
def create_project() -> flask.Response:
    projects_creation_form = CreateProjectForm(flask.request.form)

    if projects_creation_form.validate_on_submit():
        project_created = projects_creation_form.submit_request()
        html = flask.render_template(
            "/user/create-project.html",
            form=projects_creation_form,
            project_created=project_created,
        )

    else:
        html = flask.render_template(
            "/user/create-project.html", form=projects_creation_form
        )

    return flask.make_response(html)

@bp.route("/projects/starter", methods=["GET", "POST"])
@registration_required
def create_starter_project() -> flask.Response:
    projects_creation_form = CreateStarterProjectForm(flask.request.form)

    if projects_creation_form.validate_on_submit():
        project_created = projects_creation_form.submit_request()
        html = flask.render_template(
            "/user/create-starter.html",
            form=projects_creation_form,
            project_created=project_created,
        )

    else:
        html = flask.render_template(
            "/user/create-starter.html", form=projects_creation_form
        )

    return flask.make_response(html)

@bp.route("/status")
def status() -> flask.Response:
    """
    Checks the application's health and status.
    """
    return flask.make_response("No-op ok!")


@bp.route("/projects")
@registration_required
def user_projects():
    return flask.render_template(
        "/user/projects.html",
        is_researcher=registry.util.is_soteria_researcher(),
        harbor_url=flask.current_app.config["HARBOR_HOMEPAGE_URL"],
    )


@bp.route("/registration")
def registration():
    return flask.render_template(
        "/registration.html",
        has_organizational_identity=has_organizational_identity()
    )


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
