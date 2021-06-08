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


def get_orcid() -> Optional[str]:
    """
    Returns the current user's ORCID, if available.
    """
    return request.environ.get("OIDC_CLAIM_orcid")


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
