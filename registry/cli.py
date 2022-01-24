"""
SOTERIA command-line interface.
"""

import flask

__all__ = ["bp"]

bp = flask.Blueprint("command_line_interface", __name__)


@bp.cli.command("update-hub-roles")
def update_hub_roles():
    raise NotImplementedError
