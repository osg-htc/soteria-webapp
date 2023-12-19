"""
SOTERIA command-line interface.
"""

import click
import flask

import registry.util

__all__ = ["bp"]

bp = flask.Blueprint("command_line_interface", __name__)


@bp.cli.command("list-all-projects")
def list_all_projects() -> None:
    api = registry.util.get_admin_harbor_api()

    for p in api.get_all_projects():
        print(f'{p["project_id"]} {p["name"]}')


@bp.cli.command("list-all-webhooks")
def list_all_webhooks() -> None:
    api = registry.util.get_admin_harbor_api()

    for p in api.get_all_projects():
        for w in api.get_all_webhooks(p["project_id"]):
            print(w)


@bp.cli.command("delete-all-webhooks")
def delete_all_webhooks() -> None:
    api = registry.util.get_admin_harbor_api()

    for p in api.get_all_projects():
        api.delete_all_webhooks(p["project_id"])


@bp.cli.command("set-project-webhooks")
@click.argument("project_id")
def set_project_webhooks(project_id) -> None:
    api = registry.util.get_admin_harbor_api()
    harbor = registry.util.Harbor(harbor_api=api)
    harbor.set_webhooks(project_id)


@bp.cli.command("set-all-project-webhooks")
def set_all_project_webhooks() -> None:
    api = registry.util.get_admin_harbor_api()
    harbor = registry.util.Harbor(harbor_api=api)

    for p in api.get_all_projects():
        harbor.set_webhooks(p["project_id"])
