"""
Base class for a wrapper around a REST API.
"""

import logging
from typing import Optional, Tuple

import requests

__all__ = ["GenericAPI"]


class GenericAPI:
    # pylint: disable=too-few-public-methods
    """
    Base class for a wrapper around a REST API.

    All calls will be made using the credentials provided to the constructor.
    """

    def __init__(
        self,
        api_base_url: str,
        basic_auth: Optional[Tuple[str, str]] = None,
    ):
        """
        Constructs a wrapper that uses the provided credentials.

        If a username and password are provided via `basic_auth`, API calls
        will be made using Basic authentication.
        """
        self._api_base_url = api_base_url
        self._basic_auth = basic_auth

        self._session = requests.Session()

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.addHandler(logging.NullHandler())

    def _renew_session(self) -> None:
        """
        Hack for avoiding tracking XSRF tokens.
        """
        if self._session:
            self._session.close()
        self._session = requests.Session()

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Logs and sends an HTTP request.

        Keyword arguments are passed through unmodified to the `requests`
        library's `request` method. If the response contains an error
        status code, the response is still returned. Other failures result
        in an exception being raised.
        """
        if self._basic_auth:
            if "auth" not in kwargs:
                kwargs["auth"] = self._basic_auth

        self._log.info("%s %s", method.upper(), url)

        try:
            r = self._session.request(method, url, **kwargs)
        except requests.RequestException:
            self._log.exception("Unexpected `requests` error")
            raise

        # NOTE: Responses can include secrets, so it is not safe to log them
        # here without sanitizing them.

        try:
            r.raise_for_status()
        except requests.HTTPError as exn:
            self._log.info("HTTP Error: %s", exn)

        return r

    def _delete(self, route: str, **kwargs) -> requests.Response:
        """
        Logs and sends an HTTP DELETE request for the given route.
        """
        self._renew_session()

        return self._request("DELETE", f"{self._api_base_url}{route}", **kwargs)

    def _get(self, route: str, **kwargs) -> requests.Response:
        """
        Logs and sends an HTTP GET request for the given route.
        """
        return self._request("GET", f"{self._api_base_url}{route}", **kwargs)

    def _head(self, route: str, **kwargs) -> requests.Response:
        """
        Logs and sends an HTTP HEAD request for the given route.
        """
        return self._request("HEAD", f"{self._api_base_url}{route}", **kwargs)

    def _post(self, route: str, **kwargs) -> requests.Response:
        """
        Logs and sends an HTTP POST request for the given route.
        """
        self._renew_session()

        return self._request("POST", f"{self._api_base_url}{route}", **kwargs)
