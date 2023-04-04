"""
Assorted helper functions.
"""

import logging
import logging.config
import logging.handlers
import pathlib
import re
from typing import Any, List, Optional, Literal

import flask
import ldap3  # type: ignore[import]
import requests.exceptions

import registry.freshdesk
import registry.harbor
from registry.harbor import HarborRoleIds
import registry.comanage
from registry.cache import cache

__all__ = [
    "configure_logging",
    #
    "get_comanage_groups",
    "get_harbor_user",
    "get_idp_name",
    "get_orcid_id",
    "get_starter_project_name",
    "has_organizational_identity",
    "is_soteria_affiliate",
    "is_soteria_member",
    "is_soteria_researcher",
    #
    "get_admin_harbor_api",
]

LOG_FORMAT = "[%(asctime)s] %(levelname)s %(module)s:%(lineno)d %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 4  # plus the current log file -> 50 MiB total, by default


def configure_logging(filename: pathlib.Path) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)

    # We configure logging to the WSGI error stream to be more conservative
    # than the rotating file because the error stream can end up in the web
    # server's log files.

    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {"default": {"format": LOG_FORMAT, "datefmt": LOG_DATE_FORMAT}},
            "handlers": {
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "default",
                    "filename": filename,
                    "maxBytes": LOG_MAX_BYTES,
                    "backupCount": LOG_BACKUP_COUNT,
                },
                "wsgi_stream": {
                    "class": "logging.StreamHandler",
                    "level": "WARNING",
                    "formatter": "default",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                },
            },
            "root": {
                "level": "DEBUG",
                "handlers": ["rotating_file", "wsgi_stream"],
            },
        }
    )


def update_request_environ() -> None:
    """
    Add mock data to the current request's environment if debugging is enabled.
    """
    if flask.current_app.config.get("SOTERIA_DEBUG"):
        mock_oidc_claim = flask.current_app.config.get("MOCK_OIDC_CLAIM", {})
        flask.request.environ.update(mock_oidc_claim)


def get_comanage_groups() -> List[str]:
    update_request_environ()

    sub = flask.request.environ.get("OIDC_CLAIM_sub")

    if sub:
        ldap_url = flask.current_app.config["LDAP_URL"]
        ldap_username = flask.current_app.config["LDAP_USERNAME"]
        ldap_password = flask.current_app.config["LDAP_PASSWORD"]
        ldap_base_dn = flask.current_app.config["LDAP_BASE_DN"]

        server = ldap3.Server(ldap_url, get_info=ldap3.ALL)

        with ldap3.Connection(server, ldap_username, ldap_password) as conn:

            conn.search(
                ldap_base_dn,
                f"(&(objectClass=inetOrgPerson)(uid={sub}))",
                attributes=["*"],
            )

            if len(conn.entries) == 1:
                return conn.entries[0].entry_attributes_as_dict["isMemberOf"]

            if len(conn.entries) > 1:
                flask.current_app.logger.error("???")

    return []


def get_coperson_id():
    """Get the Comamange Person id for the current user"""
    comanage_api = get_admin_comanage_api()
    return comanage_api.get_persons(identifier=get_sub()).json()['CoPeople'][0]['Id']


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


def get_harbor_user():

    subiss = get_subiss()

    return get_harbor_user_by_subiss(subiss)


@cache.memoize()
def get_harbor_user_by_subiss(subiss: str) -> Any:
    """
    Returns the current user's Harbor account.
    """
    api = get_admin_harbor_api()

    for user in api.get_all_users(params={"sort": "-creation_time"}):

        details = api.get_user(user["user_id"])

        flask.current_app.logger.info(details["oidc_user_meta"]["subiss"], subiss)
        flask.current_app.logger.info(subiss == details["oidc_user_meta"]["subiss"])

        if subiss == details["oidc_user_meta"]["subiss"]:
            return details

    return None


def get_harbor_projects() -> Any:
    """Returns the users harbor projects - O(m*n)"""

    comanage_api = registry.util.get_admin_comanage_api()
    harbor_api = registry.util.get_admin_harbor_api()

    coperson_id = registry.util.get_coperson_id()

    comanage_groups = comanage_api.get_groups(coperson_id=coperson_id).json()['CoGroups']

    owner_pattern = re.compile('^soteria-(.*?)-owners')
    owned_project_names = [owner_pattern.match(g['Name']).group(1) for g in comanage_groups if owner_pattern.match(g['Name'])]

    owned_projects = []
    for project_name in owned_project_names:
        owned_projects.append(harbor_api.get_project(project_name))

    return owned_projects


