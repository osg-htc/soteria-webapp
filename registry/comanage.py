'''
Wrapper for Comanage API
'''
import datetime
import logging
from typing import Any, List, Optional, Tuple, Union, Literal

import requests

__all__ = ['ComanageAPI']

import registry.comanage

class ComanageAPI:
    '''
    Minimal wrapper for Comanage's API.

    All calls will be made using the credentials provided to the constructor.
    '''

    def __init__(
        self,
        api_base_url: str,
        co_id: int,
        basic_auth: Optional[Tuple[str, str]] = None,
    ):
        '''
        Constructs a wrapper that uses the provided credentials, if any.

        If a username and password are provided via `basic_auth`, API calls
        will be made using Basic authentication.
        '''
        self._api_base_url = api_base_url
        self._co_id = co_id
        self._basic_auth = basic_auth

        self._session = requests.Session()

        self._log = logging.getLogger(__name__)
        self._log.addHandler(logging.NullHandler())

    def _renew_session(self):
        if self._session:
            self._session.close()
        self._session = requests.Session()

    def _request(self, method, url, **kwargs):
        '''
        Logs and sends an HTTP request.

        Keyword arguments are passed through unmodified to the ``requests``
        library's ``request`` method. If the response contains a status code
        indicating failure, the response is still returned. Other failures
        result in an exception being raised.
        '''
        if self._basic_auth:
            if 'auth' not in kwargs:
                kwargs['auth'] = self._basic_auth

        self._log.info('%s %s', method.upper(), url)

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
        '''
        Logs and sends an HTTP GET request for the given route.
        '''
        self._renew_session()

        return self._request('DELETE', f'{self._api_base_url}{route}', **kwargs)

    def _get(self, route, **kwargs):
        '''
        Logs and sends an HTTP GET request for the given route.
        '''
        return self._request('GET', f'{self._api_base_url}{route}', **kwargs)

    def _head(self, route, **kwargs):
        '''
        Logs and sends an HTTP GET request for the given route.
        '''
        return self._request('HEAD', f'{self._api_base_url}{route}', **kwargs)

    def _post(self, route, **kwargs):
        '''
        Logs and sends an HTTP GET request for the given route.
        '''
        self._renew_session()

        return self._request('POST', f'{self._api_base_url}{route}', **kwargs)

    def get_group(self, group_id: int):
        return self._get(f'co_groups/{group_id}.json')

    def get_groups(self, coperson_id: int = None, search_identifier: str = None):
        return self._get(
            'co_groups.json',
            params={'coid': self._co_id, 'copersonid': coperson_id, 'search.identifier': search_identifier}
        )

    def create_group(self, name: str, description: str = None, open: bool = False,
                     status: Literal['Active', 'Suspended'] = None, cou_id: str = None):
        '''
        Creates a group in Comanage
        '''

        # https://spaces.at.internet2.edu/display/COmanage/CoGroup+Schema
        data = {
            'RequestType': 'CoGroups',
            'Version': '1.0',
            'CoGroups':
            [{
                'Version': '1.0',
                'CoId': self._co_id,
                'Name': name,
                'Description': description if description is not None else '',
                'Open': open,
                'Status': status if status is not None else 'Active',
                'CouId': cou_id
            }]
        }

        return self._post('co_groups.json', json=data)

    def delete_group(self, group_id: int):
        return self._delete(f'co_groups/{group_id}.json')

    def create_person(self, tz: str = None, dob: str = None,
                      status: Literal['Active','Approved','Confirmed','Declined','Deleted','Denied','Duplicate','Expired','GracePeriod','Invited','Locked','Pending','PendingApproval','PendingConfirmation','PendingVetting','Suspended'] = None ):

        if status is None:
            raise ValueError("Must have a valid value for status.")

        data = {
            'RequestType': 'CoPeople',
            'Version': '1.0',
            'CoPeople': [{
                'Version': '1.0',
                'CoId': self._co_id,
                'Timezone': tz,
                'DateOfBirth': dob,
                'Status': status
            }]
        }

        return self._post('co_people.json', json=data)

    def get_person(self, person_id: int):
        return self._get(f"co_people/{person_id}.json")

    def get_persons(self, email_address: str = None, identifier: str = None):
        params = {
            'coid': self._co_id,
            'search.mail': email_address,
            'search.identifier': identifier
        }

        return self._get('co_people.json', params=params)

    def delete_person(self, person_id: int):
        return self._delete(f"co_people/{person_id}.json")

    def get_group_members(self, co_group_id: str = None, coperson_id: int = None):
        if co_group_id is not None and coperson_id is not None:
            raise ValueError("co_group_id and coperson_id must be used exclusively")

        params = {
            'cogroupid': co_group_id,
            'copersonid': coperson_id
        }

        return self._get('co_group_members.json', params=params)

    def add_group_member(self, group_id: int, user_id: int, member: bool, owner: bool,
                         valid_through: datetime.datetime = None, valid_from: datetime.datetime = None):

        data = {
            'RequestType': 'CoGroupMembers',
            'Version': '1.0',
            'CoGroupMembers': [{
                'Version': '1.0',
                'CoGroupId': group_id,
                'Person': {
                    'Type': 'CO',
                    'Id': user_id
                },
                'Member': member,
                'Owner': owner,
                'ValidFrom': valid_from,
                'ValidThrough': valid_through
            }]
        }

        return self._post('co_group_members.json', json=data)
