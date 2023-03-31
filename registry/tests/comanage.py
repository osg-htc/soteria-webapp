import pytest
import re

from registry.comanage import ComanageAPI
from config import REGISTRY_API_URL, REGISTRY_API_PASSWORD, REGISTRY_API_USERNAME, REGISTRY_CO_ID

api = ComanageAPI(REGISTRY_API_URL, REGISTRY_CO_ID, (REGISTRY_API_USERNAME, REGISTRY_API_PASSWORD))

# Steal these from a user in the registry
COMANAGE_USER_EMAIL = "CLOCK@WISC.EDU"
COMANAGE_USER_EPPN = "clock@wisc.edu"
COMANAGE_USER_SUB = "http://cilogon.org/serverA/users/46022246"


@pytest.fixture()
def group():
    """Creates the deletes a comanage group to be used for testing"""
    response = api.create_group(name="Pytest-Test-Group", description="Test Description")

    if response.status_code != 201:
        raise Exception("Error: group() fixture is broken")

    data = response.json()

    yield data

    response = api.delete_group(data['Id'])

    if response.status_code != 200:
        raise Exception("Error: Have to manually remove 'Pytest-Test-Group' in Comanage")


@pytest.fixture()
def person():
    """Creates then deletes a comanage person to be used for testing"""

    response = api.create_person(status="Active")

    if response.status_code != 201:
        raise Exception("Error: person() fixture is broken")

    data = response.json()

    yield data

    response = api.delete_person(data['Id'])

    if response.status_code != 200:
        raise Exception(f"Error: Failed to delete user {data['Id']}")


class TestComanageApi:

    @pytest.mark.skip(reason="Used to clean up test groups made during ~testing~")
    def test_cleanup(self):
        cogroups = api.get_groups().json()['CoGroups']

        test_group_pattern = re.compile('^soteria-test-.*')
        soteria_test_groups = [*filter(lambda x: test_group_pattern.match(x['Name']), cogroups)]
        for cogroup in soteria_test_groups:
            if test_group_pattern.match(cogroup['Name']):
                api.delete_group(cogroup['Id'])

    def test__get(self):
        response = api._get("co_groups.json", params={'coid': 8})

        assert response.status_code == 200

    def test_get_group(self, group):
        response = api.get_group(group['Id'])

        assert response.status_code == 200

        data = response.json()

        assert isinstance(data, dict)
        assert data['ResponseType'] == "CoGroups"
        assert isinstance(data['CoGroups'], list)
        assert data['CoGroups'][0]['Id'] == group['Id']

    def test_get_groups(self):

        response = api.get_groups()

        assert response.status_code == 200

        data = response.json()

        assert isinstance(data, dict)
        assert data['ResponseType'] == "CoGroups"
        assert isinstance(data['CoGroups'], list)

    @pytest.mark.skip(reason="Works once, then Group Name is Duplicated. See test_create_delete_group.")
    def test_create_group(self):

        response = api.create_group(name="Pytest-Soteria-Group", description="Test Description")

        assert response.status_code == 201

    def test_create_delete_group(self):

        group_name = "Pytest-Soteria-Group-Delete"
        group_description = "Pytest-Soteria-Group-Delete Description"

        response = api.create_group(name=group_name, description=group_description)

        assert response.status_code == 201

        data = response.json()
        group_id = data['Id']

        group_response = api.get_group(group_id)

        assert group_response.status_code == 200

        group_data = group_response.json()

        assert group_data['CoGroups'][0]['Name'] == group_name
        assert group_data['CoGroups'][0]['Description'] == group_description

        delete_response = api.delete_group(group_id)

        assert delete_response.status_code == 200

    def test_create_person(self):
        response = api.create_person(status="Active")

        assert response.status_code == 201

    def test_get_persons(self):
        response = api.get_persons()

        assert response.status_code == 200

    def test_get_person(self, person):
        response = api.get_person(person['Id'])

        assert response.status_code == 200

    def test_get_person_by_identifier(self):
        response = api.get_persons(identifier=COMANAGE_USER_SUB)

        assert response.status_code == 200

        data = response.json()

        assert len(data['CoPeople']) > 1

    def test_get_group_members(self, group, person):
        response = api.get_group_members(group['Id'])

        assert response.status_code == 204  # This should be an empty group

    def test_add_member_to_group(self, group, person):

        response = api.add_group_member(group['Id'], person['Id'], True, True)

        assert response.status_code == 201

        response = api.get_group_members(group['Id'])

        assert response.status_code == 200

        data = response.json()
        assert data['CoGroupMembers'][0]['Person']['Id'] == person['Id']

        data = api.get_group_members(group['Id']).json()

        assert data['CoGroupMembers'][0]['Member']
        assert data['CoGroupMembers'][0]['Owner']