def create_project(name: str, public: bool):
    """Create a researcher project"""

    harbor_api = get_admin_harbor_api()
    comanage_api = get_admin_comanage_api()

    project = harbor_api.create_project(name, public)

    if not ('name' in project and project['name'] == name):
        return project

    comanage_person = comanage_api.get_persons(identifier=get_sub()).json()

    if len(comanage_person['CoPeople']) == 0:
        raise LookupError("Could not find a Comanage account associated with this user")

    coperson_id = comanage_person['CoPeople'][0]['Id']

    # Create the groups in Harbor
    harbor_api.create_project_member(name, HarborRoleIds.maintainer, group_name=f"soteria-{name}-owners")
    harbor_api.create_project_member(name, HarborRoleIds.maintainer, group_name=f"soteria-{name}-maintainers")
    harbor_api.create_project_member(name, HarborRoleIds.developer, group_name=f"soteria-{name}-developers")
    harbor_api.create_project_member(name, HarborRoleIds.guest, group_name=f"soteria-{name}-guests")

    # Create the groups in Comanage
    owner_group = comanage_api.create_group(f"soteria-{name}-owners").json()
    maintainer_group = comanage_api.create_group(f"soteria-{name}-maintainers").json()
    developer_group = comanage_api.create_group(f"soteria-{name}-developers").json()
    guest_group = comanage_api.create_group(f"soteria-{name}-guests").json()

    # Add the researcher to the groups
    comanage_api.add_group_member(owner_group['Id'], coperson_id, member=True, owner=False)
    comanage_api.add_group_member(maintainer_group['Id'], coperson_id, member=True, owner=True)
    comanage_api.add_group_member(developer_group['Id'], coperson_id, member=True, owner=True)
    comanage_api.add_group_member(guest_group['Id'], coperson_id, member=True, owner=True)

    return project


def get_idp_name() -> Optional[str]:
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_idp_name")


def get_name() -> Optional[str]:
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_name")


def get_email() -> Optional[str]:
    update_request_environ()

    return flask.request.environ.get('OIDC_CLAIM_email')


def get_eppn() -> Optional[str]:
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_eppn")


def get_sub() -> Optional[str]:
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_sub")

def get_status() -> Literal['Researcher', 'Member', 'Affiliate']:
    if is_soteria_researcher():
        return 'Researcher'
    elif is_soteria_member():
        return 'Member'
    else:
        return 'Affiliate'

def get_orcid_id() -> Optional[str]:
    """
    Returns the current user's ORCID iD.
    """
    update_request_environ()

    sub = flask.request.environ.get("OIDC_CLAIM_sub")

    if sub:
        ldap_url = flask.current_app.config["LDAP_URL"]
        ldap_username = flask.current_app.config["LDAP_USERNAME"]
        ldap_password = flask.current_app.config["LDAP_PASSWORD"]
        ldap_base_dn = flask.current_app.config["LDAP_BASE_DN"]

        server = ldap3.Server(ldap_url, get_info=ldap3.ALL)

        with ldap3.Connection(server, ldap_username, ldap_password) as conn:

            conn.search(
                ldap_base_dn,
                f"(&(objectClass=inetOrgPerson)(uid={sub}))",
                attributes=["eduPersonOrcid"],
            )

            if len(conn.entries) == 1:
                orcid = conn.entries[0].entry_attributes_as_dict["eduPersonOrcid"]

                return orcid[0] if len(orcid) != 0 else None

    return None


def get_starter_project_name() -> Optional[str]:
    user = get_harbor_user()

    if user:
        return user["username"].lower()

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


def get_admin_comanage_api():
    """
    Returns a Comanage API instance authenticated as an admin.
    """
    return registry.comanage.ComanageAPI(
        flask.current_app.config["REGISTRY_API_URL"],
        flask.current_app.config["REGISTRY_CO_ID"],
        basic_auth=(
            flask.current_app.config["REGISTRY_API_USERNAME"],
            flask.current_app.config["REGISTRY_API_PASSWORD"],
        ),
    )


def get_fresh_desk_api() -> registry.freshdesk.FreshDeskAPI:
    """
    Returns a Fresh Desk API instance
    """
    return registry.freshdesk.FreshDeskAPI(flask.current_app.config["FRESHDESK_API_KEY"])
