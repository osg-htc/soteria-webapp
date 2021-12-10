"""
SOTERIA API version 1.
"""

import dataclasses
from typing import Any, Dict, List, Optional, Union

import flask
from typing_extensions import Literal

import registry.util

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


## FIXME: Old routes


# def api_response(
#     ok: bool, data: Any = None, errors: Optional[List[Dict[str, str]]] = None
# ):
#     body = {"status": "ok" if ok else "error"}
#
#     if data:
#         body["data"] = data
#
#     if errors:
#         body["errors"] = errors  # type: ignore[assignment]
#
#     return flask.make_response(body)


@bp.route("/users/<user_id>/starter_project", methods=["POST"])
def create_user_starter_project(user_id: str):
    """
    Creates a "starter" repositories in Harbor for the current user.
    """
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    api = registry.util.get_admin_harbor_api()
    whoami = flask.current_app.config["HARBOR_ADMIN_USERNAME"]
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

    username = harbor_user["username"]

    project = api.create_project(username)

    if "errors" in project:
        return make_errors_response(project["errors"])

    project_id = project["project_id"]

    response = api.add_project_member(project_id, username)

    if "errors" in response:
        return make_errors_response(response["errors"])

    response = api.delete_project_member(project_id, whoami)

    if "errors" in response:
        return make_errors_response(response["errors"])

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
    project_name = harbor_user["username"]

    if not harbor_user:
        return make_error_response(
            200,
            f"Missing account on {flask.current_app.config['HARBOR_NAME']}",
        )

    orcid_id = registry.util.get_orcid_id()

    if not orcid_id:
        return make_error_response(200, "Missing ORCID iD")

    response = api.get_project(project_name)

    if "errors" in response:
        return make_ok_response({"verified": False})
    return make_ok_response({"verified": True, "project": response})
