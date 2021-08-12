"""
Wrapper for Harbor's API.
"""

import logging
from typing import Any, List, Tuple, Union

import requests

__all__ = ["HarborAPI"]


class RestAPI:
    """
    Provides basic functionality for a REST API.

    The functionality includes: automatic instantiation and teardown of
    a `requests.Session` object, a logger, and a method that logs and sends
    an HTTP request.
    """

    def __init__(self, api_base_url: str, session: requests.Session = None):
        self._api_base_url = api_base_url
        self._session = session or requests.Session()
        self._is_own_session = not session

        self._log = logging.getLogger(__name__)
        self._log.addHandler(logging.NullHandler())

    def __del__(self):
        if self._is_own_session:
            self._session.close()

    def _request(self, method, url, **kwargs):
        """
        Logs and sends an HTTP request.

        Keyword arguments are passed through unmodified to the ``requests``
        library's ``request`` method. If the response contains a status code
        indicating failure, the response is still returned. Other failures
        result in an exception being raised.
        """
        self._log.info("%s %s", method.upper(), url)

        try:
            r = requests.request(method, url, **kwargs)
        except requests.RequestException as exn:
            self._log.exception(exn)
            raise

        return r

    def _delete(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("DELETE", f"{self._api_base_url}{route}", **kwargs)

    def _get(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("GET", f"{self._api_base_url}{route}", **kwargs)

    def _head(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("HEAD", f"{self._api_base_url}{route}", **kwargs)

    def _post(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("POST", f"{self._api_base_url}{route}", **kwargs)


class HarborAPI(RestAPI):
    """
    Minimal wrapper for Harbor's API.

    All calls will be made using the credentials provided to the constructor.
    """

    def __init__(
        self,
        api_base_url: str,
        basic_auth: Tuple[str, str] = None,
        session: requests.Session = None,
    ):
        """
        Constructs a wrapper that uses the provided credentials, if any.

        If a username and password are provided via `basic_auth`, API calls
        will be made using Basic authentication.
        """
        super().__init__(api_base_url, session=session)

        self._basic_auth = basic_auth

    def _request(self, *args, **kwargs):
        if self._basic_auth:
            if "auth" not in kwargs:
                kwargs["auth"] = self._basic_auth

        r = super()._request(*args, **kwargs)

        try:
            r.raise_for_status()
        except requests.HTTPError as exn:
            self._log.debug(exn)

        return r

    def get_all_users(self):
        """
        Get all users.
        """
        return self._get("/users").json()

    def get_user(self, user_id):
        """
        Get a user's profile.
        """
        return self._get(f"/users/{user_id}").json()

    def create_project(self, name: str, *, storage_limit: int = 5368709120):
        """
        Create a new private project, with the given user as an administrator.
        """
        payload = {
            "project_name": name,
            "public": False,
            "storage_limit": storage_limit,
        }

        r = self._post("/projects", json=payload)

        if not r.ok:
            return r.json()
        return self.get_project(name)

    def get_project(self, project_name_or_id: Union[int, str]):
        """
        Get a new project, either by name or by ID.
        """
        return self._get(f"/projects/{project_name_or_id}").json()

    def add_project_member(self, project_id: int, username: str, role_id: int = 2):
        payload = {
            "role_id": role_id,
            "member_user": {"username": username},
        }

        r = self._post(f"/projects/{project_id}/members", json=payload)

        if not r.ok:
            return r.json()
        return self.get_project_member(project_id, username)

    def get_project_member(self, project_id: int, username: str):
        params = {"entityname": username}

        r = self._get(f"/projects/{project_id}/members", params=params).json()

        for member in r:
            if member["entity_name"] == username:
                return member

        raise NotImplementedError

    def delete_project_member(self, project_id: int, username: str):
        member = self.get_project_member(project_id, username)

        r = self._delete(f"/projects/{project_id}/members/{member['id']}")

        if not r.ok:
            return r.json()

        return {}
