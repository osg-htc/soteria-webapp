"""
Routes for interrogating and debugging the application.
"""

import json

import flask

__all__ = ["bp"]

bp = flask.Blueprint("debug", __name__)


@bp.route("/environ")
def environ():
    """
    Logs the request's environment.
    """
    env = {k: str(flask.request.environ[k]) for k in flask.request.environ}

    flask.current_app.logger.debug(json.dumps(env, indent=2, sort_keys=True))

    return flask.make_response("Ok!")
