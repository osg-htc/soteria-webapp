"""
Blueprints for debugging the application.
"""

import json

from flask import Blueprint, current_app, make_response, request

__all__ = ["debugging_bp"]

debugging_bp = Blueprint("debug", __name__)


@debugging_bp.route("/environ")
def environ():
    """
    Logs the request's environment, and returns nothing.
    """
    current_app.logger.debug(request.environ)

    return make_response({"status": "ok", "data": None})
