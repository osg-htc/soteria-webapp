"""
Blueprints for the API's routes.
"""

from typing import Any, List

import requests
from flask import Blueprint, make_response

from ...util import get_orcid, get_user_harbor_api

__all__ = ["api_bp"]

api_bp = Blueprint("api", __name__)


def api_response(ok: bool, data: Any = None, errors: List[str] = None):
    body = {"status": "ok" if ok else "error"}

    if data:
        body["data"] = data

    if errors:
        body["errors"] = errors

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
    Verifies that the current user has created an account in Harbor.
    """
    api = get_user_harbor_api()

    if api:
        try:
            r = api.current_user()
        except requests.RequestException:
            r = None

    data = {"verified": bool(r)}

    return api_response(True, data)


@api_bp.route("/verify_orcid")
def verify_orcid():
    """
    Verifies that the current user has an ORCID.
    """
    orcid = get_orcid()

    data = {"verified": bool(orcid), "orcid": orcid}

    return api_response(True, data)


@api_bp.route("/create_harbor_project")
def create_harbor_project():
    """
    Creates a "starter" project in Harbor for the current user.
    """
    raise NotImplementedError
