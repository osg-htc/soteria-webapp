"""
Wrapper for Harbor's API.
"""

import datetime
import enum
import secrets
import time
import typing
from typing import List, Optional, Tuple, Union

import flask
import requests

import registry.api_client

__all__ = ["HarborAPI", "HarborRoleID"]

GIBIBYTE = 2**30


class HarborRoleID(enum.IntEnum):
    PROJECT_ADMIN = 1
    DEVELOPER = 2
    GUEST = 3
    MAINTAINER = 4


class Harbor:
    """
    QOL Wrapper around the Harbor API
    """

    def __init__(
        self,
        api_base_url: str = None,
        basic_auth: Optional[Tuple[str, str]] = None,
        harbor_api: "HarborAPI" = None,
    ):
        if harbor_api is not None:
            self.api = harbor_api
        else:
            self.api = HarborAPI(api_base_url=api_base_url, basic_auth=basic_auth)

    def create_project(
        self, name: str, public: bool = False, *, storage_limit: int = 5 * GIBIBYTE
    ):
        """Create project then return the project data"""

        response = self.api.create_project(
            name=name, public=public, storage_limit=storage_limit
        )

        if not response.ok:
            return response.json()

        self.set_webhooks(name)

        return self.api.get_project(project_id_or_name=name).json()

    def set_webhooks(self, project_id_or_name: str):
        self.api.delete_all_webhooks(project_id_or_name)

        app = flask.current_app
        url = f'{app.config["SOTERIA_API_URL"]}/webhooks/harbor'
        token = app.config["WEBHOOKS_HARBOR_BEARER_TOKEN"]

        self.api.create_webhook(
            project_id_or_name,
            "SOTERIA",
            "Triggers SOTERIA image processing pipelines",
            ["PUSH_ARTIFACT", "DELETE_ARTIFACT"],
            url,
            f"Bearer {token}",
        )

    def search_for_user(self, email: str, subiss: str):
        """
        Returns a user with the given email address and "subiss".
        """
        params = {
            "q": f"email=~{email}",  # email addresses are not case sensitive
        }

        all_users = self.api.get_all_users(params=params)

        for u in all_users:
            user = self.api.get_user(u["user_id"])

            if user.get("oidc_user_meta", {}).get("subiss", "") == subiss:
                return user

        return None

    def get_users_who_uploaded_an_artifact(self):
        """The number of unique individuals who have uploaded at least one container to the registry"""

        start = time.time()
        previous = start

        users_who_uploaded_an_artifact = []
        for user in self.api.get_all_users():
            username = user["username"]
            uploaded_artifacts = self.api.get_audit_logs(
                q=f"operation=create,resource_type=artifact,username={username}"
            ).json()
            if len(uploaded_artifacts) > 0:
                users_who_uploaded_an_artifact.append(user)

            print(
                f"Iteration {username}:\n\tSince Start: {time.time() - start}\n\tSince Previous: {time.time() - previous}"
            )
            previous = time.time()

        return users_who_uploaded_an_artifact


