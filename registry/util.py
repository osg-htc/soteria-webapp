"""
Assorted helper functions.
"""

import logging
import logging.config
import logging.handlers
import pathlib
import re
import datetime
from typing import Any, Literal, Optional

import flask
import ldap3  # type: ignore[import]

import registry.comanage
import registry.freshdesk
import registry.harbor
from registry.cache import cache
from registry.harbor import HarborRoleID

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
    "get_freshdesk_api",
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
            "formatters": {
                "default": {"format": LOG_FORMAT, "datefmt": LOG_DATE_FORMAT}
            },
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


#
# --------------------------------------------------------------------------
#

def update_request_environ() -> None:
    """
    Adds mock data to the current request's environment if debugging is enabled.
    """
    if flask.current_app.config.get("SOTERIA_DEBUG"):
        mock_oidc_claim = flask.current_app.config.get("MOCK_OIDC_CLAIM", {})
        flask.request.environ.update(mock_oidc_claim)


def get_comanage_groups():
    """
    Returns a list of the current user's groups in COmanage.

    Queries LDAP to ensure that the list is up to date.
    """
    update_request_environ()

    groups = []
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
                groups = conn.entries[0].entry_attributes_as_dict["isMemberOf"]
            else:
                flask.current_app.logger.error(
                    "Found %s entries for the sub: %s",
                    len(conn.entries),
                    sub,
                )

    flask.current_app.logger.debug(
        "Found the following groups for %s: %s",
        sub,
        groups,
    )

    return groups


def get_coperson_id():
    """Get the Comanage Person id for the current user"""
    comanage_api = get_admin_comanage_api()
    return comanage_api.get_persons(identifier=get_sub()).json()["CoPeople"][0][
        "Id"
    ]


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
    """
    Returns the current user's Harbor account.
    """

    harbor_user = None

    api = get_admin_harbor_api()
    email = flask.request.environ.get("OIDC_CLAIM_email")
    subiss = get_subiss()

    flask.current_app.logger.debug(
        "Searching for: email=%s subiss=%s",
        email,
        subiss,
    )

    if not harbor_user and (email and subiss):
        harbor_user = api.search_for_user(email=email, subiss=subiss)

    if not harbor_user:
        harbor_user = get_harbor_user_by_subiss(subiss)

    return harbor_user


@cache.memoize()
def get_harbor_user_by_subiss(subiss: str) -> Any:
    api = get_admin_harbor_api()

    for user in api.get_all_users(params={"sort": "-creation_time"}):
        full_data = api.get_user(user["user_id"])

        if full_data.get("oidc_user_meta", {}).get("subiss", "") == subiss:
            return full_data

    return None


def get_harbor_projects() -> Any:
    """Returns the users harbor projects - O(n)"""

    comanage_api = registry.util.get_admin_comanage_api()
    harbor_api = registry.util.get_admin_harbor_api()

    coperson_id = registry.util.get_coperson_id()

    comanage_groups = comanage_api.get_groups(coperson_id=coperson_id).json()["CoGroups"]
    comanage_group_names = map(lambda x: x['Name'], comanage_groups)

    owner_pattern = re.compile("^soteria-(.*?)-owners")
    temporary_pattern = re.compile("^soteria-(.*?)-temporary")
    developer_pattern = re.compile("^soteria-(.*?)-developers")
    maintainer_pattern = re.compile("^soteria-(.*?)-maintainers")
    guest_pattern = re.compile("^soteria-(.*?)-guests")

    patterns = [owner_pattern, temporary_pattern, developer_pattern, maintainer_pattern, guest_pattern]

    project_names = []
    for group_name in comanage_group_names:
        for pattern in patterns:
            if pattern.match(group_name):
                project_names.append(pattern.match(group_name).group(1))
                break

    projects = []
    for project_name in project_names:
        projects.append(harbor_api.get_project(project_name))

    return projects


def create_project(name: str, public: bool):
    """Create a researcher project"""

    harbor_api = get_admin_harbor_api()

    project = harbor_api.create_project(name, public)

    if not ("name" in project and project["name"] == name):
        return project

    coperson_id = get_coperson_id()

    try:
        create_permission_group(
            group_name=f"soteria-{name}-owners",
            project_name=name,
            harbor_role_id=HarborRoleID.MAINTAINER,
            comanage_person_id=coperson_id,
            comanage_group_member=True,
            comanage_group_owner=False
        )
        create_permission_group(
            group_name=f"soteria-{name}-maintainers",
            project_name=name,
            harbor_role_id=HarborRoleID.MAINTAINER,
            comanage_person_id=coperson_id,
            comanage_group_member=True,
            comanage_group_owner=True
        )
        create_permission_group(
            group_name=f"soteria-{name}-developers",
            project_name=name,
            harbor_role_id=HarborRoleID.DEVELOPER,
            comanage_person_id=coperson_id,
            comanage_group_member=True,
            comanage_group_owner=True
        )
        create_permission_group(
            group_name=f"soteria-{name}-guests",
            project_name=name,
            harbor_role_id=HarborRoleID.GUEST,
            comanage_person_id=coperson_id,
            comanage_group_member=True,
            comanage_group_owner=True
        )
    except Exception as error:
        flask.current_app.logger.error(error)

    return project


