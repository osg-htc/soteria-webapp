"""
Blueprints for repositories page that shows all of a users repositories
"""

from flask import Blueprint, make_response, render_template
import json

__all__ = ["repositories_bp"]

repositories_bp = Blueprint("repositories", __name__, template_folder="templates")

@repositories_bp.route("/", methods=['GET', 'POST'])
def index():
    """
    Returns a page where the current user can manage their registration.
    """

    with open("../data-templates/TEMPLATE-projects.json") as json_file:
        projects = json.load(json_file)

    return make_response(render_template("repositories.html", projects=projects))

