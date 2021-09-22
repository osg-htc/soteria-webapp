"""
Assorted helper functions.
"""

import logging
import logging.handlers
import pathlib
from typing import Any, List, Optional

import flask
import ldap3

import registry.harbor

__all__ = [
    "configure_logging",
    #
    "get_comanage_groups",
    "get_harbor_user",
    "get_idp_name",
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
    if flask.current_app.config.get("SOTERIA_DEBUG"):
        flask.request.environ.update(flask.current_app.config.get("FAKE_USER", {}))


def get_comanage_groups() -> List[str]:
    update_request_environ()

    sub = flask.request.environ.get("OIDC_CLAIM_sub")

    if sub:
        ldap_url = flask.current_app.config.get("LDAP_URL")
        ldap_username = flask.current_app.config.get("LDAP_USERNAME")
        ldap_password = flask.current_app.config.get("LDAP_PASSWORD")
        ldap_base_dn = flask.current_app.config.get("LDAP_BASE_DN")

        server = ldap3.Server(ldap_url, get_info=ldap3.ALL)

        with ldap3.Connection(server, ldap_username, ldap_password) as conn:

            conn.search(
                ldap_base_dn,
                f"(&(objectClass=inetOrgPerson)(uid={sub}))",
                attributes=["isMemberOf"],
            )

            if len(conn.entries) > 1:
                flask.current_app.logger.error("???")

            return conn.entries[0].entry_attributes_as_dict["isMemberOf"]

    return None


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


def get_idp_name() -> Optional[str]:
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_idp_name")


def get_orcid_id() -> Optional[str]:
    """
    Returns the current user's ORCID iD.
    """
    update_request_environ()

    sub = flask.request.environ.get("OIDC_CLAIM_sub")

    if sub:
        ldap_url = flask.current_app.config.get("LDAP_URL")
        ldap_username = flask.current_app.config.get("LDAP_USERNAME")
        ldap_password = flask.current_app.config.get("LDAP_PASSWORD")
        ldap_base_dn = flask.current_app.config.get("LDAP_BASE_DN")

        server = ldap3.Server(ldap_url, get_info=ldap3.ALL)

        with ldap3.Connection(server, ldap_username, ldap_password) as conn:

            conn.search(
                ldap_base_dn,
                f"(&(objectClass=inetOrgPerson)(uid={sub}))",
                attributes=["eduPersonOrcid"],
            )

            flask.current_app.logger.debug(sub)

            if len(conn.entries) > 1:
                flask.current_app.logger.error("???")

            return conn.entries[0].entry_attributes_as_dict["eduPersonOrcid"]

    return None


def get_subiss() -> Optional[str]:
    """
    Returns the concatenation of the current user's `sub` and `iss`.
    """
    update_request_environ()

    sub: str = flask.request.environ.get("OIDC_CLAIM_sub", "")
    iss: str = flask.request.environ.get("OIDC_CLAIM_iss", "")

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


def get_admin_harbor_api() -> registry.harbor.HarborAPI:
    """
    Returns a Harbor API instance authenticated as an admin.
    """
    return registry.harbor.HarborAPI(
        flask.current_app.config["HARBOR_API_URL"],
        basic_auth=(
            flask.current_app.config["HARBOR_ADMIN_USERNAME"],
            flask.current_app.config["HARBOR_ADMIN_PASSWORD"],
        ),
    )


def get_robot_harbor_api() -> registry.harbor.HarborAPI:
    """
    Returns a Harbor API instance authenticated as a robot.
    """
    return registry.harbor.HarborAPI(
        flask.current_app.config["HARBOR_API_URL"],
        basic_auth=(
            flask.current_app.config["HARBOR_ROBOT_USERNAME"],
            flask.current_app.config["HARBOR_ROBOT_PASSWORD"],
        ),
    )
