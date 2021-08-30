"""
Blueprints for pages where the current user can manage their registration.
"""

from flask import Blueprint, make_response, render_template
import json

__all__ = ["about_bp"]

about_bp = Blueprint("about", __name__, template_folder="templates")

@about_bp.route("/")
def index():

    return make_response(render_template("about.html"))