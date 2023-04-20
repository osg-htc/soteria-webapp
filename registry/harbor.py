"""
Wrapper for Harbor's API.
"""

import enum
import typing
from typing import Optional, Union

import registry.api_client

__all__ = ["HarborAPI", "HarborRoleID"]


class HarborRoleID(enum.IntEnum):
    PROJECT_ADMIN = 1
    DEVELOPER = 2
    GUEST = 3
    MAINTAINER = 4


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

        info_response = self._get(route, params={'page_size': 1})
        number_of_pages = (int(info_response.headers.get('x-total-count')) // PAGE_SIZE) + 1

        for i in range(1, number_of_pages + 1):
            values = self._get(route, **{
                **kwargs,
                'params': {'page': i, 'page_size': PAGE_SIZE, **kwargs.get("params", {})}
            }).json()
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

    def get_all_users(self, **kwargs) -> typing.Generator[dict, None, None]:
        """
        Returns a list of all users.

        Might not include data populated via OIDC.
        """
        return self._get_all("/users", **kwargs)

    def search_for_user(self, email: str, subiss: str):
        """
        Returns a user with the given email address and "subiss".
        """
        params = {
            "page_size": 100,
            "q": f"email=~{email}",  # email addresses are not case sensitive
        }
        users = self._get("/users", params=params).json()

        for u in users:
            user = self.get_user(u["user_id"])

            if user.get("oidc_user_meta", {}).get("subiss", "") == subiss:
                return user

        return None

    #
    # ----------------------------------------------------------------------
    #

    def create_project(
        self,
        name: str,
        is_public: bool = False,
        *,
        storage_limit: int = 5368709120,
    ):
        # 5 GiB = 5368709120 bytes = 5 * 1024 * 1024 * 1024
        """
        Create a new private project, with the given user as an administrator.
        """
        payload = {
            "project_name": name,
            "public": is_public,
            "storage_limit": storage_limit,
        }
        r = self._post("/projects", json=payload)

        if not r.ok:
            return r.json()
        return self.get_project(name)

    def get_project(self, project_id_or_name: Union[int, str]):
        """
        Get a new project, either by ID or by name.
        """
        return self._get(f"/projects/{project_id_or_name}").json()

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

        r = self._post(f"/projects/{project_id}/members", json=payload)

        if not r.ok:
            return r.json()
        return self.get_project_member(project_id, username)

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

    def get_all_project_members(self, project_id: Union[str, int]) -> typing.Generator[dict, None, None]:
        return self._get_all(f"/projects/{project_id}/members")

    def delete_project_member(self, project_id: int, username: str):
        member = self.get_project_member(project_id, username)

        r = self._delete(f"/projects/{project_id}/members/{member['id']}")

        if not r.ok:
            return r.json()
        return {}

    def delete_usergroup(self, usergroup_id: int):
        return self._delete(f"/usergroups/{usergroup_id}")
