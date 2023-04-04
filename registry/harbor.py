"""
Wrapper for Harbor's API.
"""

import logging
from typing import Any, List, Optional, Tuple, Union, Literal

import requests

__all__ = ["HarborAPI"]


class HarborRoleIds:
    project_admin = 1
    developer = 2
    guest = 3
    maintainer = 4


class HarborAPI:
    """
    Minimal wrapper for Harbor's API.

    All calls will be made using the credentials provided to the constructor.
    """

    def __init__(
        self,
        api_base_url: str,
        basic_auth: Optional[Tuple[str, str]] = None,
    ):
        """
        Constructs a wrapper that uses the provided credentials, if any.

        If a username and password are provided via `basic_auth`, API calls
        will be made using Basic authentication.
        """
        self._api_base_url = api_base_url
        self._basic_auth = basic_auth

        self._session = requests.Session()

        self._log = logging.getLogger(__name__)
        self._log.addHandler(logging.NullHandler())

    def _renew_session(self):
        if self._session:
            self._session.close()
        self._session = requests.Session()

    def _request(self, method, url, **kwargs):
        """
        Logs and sends an HTTP request.

        Keyword arguments are passed through unmodified to the ``requests``
        library's ``request`` method. If the response contains a status code
        indicating failure, the response is still returned. Other failures
        result in an exception being raised.
        """
        if self._basic_auth:
            if "auth" not in kwargs:
                kwargs["auth"] = self._basic_auth

        self._log.info("%s %s", method.upper(), url)

        try:
            r = self._session.request(method, url, **kwargs)
        except requests.RequestException as exn:
            self._log.exception(exn)
            raise

        try:
            r.raise_for_status()
        except requests.HTTPError as exn:
            self._log.debug(exn)

        return r

    def _delete(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        self._renew_session()

        return self._request("DELETE", f"{self._api_base_url}{route}", **kwargs)

    def _get(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("GET", f"{self._api_base_url}{route}", **kwargs)

    def _get_all(self, route, **kwargs):
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




    def _head(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("HEAD", f"{self._api_base_url}{route}", **kwargs)

    def _post(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        self._renew_session()

        return self._request("POST", f"{self._api_base_url}{route}", **kwargs)

    def get_all_users(self, **kwargs):
        """
        Get all users, internal use only
        """
        return self._get_all("/users", **kwargs)

    def get_user(self, user_id):
        """
        Get a user's profile.
        """
        return self._get(f"/users/{user_id}").json()

    def create_project(self, name: str, public: bool = False, *, storage_limit: int = 5368709120):
        ## 5368709120 bytes = 1024 * 1024 * 1024
        """
        Create a new private project, with the given user as an administrator.
        """
        payload = {
            "project_name": name,
            "public": public,
            "storage_limit": storage_limit,
        }

        r = self._post("/projects", json=payload)

        if not r.ok:
            return r.json()
        return self.get_project(name)

    def delete_project(self, name: str):
        return self._delete(f"/projects/{name}")

    def get_all_projects(self, **kwargs):
        """
        Get all projects, purely internal function
        """
        return self._get_all("/projects", **kwargs)

    def get_project(self, project_name_or_id: Union[int, str]):
        """
        Get a new project, either by name or by ID.
        """
        return self._get(f"/projects/{project_name_or_id}").json()

    def list_projects(
            self, q: str=None, page: int=None, page_size: int=None, sort: str=None, name: str=None,
            public: bool=None, owner: str=None, with_detail: bool=None
    ):
        return self._get("/projects", params={
            "q": q,
            "page": page,
            "page_size": page_size,
            "sort": sort,
            "name": name,
            "public": public,
            "owner": owner,
            "with_detail": with_detail
        })

    def add_project_member(self, project_id: int, username: str, role_id: int = 2):
        payload = {
            "role_id": role_id,
            "member_user": {"username": username},
        }

        r = self._post(f"/projects/{project_id}/members", json=payload)

        if not r.ok:
            return r.json()
        return self.get_project_member(project_id, username)

    def create_project_member(self, project_name_or_id: str, role: Literal[1,2,3,4], group_id: int = None,
                              group_name: str = None, user_id: int = None, username: str = None):
        """Add/Create a new project member ( user or group )"""

        if sum(map(lambda x: x is not None, [group_name, group_id, username, user_id])) != 1:
            raise ValueError("Exactly one of group_name, group_id, username, and user_id can be input.")

        data = {
            "role_id": role,
            "member_group": {
                "group_name": group_name,
                "id": group_id
            },
            "member_user": {
                "username": username,
                "user_id": user_id
            }
        }

        return self._post(f"/projects/{project_name_or_id}/members", json=data)

    def get_project_member(self, project_id: int, username: str):
        params = {"entityname": username}

        r = self._get(f"/projects/{project_id}/members", params=params).json()

        for member in r:
            if member["entity_name"] == username:
                return member

        return None

    def get_all_project_members(self, project_id: Union[str, int]):

        return self._get_all(f"/projects/{project_id}/members")

    def delete_project_member(self, project_id: int, username: str):
        member = self.get_project_member(project_id, username)

        r = self._delete(f"/projects/{project_id}/members/{member['id']}")

        if not r.ok:
            return r.json()

        return {}

    def delete_usergroup(self, usergroup_id: int):
        return self._delete(f"/usergroups/{usergroup_id}")
