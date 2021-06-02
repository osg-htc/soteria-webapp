"""
Assorted helper functions.
"""

from typing import Optional

from flask import request


def get_orcid() -> Optional[str]:
    """
    Returns the current user's ORCID, if available.
    """
    return request.environ.get("OIDC_CLAIM_orcid")
