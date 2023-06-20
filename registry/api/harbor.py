"""
Wrapper around
"""

import flask
import requests
import json

import registry.harbor
from registry.util import get_admin_harbor_api, get_harbor_api, is_soteria_admin

__all__ = ["bp"]

bp = flask.Blueprint("harbor_api", __name__)

HEADERS_TO_PASS = ["Content-Type", "Date", "Link", "X-Total-Count", "X-Request-Id"]

def get_api() -> registry.harbor.HarborAPI:
    """Prevents non admin users form accessing the admin harbor api"""

    if is_soteria_admin():
        return get_admin_harbor_api()
    else:
        return get_harbor_api()

@bp.route('/get/', defaults={'path': ''}, methods=["GET"])
@bp.route('/get/<path:path>')
def catch_all(path):
    response = requests.get("{0}/{1}".format(flask.current_app.config["HARBOR_API_URL"], path), params=flask.request.args)
    headers = {k:v for k,v in response.headers.items() if k in HEADERS_TO_PASS}

    return flask.make_response((response.content, response.status_code, headers))

@bp.route('/users', methods=["GET"])
def get_users():
    response = get_api().get_users(**flask.request.args)
    headers = {k: v for k, v in response.headers.items() if k in HEADERS_TO_PASS}
    return flask.make_response((response.content, response.status_code, headers))

@bp.route("/audit-logs", methods=["GET"])
def audit_logs():
    response = get_api().get_audit_logs(**flask.request.args)
    headers = {k: v for k, v in response.headers.items() if k in HEADERS_TO_PASS}
    return flask.make_response((response.content, response.status_code, headers))

@bp.route("/scanners/all", methods=["GET"])
def scanners_all():
    response = get_api().get_all_scanners(**flask.request.args)
    return flask.Response(json.dumps([*response]),  mimetype='application/json')
