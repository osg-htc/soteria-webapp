"""
SOTERIA command-line interface.
"""

import flask

__all__ = ["bp"]

bp = flask.Blueprint("command_line_interface", __name__)