class HarborAPI(registry.api_client.GenericAPI):
    """
    Wrapper for Harbor's API.

    All calls will be made using the credentials provided to the constructor.
    """

    def _get_all(self, route, **kwargs) -> typing.Generator[dict, None, None]:
        """
        Iterates all pages and retrieves all resource in a route
        """
        PAGE_SIZE = 100

        info_response = self._get(route, params={"page_size": 1})
        number_of_pages = (int(info_response.headers.get("x-total-count")) // PAGE_SIZE) + 1

        for i in range(1, number_of_pages + 1):
            values = self._get(
                route,
                **{
                    **kwargs,
                    "params": {"page": i, "page_size": PAGE_SIZE, **kwargs.get("params", {})},
                },
            ).json()
            for value in values:
                yield value

    #
    # ----------------------------------------------------------------------
    #

    def get_user(self, user_id: int):
        """
        Returns a user's profile.
        """
        return self._get(f"/users/{user_id}").json()

    def get_users(self, q: str = None, sort: str = None, page: int = 1, page_size: int = 10):
        params = {"q": q, "sort": sort, "page": page, "page_size": page_size}

        return self._get("/users", params=params)

    def get_all_users(self, **kwargs) -> typing.Generator[dict, None, None]:
        """
        Returns a list of all users.

        Might not include data populated via OIDC.
        """
        return self._get_all("/users", **kwargs)

    #
    # Repositories
    # ----------------------------------------------------------------------
    #

    def get_repositories(
        self,
        project_name: str,
        q: str = None,
        sort: str = None,
        page: int = 1,
        page_size: int = 10,
    ):
        params = {"q": q, "sort": sort, "page": page, "page_size": page_size}

        return self._get(f"/projects/{project_name}/repositories", params=params)

    #
    # ----------------------------------------------------------------------
    #

    def create_project(
        self,
        name: str,
        public: bool = False,
        *,
        storage_limit: int = 5 * GIBIBYTE,
    ):
        # 5 GiB = 5368709120 bytes = 5 * 1024 * 1024 * 1024
        """
        Create a new private project, with the given user as an administrator.
        """
        payload = {
            "project_name": name,
            "public": public,
            "storage_limit": storage_limit,
        }

        return self._post("/projects", json=payload)

    def get_project(self, project_id_or_name: Union[int, str]):
        """
        Get a new project, either by ID or by name.
        """

        return self._get(f"/projects/{project_id_or_name}")

    def get_all_projects(self, **kwargs) -> typing.Generator[dict, None, None]:
        """
        Get all projects, purely internal function
        """
        return self._get_all("/projects", **kwargs)

    def delete_project(self, name: str):
        return self._delete(f"/projects/{name}")

    #
    # ----------------------------------------------------------------------
    #

    def add_project_member(
        self,
        project_id: int,
        username: str,
        role_id: int = 2,
    ):
        payload = {
            "role_id": role_id,
            "member_user": {"username": username},
        }

        return self._post(f"/projects/{project_id}/members", json=payload)

    def create_project_member(
        self,
        project_id_or_name: str,
        role: HarborRoleID,
        *,
        group_id: Optional[int] = None,
        group_name: Optional[str] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
    ):
        """Add/Create a new project member ( user or group )"""

        if (
            sum(
                map(
                    lambda x: x is not None,
                    [group_name, group_id, username, user_id],
                )
            )
            != 1
        ):
            raise ValueError(
                "Exactly one of group_name, group_id, username, and user_id can be input."
            )

        data = {
            "role_id": role,
            "member_group": {"group_name": group_name, "id": group_id},
            "member_user": {"username": username, "user_id": user_id},
        }

        return self._post(f"/projects/{project_id_or_name}/members", json=data)

    def get_project_member(self, project_id: int, username: str):
        params = {"entityname": username}

        r = self._get(f"/projects/{project_id}/members", params=params).json()

        for member in r:
            if member["entity_name"] == username:
                return member
        return None

    def get_all_project_members(
        self, project_id: Union[str, int]
    ) -> typing.Generator[dict, None, None]:
        return self._get_all(f"/projects/{project_id}/members")

    def delete_project_member(self, project_id: int, username: str):
        member = self.get_project_member(project_id, username)

        r = self._delete(f"/projects/{project_id}/members/{member['id']}")

        if not r.ok:
            return r.json()
        return {}

    def delete_usergroup(self, usergroup_id: int):
        return self._delete(f"/usergroups/{usergroup_id}")

    #
    # Robot Account
    # ----------------------------------------------------------------------
    #

    def create_project_robot_account(
        self,
        project_name: str,
        robot_name: str,
        level: str = None,
        duration: int = -1,
        description: str = None,
        list_repository: bool = False,
        pull_repository: bool = False,
        push_repository: bool = False,
        delete_repository: bool = False,
        list_artifact: bool = False,
        read_artifact: bool = False,
        delete_artifact: bool = False,
        create_artifact_label: bool = False,
        delete_artifact_label: bool = False,
        list_tag: bool = False,
        create_tag: bool = False,
        delete_tag: bool = False,
        create_scan: bool = False,
        stop_scan: bool = False,
        read_helm_chart: bool = False,
        create_helm_chart_version: bool = False,
        delete_helm_chart_version: bool = False,
        create_helm_chart_version_label: bool = False,
        delete_helm_chart_version_label: bool = False,
    ) -> Tuple[requests.Response, str]:
        level = "system" if level is None else level
        description = "" if description is None else description

        data = {
            "disable": False,
            "name": robot_name,
            "level": level,
            "duration": duration,
            "description": description,
            "permissions": [{"access": [], "kind": "project", "namespace": project_name}],
        }

        access_list = data["permissions"][0]["access"]

        if list_repository:
            access_list.append({"action": "list", "resource": "repository"})

        if pull_repository:
            access_list.append({"action": "pull", "resource": "repository"})

        if push_repository:
            access_list.append({"action": "push", "resource": "repository"})

        if delete_repository:
            access_list.append({"action": "delete", "resource": "repository"})

        if list_artifact:
            access_list.append({"action": "list", "resource": "artifact"})

        if read_artifact:
            access_list.append({"action": "read", "resource": "artifact"})

        if delete_artifact:
            access_list.append({"action": "delete", "resource": "artifact"})

        if create_artifact_label:
            access_list.append({"action": "create", "resource": "artifact-label"})

        if delete_artifact_label:
            access_list.append({"action": "delete", "resource": "artifact-label"})

        if list_tag:
            access_list.append({"action": "list", "resource": "tag"})

        if create_tag:
            access_list.append({"action": "create", "resource": "tag"})

        if delete_tag:
            access_list.append({"action": "delete", "resource": "tag"})

        if create_scan:
            access_list.append({"action": "create", "resource": "scan"})

        if stop_scan:
            access_list.append({"action": "stop", "resource": "scan"})

        if read_helm_chart:
            access_list.append({"action": "read", "resource": "helm-chart"})

        if create_helm_chart_version:
            access_list.append({"action": "create", "resource": "helm-chart-version"})

        if delete_helm_chart_version:
            access_list.append({"action": "delete", "resource": "helm-chart-version"})

        if create_helm_chart_version_label:
            access_list.append({"action": "create", "resource": "helm-chart-version-label"})

        if delete_helm_chart_version_label:
            access_list.append({"action": "delete", "resource": "helm-chart-version-label"})

        return self._post(f"/robots", json=data)

    def get_robots(
        self, q: str = None, sort: str = None, page: int = None, page_size: int = None
    ):
        params = {"q": q, "sort": sort, "page": page, "page_size": page_size}

        return self._get(f"/robots", params=params)

    def delete_robot(self, robot_id: int):
        return self._delete(f"/robots/{robot_id}")

    def get_robot(self, robot_id: int):
        return self._get(f"/robots/{robot_id}")

    #
    # Statistics
    # ----------------------------------------------------------------------
    #

    def get_statistics(self):
        return self._get("/statistics")

    #
    # Audit Logs
    # ----------------------------------------------------------------------
    #

    def get_audit_logs(
        self, q: str = None, sort: str = None, page: int = 1, page_size: int = 10
    ):
        params = {"q": q, "sort": sort, "page": page, "page_size": page_size}

        return self._get("/audit-logs", params=params)

    #
    # Scanner
    # ----------------------------------------------------------------------
    #

    def get_scanners(self, q: str = None, sort: str = None, page: int = 1, page_size: int = 10):
        params = {"q": q, "sort": sort, "page": page, "page_size": page_size}

        return self._get("/scanners", params=params)

    def get_all_scanners(self, q: str = None, sort: str = None):
        params = {"q": q, "sort": sort}

        return self._get_all("/scanners", params=params)

    #
    # Webhooks
    # ----------------------------------------------------------------------
    #

    def get_all_webhooks(self, project_id_or_name: Union[int, str]):
        return self._get_all(f"/projects/{project_id_or_name}/webhook/policies")

    def delete_all_webhooks(self, project_id_or_name: Union[int, str]):
        for hook in self.get_all_webhooks(project_id_or_name):
            project_id = hook["project_id"]
            id = hook["id"]
            self._delete(f"/projects/{project_id}/webhook/policies/{id}")

    def create_webhook(
        self,
        project_id_or_name: Union[int, str],
        name: str,
        description: str,
        event_types: List[str],
        url: str,
        auth_header: str,
    ):
        payload = {
            "name": name,
            "description": description,
            "enabled": True,
            "event_types": event_types,
            "targets": [
                {
                    "type": "http",
                    "address": url,
                    "skip_cert_verify": False,
                    "auth_header": auth_header,
                }
            ],
        }

        return self._post(f"/projects/{project_id_or_name}/webhook/policies", json=payload)
