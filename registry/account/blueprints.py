"""
Blueprints for pages where the current user can manage their registration.
"""

from flask import Blueprint, make_response, render_template, request
from registry.forms import ResearcherApplication
import json

__all__ = ["account_bp"]

account_bp = Blueprint("account", __name__, template_folder="templates")

@account_bp.route("/", methods=["GET", "POST"])
def index():
    """
    Returns a page where the current user can manage their registration.
    """
    try:
        with open("../data-templates/TEMPLATE-user.json") as json_file:
            user = json.load(json_file)
    except:
        user = {
          "name": "First Last",
          "orcid_id": 11235813,
          "status": "Affiliate/Member/Researcher",
          "email": "hello@world.org",
          "days_remaining": "Days Left (int)"
        }


    return make_response(render_template("account.html", user=user))
