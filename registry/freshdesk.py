import json
import logging

import requests

__all__ = ["FreshDeskAPI"]

BASE_URL = "https://opensciencegrid.freshdesk.com"


class FreshDeskAPI:
    """
    Minimal wrapper for FreshDesk's API. ( Copied from HARBORAPI )

    All calls will be made using the credentials provided to the constructor.
    """

    def __init__(self, api_key: str):

        self.session = requests.Session()
        self.api_key = api_key

        self.base_url = BASE_URL

        self.log = logging.getLogger(__name__)

    def _renew_session(self):
        if self.session:
            self.session.close()
        self.session = requests.Session()

    def _request(self, method, url, **kwargs):
        """
        Logs and sends an HTTP request.

        Keyword arguments are passed through unmodified to the ``requests``
        library's ``request`` method. If the response contains a status code
        indicating failure, the response is still returned. Other failures
        result in an exception being raised.
        """
        if self.api_key:
            if "auth" not in kwargs:
                kwargs["auth"] = (self.api_key, "X")

        self.log.info("%s %s", method.upper(), url)

        try:
            r = self.session.request(method, url, **kwargs)
        except requests.RequestException as exn:
            self.log.exception(exn)
            raise

        try:
            r.raise_for_status()
        except requests.HTTPError as exn:
            self.log.debug(exn)

        return r

    def _post(self, route, **kwargs):
        """
        Logs and sends an HTTP GET request for the given route.
        """
        self._renew_session()

        return self._request("POST", f"{self.base_url}{route}", **kwargs)

    def create_ticket(self, **kwargs):
        """
        Create a ticket
        """
        data = json.dumps(kwargs)
        headers = {"Content-Type": "application/json"}

        return self._post(f"/api/v2/tickets", data=data, headers=headers)
