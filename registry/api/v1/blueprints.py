"""
Blueprints for the API's routes.
"""

from typing import Any, Dict, List

from flask import Blueprint, current_app, make_response

import registry.util

__all__ = ["api_bp"]

api_bp = Blueprint("api", __name__)


def api_response(ok: bool, data: Any = None, errors: List[Dict[str, str]] = None):
    body = {"status": "ok" if ok else "error"}

    if data:
        body["data"] = data

    if errors:
        body["errors"] = errors  # type: ignore[assignment]

    return make_response(body)


@api_bp.route("/ping", methods=["HEAD", "GET", "POST", "PUT", "DELETE"])
def ping():
    """
    Confirms that the API is functioning at some minimal level.
    """
    return api_response(True, "pong!")


@api_bp.route("/verify_harbor_account")
def verify_harbor_account():
    """
    Verifies that the current user has created an registration in Harbor.
    """
    harbor_user = registry.util.get_harbor_user()

    username = harbor_user["username"] if harbor_user else None

    data = {"verified": bool(username), "username": username}

    return api_response(True, data)


@api_bp.route("/verify_orcid_id")
def verify_orcid():
    """
    Verifies that the current user has an ORCID iD.
    """
    orcid_id = registry.util.get_orcid_id()

    data = {"verified": bool(orcid_id), "orcid_id": orcid_id}

    return api_response(True, data)


@api_bp.route("/create_harbor_project")
def create_harbor_project():
    """
    Creates a "starter" repositories in Harbor for the current user.
    """
    api = registry.util.get_admin_harbor_api()
    whoami = current_app.config["HARBOR_ADMIN_USERNAME"]
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
