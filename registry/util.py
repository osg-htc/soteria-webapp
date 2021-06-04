"""
Assorted helper functions.
"""

from typing import Optional

from flask import current_app, request

from .harbor import HarborAPI

__all__ = [
    "get_orcid",
    "get_user_harbor_api",
]


def get_orcid() -> Optional[str]:
    """
    Returns the current user's ORCID, if available.
    """
    return request.environ.get("OIDC_CLAIM_orcid")


def get_user_harbor_api() -> Optional[HarborAPI]:
    """
    Returns a Harbor API instance that is authenticated as the current user.
    """
    token = request.environ.get("OIDC_id_token")

    if token:
        return HarborAPI(current_app.config["HARBOR_API"], bearer_token=token)

    return None
