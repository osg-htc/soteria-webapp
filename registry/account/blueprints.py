"""
Blueprints for pages where the current user can manage their account.
"""

from flask import Blueprint, make_response, render_template

__all__ = ["account_bp"]

account_bp = Blueprint("account", __name__, template_folder="templates")


@account_bp.route("/")
def index():
    """
    Returns a page where the current user can manage their account.
    """
    return make_response(render_template("account.html"))
