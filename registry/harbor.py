import logging
from typing import Tuple

import requests

__all__ = ["HarborAPI"]


class RestAPI:
    """
    Provides basic functionality for a REST API.

    The functionality includes: automatic instantiation and teardown of
    a `requests.Session` object, a logger, and a method that logs and sends
    an HTTP request.
    """

    def __init__(self, api_server: str, session: requests.Session = None):
        self._api_server = api_server
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
        self._log.info("%s %s %s", method.upper(), url, kwargs)

        try:
            r = self._session.request(method, url, **kwargs)
            r.raise_for_status()
        except requests.RequestException:
            self._log.exception("%s %s %s", method, url, kwargs)
            raise
        else:
            return r

    def _get(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("GET", f"{self._api_server}{route}", **kwargs)


class HarborAPI(RestAPI):
    def __init__(
        self,
        api_server: str,
        auth: Tuple[str, str] = None,
        token: str = None,
        session: requests.Session = None,
    ):
        super().__init__(api_server, session=session)

        self._auth = auth
        self._token = token

    def _request(self, *args, **kwargs):
        if self._auth:
            if "auth" not in kwargs:
                kwargs["auth"] = self._auth

        if self._token:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            if "authorization" not in kwargs["headers"]:
                kwargs["headers"]["authorization"] = f"Bearer {self._token}"

        return super()._request(*args, **kwargs)
