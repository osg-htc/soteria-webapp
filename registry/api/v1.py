"""
SOTERIA API version 1.
"""

import dataclasses
import datetime
import json
from typing import Any, Dict, List, Optional, Union

import flask
from typing_extensions import Literal

import registry.util
from registry.cache import cache
from registry.harbor import HarborRoleID

__all__ = ["bp"]

bp = flask.Blueprint("api_v1", __name__)


@dataclasses.dataclass
class UserObject:
    is_soteria_affiliate: bool
    is_soteria_member: bool
    is_soteria_researcher: bool
    is_registered: bool

    harbor_id: Optional[str] = None
    harbor_username: Optional[str] = None
    orcid_id: Optional[str] = None


@dataclasses.dataclass
class ProjectObject:
    harbor_id: Optional[str] = None
    harbor_name: Optional[str] = None


@dataclasses.dataclass
class MiscellaneousObject:
    blob: str


DataObject = Union[UserObject, Dict[str, Any]]


@dataclasses.dataclass
class BaseResponse:
    status: Literal["ok", "errors"]


@dataclasses.dataclass
class SoteriaResponse(BaseResponse):
    data: DataObject


@dataclasses.dataclass
class ErrorResponse(BaseResponse):
    errors: Union[Any, List[Dict[Literal["code", "message"], str]]]


def make_ok_response(data: DataObject) -> flask.Response:
    response = SoteriaResponse("ok", data)
    return flask.make_response(dataclasses.asdict(response))


def make_error_response(code: int, message: str) -> flask.Response:
    response = ErrorResponse("errors", [{"code": str(code), "message": message}])
    if 400 <= code < 600:
        return flask.make_response(dataclasses.asdict(response), code)
    return flask.make_response(dataclasses.asdict(response))


def make_errors_response(errors: Any) -> flask.Response:
    response = ErrorResponse("errors", errors)
    return flask.make_response(dataclasses.asdict(response), 500)


@bp.after_request
def disable_caching(resp: flask.Response) -> flask.Response:
    """
    Sets the response's headers to prevent storing responses at the client.
    """
    resp.headers["Cache-Control"] = "no-store"

    return resp


@bp.route("/ping", methods=["GET", "POST", "PUT", "DELETE"])
def ping():
    """
    Confirms that the API is functioning at some minimal level.
    """
    return make_ok_response({"message": "pong!"})


@bp.route("/version")
def version() -> flask.Response:
    version_string = flask.current_app.config.get("SOTERIA_VERSION", "<not set>")

    return make_ok_response({"version": version_string})


@bp.route("/users/<user_id>")
def get_user(user_id: str) -> flask.Response:
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    harbor_user = registry.util.get_harbor_user() or {}

    user = UserObject(
        is_soteria_affiliate=registry.util.is_soteria_affiliate(),
        is_soteria_member=registry.util.is_soteria_member(),
        is_soteria_researcher=registry.util.is_soteria_researcher(),
        is_registered=registry.util.is_registered(),
        harbor_id=harbor_user.get("user_id"),
        harbor_username=harbor_user.get("username"),
        orcid_id=registry.util.get_orcid_id(),
    )

    return make_ok_response(user)


@bp.route("/users/<user_id>/enrollment")
def check_user_enrollment(user_id: str):
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    enrolled = registry.util.is_in_soteria_cou()
    idp_name = registry.util.get_idp_name()

    data = {"verified": bool(enrolled), "idp_name": idp_name}

    return make_ok_response(data)


@bp.route("/users/<user_id>/harbor_id")
def check_user_harbor_id(user_id: str):
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    flask.current_app.logger.info("Subiss Below:")
    flask.current_app.logger.info(registry.util.get_subiss())

    cache.delete_memoized(registry.util.get_harbor_user_by_subiss, registry.util.get_subiss())
    harbor_user = registry.util.get_harbor_user()

    username = harbor_user["username"] if harbor_user else None

    data = {
        "verified": bool(username),
        "username": username,
        "harbor": {"name": flask.current_app.config["HARBOR_NAME"]},
    }

    return make_ok_response(data)


@bp.route("/users/<user_id>/orcid_id")
def verify_orcid(user_id: str):
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    orcid_id = registry.util.get_orcid_id()

    data = {"verified": bool(orcid_id), "orcid_id": orcid_id}

    return make_ok_response(data)


@bp.route("/users/<user_id>/projects")
def get_projects(user_id: str):
    """
    Lists all current users related projects
    """
    if user_id != "current":
        return make_error_response(400, "Malformed user ID")

    return flask.jsonify(
        registry.util.get_harbor_projects(
            owner=True, maintainer=True, developer=True, guest=True, temporary=True
        )
    )


@bp.route("/webhooks/harbor", methods=["POST"])
def webhook_for_harbor():
    auth = flask.request.authorization

    if (
        auth
        and auth.type.lower() == "bearer"
        and auth.token == flask.current_app.config["WEBHOOKS_HARBOR_BEARER_TOKEN"]
    ):
        payload = flask.request.get_json()
        payload_as_msg = json.dumps(payload, indent=2)
        payload_as_text = json.dumps(payload, separators=(",", ":"))

        flask.current_app.logger.info(f"Webhook called from Harbor: {payload_as_msg}")
        registry.database.insert_new_payload(payload_as_text)
        return make_ok_response({"message": "webhook completed succesfully"})

    return make_error_response(401, "Missing authorization")
