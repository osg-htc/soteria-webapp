"""
Public Side of the Soteria Website

Provides views of Projects, images, etc...
"""

import flask

__all__ = ["bp"]

bp = flask.Blueprint("public", __name__)


@bp.route("/projects")
def public_projects():
    return flask.render_template("/public/projects.html")


@bp.route("/projects/<project>/repositories")
def public_project_repositories(project: str):
    return flask.render_template("/public/repositories.html", project=project)

@bp.route("/projects/<project>/repositories/<repository>/tags")
def public_project_repository_tags(project: str, repository: str):
    return flask.render_template("/public/tags.html", project=project, repository=repository)

@bp.route("/projects/<project>/repositories/<repository>/tags/<tag>")
def public_project_repository_image(project: str, repository: str, tag: str):
    return flask.render_template("/public/image.html", project=project, repository=repository, tag=tag)