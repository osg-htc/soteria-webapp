"""
Blueprints for the API's routes.
"""

from typing import Any, List

from flask import Blueprint, make_response, request

from ... import util

__all__ = ["api_bp"]

api_bp = Blueprint("api", __name__)


def api_response(ok: bool, data: Any = None, errors: List[str] = None):
    body = {"status": "ok" if ok else "error"}

    if data:
        body["data"] = data

    if errors:
        body["errors"] = errors  # type: ignore[assignment]

    return make_response(body)


@api_bp.route("/ping", methods=["GET", "POST", "PUT", "DELETE"])
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
    api = util.get_admin_harbor_api()

    subiss = util.get_subiss()
    username = None

    for user in api.all_users():
        details = api.user(user["user_id"])

        if subiss == details["oidc_user_meta"]["subiss"]:
            username = details["username"]
            break

    data = {"verified": bool(username), "username": username}

    return api_response(True, data)


@api_bp.route("/verify_orcid")
def verify_orcid():
    """
    Verifies that the current user has an ORCID.
    """
    orcid = util.get_orcid()

    data = {"verified": bool(orcid), "orcid": orcid}

    return api_response(True, data)


@api_bp.route("/create_harbor_project")
def create_harbor_project():
    """
    Creates a "starter" repositories in Harbor for the current user.
    """
    raise NotImplementedError
