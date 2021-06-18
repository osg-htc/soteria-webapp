"""
Blueprints for the API's routes.
"""

from typing import Any, List

from flask import Blueprint, make_response, request

from ... import util

import time
import random

__all__ = ["api_bp_test"]

api_bp_test = Blueprint("api_test", __name__)

def createResponse(verified, info={}):
    time.sleep(random.random()*2)
    base = info
    if verified:
        base.update({"verified":verified})

    return base

def api_response(ok: bool, data: Any = None, errors: List[str] = None):
    body = {"status": "ok" if ok else "error"}

    if data:
        body["data"] = data

    if errors:
        body["errors"] = errors  # type: ignore[assignment]

    return make_response(body)


@api_bp_test.route("/ping", methods=["GET", "POST", "PUT", "DELETE"])
def ping():
    """
    Confirms that the API is functioning at some minimal level.
    """
    return api_response(True, "pong!")


@api_bp_test.route("/verify_harbor_account")
def verify_harbor_account():
    data = createResponse(True, {"username":"takingdrake"})
    #data = createResponse(False, {"username": "takingdrake"})

    return api_response(True, data)


@api_bp_test.route("/verify_orcid")
def verify_orcid():
    data = createResponse(True, {"orc_id":"23462456456"})
    #data = createResponse(False, {"orc_id":"345634563456"})

    return api_response(True, data)


@api_bp_test.route("/create_harbor_project")
def create_harbor_project():

    data = createResponse(True, {"url":"https://takingdrake.org"})
    #data = createResponse(False, {"url":"https://takingdrake.com"})

    return api_response(True, data)
