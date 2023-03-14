"""
Wrapper around
"""

import flask
import requests

__all__ = ["bp"]

bp = flask.Blueprint("harbor_wrapper", __name__)

HEADERS_TO_PASS = ["Content-Type", "Date", "Link", "X-Total-Count", "X-Request-Id"]


@bp.route('/get/', defaults={'path': ''})
@bp.route('/get/<path:path>')
def catch_all(path):
    response = requests.get("{0}/{1}".format(flask.current_app.config["HARBOR_API_URL"], path), params=flask.request.args)
    json = response.json()
    headers = {k:v for k,v in response.headers.items() if k in HEADERS_TO_PASS}

    return flask.make_response((flask.jsonify(json), response.status_code, headers))
