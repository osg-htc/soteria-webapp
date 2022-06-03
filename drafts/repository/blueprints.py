"""
Blueprints for repository page that shows repository details
"""

import json

from flask import Blueprint, make_response, render_template

__all__ = ["repository_bp"]

repository_bp = Blueprint("repository", __name__, template_folder="templates")


@repository_bp.route("/<user_name>/<project_name>/", methods=["GET", "POST"])
@repository_bp.route("/<user_name>/<project_name>/general", methods=["GET", "POST"])
def index(user_name, project_name):
    """
    Returns a page where the current user can manage their registration.
    """

    with open("../data-templates/TEMPLATE-projects.json") as json_file:
        projects = json.load(json_file)
        for project in projects:
            if project["name"] == project_name:
                break

    return make_response(
        render_template(
            "repository.html",
            project=project,
            user_name=user_name,
            project_name=project_name,
        )
    )


@repository_bp.route("/<user_name>/<project_name>/tags", methods=["GET", "POST"])
def tags(user_name, project_name):

    with open("../data-templates/TEMPLATE-projects.json") as json_file:
        projects = json.load(json_file)
        for project in projects:
            if project["name"] == project_name:
                break

    tags = project["tags"]

    return make_response(render_template("tags.html", project=project, tags=tags))


@repository_bp.route("/<user_name>/<project_name>/collaborators", methods=["GET", "POST"])
def collaborators(user_name, project_name):

    with open("../data-templates/TEMPLATE-projects.json") as json_file:
        projects = json.load(json_file)
        for project in projects:
            if project["name"] == project_name:
                break

    users = project["users"]

    return make_response(render_template("collaborators.html", project=project, users=users))
