"""
Blueprints for debugging the application.
"""

import json
import os

from flask import Blueprint, make_response, request

__all__ = ["debugging_bp"]

debugging_bp = Blueprint("debug", __name__)


@debugging_bp.route("/environ")
def environ():
    """
    Returns environment variables that are available to the current request.
    """
    data = {}

    for k in request.environ:
        data[k] = str(request.environ[k])

    return make_response(json.dumps(data, indent=2, sort_keys=True))
