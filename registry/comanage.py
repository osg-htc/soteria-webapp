"""
Wrapper for COmanage's API.
"""
import datetime
from typing import Literal, Optional, Tuple

import registry.api_client

__all__ = ["COmanageAPI"]


class COmanageAPI(registry.api_client.GenericAPI):
    """
    Wrapper for COmanage's API.

    All calls will be made using the credentials provided to the constructor.
    """

    def __init__(
        self,
        api_base_url: str,
        co_id: int,
        basic_auth: Optional[Tuple[str, str]] = None,
    ):
        """
        Constructs a wrapper that uses the provided credentials, if any.

        If a username and password are provided via `basic_auth`, API calls
        will be made using Basic authentication.
        """
        super().__init__(api_base_url, basic_auth)

        self._co_id = co_id

    def get_group(self, group_id: int):
        return self._get(f"co_groups/{group_id}.json")

    def get_groups(
        self,
        coperson_id: Optional[int] = None,
        search_identifier: Optional[str] = None,
    ):
        return self._get(
            "co_groups.json",
            params={
                "coid": self._co_id,
                "copersonid": coperson_id,
                "search.identifier": search_identifier,
            },
        )

    def create_group(
        self,
        name: str,
        description: str = "",
        open: bool = False,
        status: Optional[Literal["Active", "Suspended"]] = None,
        cou_id: Optional[str] = None,
    ):
        """
        Creates a group in Comanage
        """

        # https://spaces.at.internet2.edu/display/COmanage/CoGroup+Schema
        data = {
            "RequestType": "CoGroups",
            "Version": "1.0",
            "CoGroups": [
                {
                    "Version": "1.0",
                    "CoId": self._co_id,
                    "Name": name,
                    "Description": description,
                    "Open": open,
                    "Status": status if status is not None else "Active",
                    "CouId": cou_id,
                }
            ],
        }

        return self._post("co_groups.json", json=data)

    def delete_group(self, group_id: int):
        return self._delete(f"co_groups/{group_id}.json")

    def create_person(
        self,
        tz: Optional[str] = None,
        dob: Optional[str] = None,
        status: Optional[
            Literal[
                "Active",
                "Approved",
                "Confirmed",
                "Declined",
                "Deleted",
                "Denied",
                "Duplicate",
                "Expired",
                "GracePeriod",
                "Invited",
                "Locked",
                "Pending",
                "PendingApproval",
                "PendingConfirmation",
                "PendingVetting",
                "Suspended",
            ]
        ] = None,
    ):
        if status is None:
            raise ValueError("Must have a valid value for status.")

        data = {
            "RequestType": "CoPeople",
            "Version": "1.0",
            "CoPeople": [
                {
                    "Version": "1.0",
                    "CoId": self._co_id,
                    "Timezone": tz,
                    "DateOfBirth": dob,
                    "Status": status,
                }
            ],
        }

        return self._post("co_people.json", json=data)

    def get_person(self, person_id: int):
        return self._get(f"co_people/{person_id}.json")

    def get_persons(
        self,
        email_address: Optional[str] = None,
        identifier: Optional[str] = None,
    ):
        params = {
            "coid": self._co_id,
            "search.mail": email_address,
            "search.identifier": identifier,
        }

        return self._get("co_people.json", params=params)

    def delete_person(self, person_id: int):
        return self._delete(f"co_people/{person_id}.json")

    def get_group_members(
        self,
        co_group_id: Optional[str] = None,
        coperson_id: Optional[int] = None,
    ):
        if co_group_id is not None and coperson_id is not None:
            raise ValueError(
                "co_group_id and coperson_id must be used exclusively"
            )

        params = {"cogroupid": co_group_id, "copersonid": coperson_id}

        return self._get("co_group_members.json", params=params)

    def add_group_member(
        self,
        group_id: int,
        user_id: int,
        member: bool,
        owner: bool,
        valid_through: Optional[datetime.datetime] = None,
        valid_from: Optional[datetime.datetime] = None,
    ):
        data = {
            "RequestType": "CoGroupMembers",
            "Version": "1.0",
            "CoGroupMembers": [
                {
                    "Version": "1.0",
                    "CoGroupId": group_id,
                    "Person": {"Type": "CO", "Id": user_id},
                    "Member": member,
                    "Owner": owner,
                    "ValidFrom": valid_from,
                    "ValidThrough": valid_through,
                }
            ],
        }

        return self._post("co_group_members.json", json=data)
