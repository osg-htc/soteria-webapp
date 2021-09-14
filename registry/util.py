"""
Assorted helper functions.
"""

import logging
import logging.handlers
import pathlib
from typing import Any, List, Optional

from flask import current_app, request

from .harbor import HarborAPI

__all__ = [
    "configure_logging",
    #
    "get_comanage_groups",
    "get_harbor_user",
    "get_orcid_id",
    "has_organizational_identity",
    "is_soteria_affiliate",
    "is_soteria_member",
    "is_soteria_researcher",
    #
    "get_admin_harbor_api",
    "get_robot_harbor_api",
]


def configure_logging(
    filename: pathlib.Path,
    *,
    level: int = logging.DEBUG,
    fmt: str = "[%(asctime)s] %(levelname)s %(module)s:%(lineno)d %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    maxBytes: int = 10 * 1024 * 1024,
    backupCount: int = 4,  # plus the current log file -> 50 MiB total
) -> None:
    """
    Adds a stream handler and a rotating file handler to the root logger.
    """

    filename.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    for handler in [
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            filename, maxBytes=maxBytes, backupCount=backupCount
        ),
    ]:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)


def update_request_environ() -> None:
    """
    Add mock data to the current request's environment if debugging is enabled.
    """
    if current_app.config.get("SOTERIA_DEBUG"):
        request.environ.update(current_app.config.get("FAKE_USER", {}))


def get_comanage_groups() -> List[str]:
    update_request_environ()

    raw_groups = request.environ.get("OIDC_CLAIM_groups")

    if raw_groups:
        return raw_groups.split(",")
    return []


def get_harbor_user() -> Any:
    """
    Returns the current users's Harbor account.
    """
    api = get_admin_harbor_api()

    subiss = get_subiss()

    for user in api.get_all_users():
        details = api.get_user(user["user_id"])

        if subiss == details["oidc_user_meta"]["subiss"]:
            return details

    return None


def get_orcid_id() -> Optional[str]:
    """
    Returns the current user's ORCID iD.
    """
    update_request_environ()

    return request.environ.get("OIDC_CLAIM_orcid")


def get_subiss() -> Optional[str]:
    """
    Returns the concatenation of the current user's `sub` and `iss`.
    """
    update_request_environ()

    sub = request.environ.get("OIDC_CLAIM_sub")
    iss = request.environ.get("OIDC_CLAIM_iss")

    if sub and iss:
        return sub + iss

    return None


def has_organizational_identity() -> bool:
    groups = get_comanage_groups()

    return "CO:members:all" in groups


def is_soteria_affiliate() -> bool:
    groups = get_comanage_groups()

    return "CO:COU:SOTERIA-All:members:all" in groups


def is_soteria_member() -> bool:
    groups = get_comanage_groups()

    return "CO:COU:SOTERIA-Collaborators:members:all" in groups


def is_soteria_researcher() -> bool:
    groups = get_comanage_groups()

    return "CO:COU:SOTERIA-Researchers:members:all" in groups


def get_admin_harbor_api() -> HarborAPI:
    """
    Returns a Harbor API instance authenticated as an admin.
    """
    return HarborAPI(
        current_app.config["HARBOR_API_URL"],
        basic_auth=(
            current_app.config["HARBOR_ADMIN_USERNAME"],
            current_app.config["HARBOR_ADMIN_PASSWORD"],
        ),
    )


def get_robot_harbor_api() -> HarborAPI:
    """
    Returns a Harbor API instance authenticated as a robot.
    """
    return HarborAPI(
        current_app.config["HARBOR_API_URL"],
        basic_auth=(
            current_app.config["HARBOR_ROBOT_USERNAME"],
            current_app.config["HARBOR_ROBOT_PASSWORD"],
        ),
    )
