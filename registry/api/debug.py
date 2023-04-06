"""
Routes for debugging the application.
"""

import json

import flask

__all__ = ["bp"]

bp = flask.Blueprint("debug", __name__)


@bp.after_request
def disable_caching(resp: flask.Response) -> flask.Response:
    """
    Sets the response's headers to prevent storing responses at the client.
    """
    resp.headers["Cache-Control"] = "no-store"

    return resp


@bp.route("/environ")
def environ():
    """
    Logs the request's environment.
    """
    env = {k: str(flask.request.environ[k]) for k in flask.request.environ}

    flask.current_app.logger.debug(json.dumps(env, indent=2, sort_keys=True))

    return flask.make_response("Ok!")