def create_permission_group(
        group_name: str,
        project_name: str,
        harbor_role_id: HarborRoleID,
        comanage_person_id: int,
        comanage_group_member: bool,
        comanage_group_owner: bool,
        valid_through: Optional[datetime.datetime] = None
):
    """
    Creates a permissions group and assign provides access to the provided COmanage person
    """

    harbor_api = get_admin_harbor_api()
    comanage_api = get_admin_comanage_api()

    # Create Group in Harbor
    response = harbor_api.create_project_member(
        project_id_or_name=project_name,
        role=harbor_role_id,
        group_name=group_name
    )

    if not response.ok:
        raise Exception(f"Could not create Harbor group: {response.text}")

    # Create the group in Comanage
    response = comanage_api.create_group(group_name)

    if not response.ok:
        raise Exception(f"Could not create COmanage group: {response.text}")

    comanage_group = response.json()

    # Add the researcher to the groups
    response = comanage_api.add_group_member(
        comanage_group["Id"],
        comanage_person_id,
        member=comanage_group_member,
        owner=comanage_group_owner,
        valid_through=valid_through
    )

    if not response.ok:
        raise Exception(f"Could not add person to COmanage Group: {response.text}")


def get_comanage_person():
    """Get current users Comanage Person data"""
    comanage_api = get_admin_comanage_api()

    comanage_person = comanage_api.get_persons(identifier=get_sub()).json()

    if len(comanage_person["CoPeople"]) == 0:
        raise LookupError(
            "Could not find a Comanage account associated with this user"
        )

    return comanage_person["CoPeople"][0]

def get_email():
    """
    Returns the current user's email address.
    """
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_email")


def get_eppn() -> Optional[str]:
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_eppn")


def get_idp_name():
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_idp_name")


def get_name():
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_name")


def get_sub() -> Optional[str]:
    update_request_environ()

    return flask.request.environ.get("OIDC_CLAIM_sub")


def get_status() -> Literal["Researcher", "Member", "Affiliate", "Registration Incomplete", None]:
    if is_soteria_researcher():
        return "Researcher"
    elif is_soteria_member():
        return "Member"
    elif is_soteria_affiliate():
        return "Affiliate"
    elif not is_registered():
        return "Registration Incomplete"
    else:
        return None


def get_orcid_id():
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


#
# --------------------------------------------------------------------------
#


def get_starter_project_name():
    user = get_harbor_user()

    if user:
        return user["username"].lower() + "_temporary"
    return None


def has_organizational_identity() -> bool:
    groups = get_comanage_groups()

    return "CO:members:all" in groups

def is_registered() -> bool:
    orcid_id = get_orcid_id()
    harbor_user = get_harbor_user()
    is_in_soteria = is_in_soteria_cou()

    return all([is_in_soteria, orcid_id is not None, harbor_user is not None])


def is_in_soteria_cou():
    """Checks that a researcher is in the SOTERIA group, which is a superset of SOTERIA COU Groups"""
    groups = get_comanage_groups()

    return "SOTERIA" in groups


def is_soteria_affiliate() -> bool:
    groups = get_comanage_groups()

    return "CO:COU:SOTERIA-Affiliates:members:active" in groups


def is_soteria_member() -> bool:
    groups = get_comanage_groups()

    return "CO:COU:SOTERIA-Collaborators:members:active" in groups


def is_soteria_researcher() -> bool:
    groups = get_comanage_groups()

    return "CO:COU:SOTERIA-Researchers:members:active" in groups


#
# --------------------------------------------------------------------------
#


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
    return registry.comanage.COmanageAPI(
        flask.current_app.config["REGISTRY_API_URL"],
        flask.current_app.config["REGISTRY_CO_ID"],
        basic_auth=(
            flask.current_app.config["REGISTRY_API_USERNAME"],
            flask.current_app.config["REGISTRY_API_PASSWORD"],
        ),
    )


def get_freshdesk_api() -> registry.freshdesk.FreshDeskAPI:
    """
    Returns a Freshdesk API instance.
    """
    return registry.freshdesk.FreshDeskAPI(
        flask.current_app.config["FRESHDESK_API_KEY"]
    )
