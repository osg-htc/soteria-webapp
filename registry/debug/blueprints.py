"""
Blueprints for debugging the application.
"""

import json
import os

from flask import Blueprint, make_response

__all__ = ["debugging_bp"]

debugging_bp = Blueprint("debug", __name__)


@debugging_bp.route("/environ")
def environ():
    """
    Returns all available environment variables.
    """
    return make_response(json.dumps(dict(os.environ), indent=2, sort_keys=True))
