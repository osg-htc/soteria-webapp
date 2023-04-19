"""
SOTERIA API version 1.
"""

import dataclasses
import datetime
from typing import Any, Dict, List, Optional, Union

import flask
from typing_extensions import Literal

import registry.util
from registry.cache import cache
from registry.harbor import HarborRoleID

__all__ = ["bp"]

bp = flask.Blueprint("api_v1", __name__)


@dataclasses.dataclass
class UserObject:
    is_soteria_affiliate: bool
    is_soteria_member: bool
    is_soteria_researcher: bool

    harbor_id: Optional[str] = None
    harbor_username: Optional[str] = None
    orcid_id: Optional[str] = None


@dataclasses.dataclass
class ProjectObject:
    harbor_id: Optional[str] = None
    harbor_name: Optional[str] = None


@dataclasses.dataclass
class MiscellaneousObject:
    blob: str


DataObject = Union[UserObject, Dict[str, Any]]


@dataclasses.dataclass
class BaseResponse:
    status: Literal["ok", "errors"]


@dataclasses.dataclass
class SoteriaResponse(BaseResponse):
    data: DataObject


@dataclasses.dataclass
class ErrorResponse(BaseResponse):
    errors: Union[Any, List[Dict[Literal["code", "message"], str]]]


def make_ok_response(data: DataObject) -> flask.Response:
    response = SoteriaResponse("ok", data)
    return flask.make_response(dataclasses.asdict(response))


def make_error_response(code: int, message: str) -> flask.Response:
    response = ErrorResponse(
        "errors", [{"code": str(code), "message": message}]
    )
    if 400 <= code < 600:
        return flask.make_response(dataclasses.asdict(response), code)
    return flask.make_response(dataclasses.asdict(response))


def make_errors_response(errors: Any) -> flask.Response:
    response = ErrorResponse("errors", errors)
    return flask.make_response(dataclasses.asdict(response), 500)


@bp.after_request
def disable_caching(resp: flask.Response) -> flask.Response:
    """
    Sets the response's headers to prevent storing responses at the client.
    """
    resp.headers["Cache-Control"] = "no-store"

    return resp


@bp.route("/ping", methods=["GET", "POST", "PUT", "DELETE"])
def ping():
    """
    Confirms that the API is functioning at some minimal level.
    """
    return make_ok_response({"message": "pong!"})


@bp.route("/version")
def version() -> flask.Response:
    version_string = flask.current_app.config.get(
        "SOTERIA_VERSION", "<not set>"
    )

    return make_ok_response({"version": version_string})


@bp.route("/users/<user_id>")
def get_user(user_id: str) -> flask.Response:
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    harbor_user = registry.util.get_harbor_user() or {}

    user = UserObject(
        is_soteria_affiliate=registry.util.is_soteria_affiliate(),
        is_soteria_member=registry.util.is_soteria_member(),
        is_soteria_researcher=registry.util.is_soteria_researcher(),
        harbor_id=harbor_user.get("user_id"),
        harbor_username=harbor_user.get("username"),
        orcid_id=registry.util.get_orcid_id(),
    )

    return make_ok_response(user)


@bp.route("/users/<user_id>/enrollment")
def check_user_enrollment(user_id: str):
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    enrolled = registry.util.has_organizational_identity()
    idp_name = registry.util.get_idp_name()

    data = {"verified": bool(enrolled), "idp_name": idp_name}

    return make_ok_response(data)


@bp.route("/users/<user_id>/harbor_id")
def check_user_harbor_id(user_id: str):
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    flask.current_app.logger.info("Subiss Below:")
    flask.current_app.logger.info(registry.util.get_subiss())

    cache.delete_memoized(
        registry.util.get_harbor_user_by_subiss, registry.util.get_subiss()
    )
    harbor_user = registry.util.get_harbor_user()

    username = harbor_user["username"] if harbor_user else None

    data = {
        "verified": bool(username),
        "username": username,
        "harbor": {"name": flask.current_app.config["HARBOR_NAME"]},
    }

    return make_ok_response(data)


@bp.route("/users/<user_id>/orcid_id")
def verify_orcid(user_id: str):
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    orcid_id = registry.util.get_orcid_id()

    data = {"verified": bool(orcid_id), "orcid_id": orcid_id}

    return make_ok_response(data)


@bp.route("/users/<user_id>/projects")
def get_projects(user_id: str):
    """
    Lists all current users related projects
    """
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    return flask.jsonify(registry.util.get_harbor_projects())


@bp.route("/users/<user_id>/starter_project", methods=["POST"])
def create_user_starter_project(user_id: str):
    """
    Creates a "starter" repositories in Harbor for the current user.
    """
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    api = registry.util.get_admin_harbor_api()
    errors = []

    orcid_id = registry.util.get_orcid_id()
    harbor_user = registry.util.get_harbor_user()

    if not orcid_id:
        errors.append({"code": "PREREQUISITE", "message": "Missing ORCID iD"})
    if not harbor_user:
        errors.append(
            {"code": "PREREQUISITE", "message": "Missing Harbor user"}
        )
    if errors:
        return make_errors_response(errors)

    projectname = registry.util.get_starter_project_name()

    project = api.create_project(projectname, is_public=False)

    if "errors" in project:
        return make_errors_response(project["errors"])

    coperson_id = registry.util.get_coperson_id()

    project_expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)

    try:
        registry.util.create_permission_group(
            group_name=f"soteria-{projectname}-temporary",
            project_name=projectname,
            harbor_role_id=HarborRoleID.DEVELOPER,
            comanage_person_id=coperson_id,
            comanage_group_member=True,
            comanage_group_owner=False,
            valid_through=project_expiration_date
        )
    except Exception as error:
        return make_errors_response([{
            "code": "Error", "message": error
        }])

    # Try to delete admin from project, but ignore if it doesn't work
    harbor_admin_username = flask.current_app.config["HARBOR_ADMIN_USERNAME"]
    api.delete_project_member(project['project_id'], harbor_admin_username)

    return make_ok_response({"project_name": project["name"]})


@bp.route("/users/<user_id>/starter_project", methods=["GET"])
def check_user_starter_project(user_id: str):
    """
    Return's the current user's "starter" project in Harbor, if any.
    """
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    api = registry.util.get_admin_harbor_api()

    harbor_user = registry.util.get_harbor_user() or {}
    project_name = registry.util.get_starter_project_name()

    if not harbor_user:
        return make_error_response(
            200,
            f"Missing account on {flask.current_app.config['HARBOR_NAME']}",
        )

    orcid_id = registry.util.get_orcid_id()

    if not orcid_id:
        return make_error_response(200, "Missing ORCID iD")

    response = api.get_project(project_name)

    flask.current_app.logger.info(response)

    harbor = {
        "name": flask.current_app.config["HARBOR_NAME"],
        "projects_url": flask.current_app.config["HARBOR_HOMEPAGE_URL"]
        + "/harbor/projects",
    }

    if "errors" in response:
        return make_ok_response({"verified": False})
    return make_ok_response(
        {"verified": True, "harbor": harbor, "project": response}
    )
