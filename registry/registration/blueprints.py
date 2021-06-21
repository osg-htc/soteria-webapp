"""
Blueprints for pages where the current user can manage their registration.
"""

from flask import Blueprint, make_response, render_template

__all__ = ["registration_bp"]

registration_bp = Blueprint("registration", __name__, template_folder="templates")


@registration_bp.route("/")
def index():
    """
    Returns a page where the current user can manage their registration.
    """
    return make_response(render_template("registration.html"))
