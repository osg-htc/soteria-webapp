"""
Blueprints for debugging the application.
"""

import json
import os

from flask import Blueprint, current_app, make_response, request

from ..harbor import HarborAPI

__all__ = ["debugging_bp"]

debugging_bp = Blueprint("debug", __name__)


@debugging_bp.route("/environ")
def environ():
    """
    Logs the request's environment, and returns nothing.
    """
    env = {k: str(request.environ[k]) for k in request.environ}

    current_app.logger.debug(json.dumps(env, indent=2, sort_keys=True))

    return make_response({"status": "ok", "data": None})


@debugging_bp.route("/arbitrary")
def arbitrary():
    api_server = current_app.config["HARBOR_API"]

    api = HarborAPI(api_server, token=request.environ["OIDC_access_token"])

    return api._get("/users/current")
