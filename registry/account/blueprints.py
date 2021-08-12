"""
Blueprints for pages where the current user can manage their registration.
"""

from flask import Blueprint, make_response, render_template
import json

__all__ = ["account_bp"]

account_bp = Blueprint("account", __name__, template_folder="templates")

@account_bp.route("/")
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
          "ORCID": 11235813,
          "account_type": "Affiliate/Member/Researcher",
          "account_status": "Days Left (int)"
        }


    return make_response(render_template("account.html", user=user))
