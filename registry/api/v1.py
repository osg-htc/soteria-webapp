"""
SOTERIA API version 1.
"""

import dataclasses
from typing import Any, Dict, List, Optional, Union

import flask
from typing_extensions import Literal

import registry.util

# from flask import Response, Blueprint, current_app, make_response


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


DataObject = Union[UserObject, ProjectObject, MiscellaneousObject]


@dataclasses.dataclass
class SoteriaResponse:
    status: Literal["ok", "errors"]
    data: Optional[DataObject] = None
    errors: Optional[List[Dict[Literal["code", "message"], str]]] = None


def make_ok_response(data: DataObject) -> flask.Response:
    response = SoteriaResponse(status="ok", data=data)
    return flask.make_response(dataclasses.asdict(response))


def make_error_response(code: int, message: str) -> flask.Response:
    response = SoteriaResponse(
        status="errors", errors=[{"code": str(code), "message": message}]
    )
    if 400 <= code < 600:
        return flask.make_response(dataclasses.asdict(response), code)
    return flask.make_response(dataclasses.asdict(response))


@bp.route("/ping", methods=["GET", "POST", "PUT", "DELETE"])
def ping():
    """
    Confirms that the API is functioning at some minimal level.
    """
    return api_response(True, "pong!")


@bp.route("/users/<id>")
def get_user(id: str) -> flask.Response:
    if id != "current":
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


## FIXME: Old routes


def api_response(
    ok: bool, data: Any = None, errors: Optional[List[Dict[str, str]]] = None
):
    body = {"status": "ok" if ok else "error"}

    if data:
        body["data"] = data

    if errors:
        body["errors"] = errors  # type: ignore[assignment]

    return flask.make_response(body)


@bp.route("/verify_enrollment")
def verify_enrollment():
    enrolled = registry.util.has_organizational_identity()
    idp_name = registry.util.get_idp_name()

    data = {"verified": bool(enrolled), "idp_name": idp_name}

    return api_response(True, data)


@bp.route("/verify_harbor_account")
def verify_harbor_account():
    """
    Verifies that the current user has created an registration in Harbor.
    """
    harbor_user = registry.util.get_harbor_user()

    username = harbor_user["username"] if harbor_user else None

    data = {"verified": bool(username), "username": username}

    return api_response(True, data)


@bp.route("/verify_orcid_id")
def verify_orcid():
    """
    Verifies that the current user has an ORCID iD.
    """
    orcid_id = registry.util.get_orcid_id()

    data = {"verified": bool(orcid_id), "orcid_id": orcid_id}

    return api_response(True, data)


@bp.route("/create_harbor_project")
def create_harbor_project():
    """
    Creates a "starter" repositories in Harbor for the current user.
    """
    api = registry.util.get_admin_harbor_api()
    whoami = flask.current_app.config["HARBOR_ADMIN_USERNAME"]
    errors = []

    orcid_id = registry.util.get_orcid_id()
    harbor_user = registry.util.get_harbor_user()

    if not orcid_id:
        errors.append({"code": "PREREQUISITE", "message": "Missing ORCID iD"})
    if not harbor_user:
        errors.append({"code": "PREREQUISITE", "message": "Missing Harbor user"})
    if errors:
        return api_response(False, errors=errors)

    username = harbor_user["username"]

    project = api.create_project(username)

    if "errors" in project:
        return api_response(False, errors=project["errors"])

    project_id = project["project_id"]

    response = api.add_project_member(project_id, username)

    if "errors" in response:
        return api_response(False, errors=response["errors"])

    response = api.delete_project_member(project_id, whoami)

    if "errors" in response:
        return api_response(False, errors=response["errors"])

    return api_response(True, data={"project_name": project["name"]})
