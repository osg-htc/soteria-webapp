"""
SOTERIA's command-line interface.
"""

import time

import click
import flask

import registry.database
import registry.processing
import registry.util

__all__ = ["bp"]

# Number of seconds to wait between iterations of the polling loop.
LOOP_DELAY = 120

bp = flask.Blueprint("command_line_interface", __name__)


# --------------------------------------------------------------------------


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


# --------------------------------------------------------------------------


@bp.cli.command("reinitialize-database")
def reinitialize_database() -> None:
    """
    (Re)Initialize the web application's database.

    This should be necessary only in the event that the database was removed
    after the application instance was created, e.g., during development and
    testing.
    """
    registry.database.init(flask.current_app)


@bp.cli.command("run-polling-loop")
def run_polling_loop() -> None:
    """
    Periodically poll the web application's database.
    """
    app = flask.current_app
    loop_delay = LOOP_DELAY if not app.config.get("SOTERIA_DEBUG") else 15

    try:
        while True:
            app.logger.debug("Starting iteration of polling loop")
            for payload in registry.database.get_new_payloads():
                if new_state := registry.processing.process(payload):
                    registry.database.update_payload(payload.id_, new_state)
                    registry.processing.finalize_payload(payload)

            app.logger.debug("Finished iteration of polling loop")
            time.sleep(loop_delay)
    except Exception:  # pylint: disable=broad-except
        app.logger.exception("Uncaught exception")
