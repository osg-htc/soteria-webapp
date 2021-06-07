"""
Wrapper for Harbor's API.
"""

import logging
from typing import Tuple

import requests
from flask import current_app

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

        Keyword arguments are passed through unmodified to the `requests`
        library's `request` method. If an HTTP error occurs, an exception
        is raised.
        """
        current_app.logger.info("%s %s", method.upper(), url)

        try:
            r = self._session.request(method, url, **kwargs)
            r.raise_for_status()
        except requests.RequestException as exn:
            current_app.logger.exception(exn)
        finally:
            return r

    def _get(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("GET", f"{self._api_base_url}{route}", **kwargs)


class HarborAPI(RestAPI):
    """
    Minimal wrapper for Harbor's API.

    All calls will be made using the credentials provided to the constructor.
    """

    def __init__(
        self,
        api_base_url: str,
        basic_auth: Tuple[str, str] = None,
        bearer_token: str = None,
        session: requests.Session = None,
    ):
        """
        Constructs a wrapper that uses the provided credentials, if any.

        If a username and password are provided via `basic_auth`, API calls
        will be made using Basic authentication.

        If an OIDC **ID** token is provided via `bearer_token`, API calls
        will be made using Bearer authentication. (NOTE: Normal practice is
        to provide an access token. Harbor's API works differently.)
        """
        super().__init__(api_base_url, session=session)

        self._basic_auth = basic_auth
        self._bearer_token = bearer_token

    def _request(self, *args, **kwargs):
        if self._basic_auth:
            if "auth" not in kwargs:
                kwargs["auth"] = self._basic_auth

        if self._bearer_token:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            if "authorization" not in kwargs["headers"]:
                kwargs["headers"]["authorization"] = f"Bearer {self._bearer_token}"

        return super()._request(*args, **kwargs)

    def user(self, user_id):
        """
        Get a user's profile.
        """
        return self._get(f"/users/{user_id}").json()

    def all_users(self):
        """
        Get all registered users.
        """
        return self._get("/users").json()

    def current_user(self):
        """
        Get the current user's profile.
        """
        return self._get("/users/current").json()
