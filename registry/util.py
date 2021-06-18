"""
Assorted helper functions.
"""

from typing import Optional

from flask import current_app, request

from .harbor import HarborAPI

__all__ = [
    "get_orcid",
    #
    "get_admin_harbor_api",
    "get_robot_harbor_api",
]


def update_request_environ() -> None:
    """
    Add mock data to the current request's environment if debugging is enabled.
    """
    if current_app.config.get("REGISTRY_DEBUG"):
        request.environ.update(current_app.config.get("FAKE_USER", {}))


def get_orcid() -> Optional[str]:
    """
    Returns the current user's ORCID.
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


def get_admin_harbor_api() -> HarborAPI:
    """
    Returns a Harbor API instance authenticated as an admin.
    """
    return HarborAPI(
        current_app.config["HARBOR_API"],
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
        current_app.config["HARBOR_API"],
        basic_auth=(
            current_app.config["HARBOR_ROBOT_USERNAME"],
            current_app.config["HARBOR_ROBOT_PASSWORD"],
        ),
    )
