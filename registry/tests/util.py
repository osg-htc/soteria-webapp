import flask
import pytest

from registry.app import create_app
from registry import util
from registry.harbor import HarborAPI
from registry.comanage import ComanageAPI

from config import HARBOR_ADMIN_USERNAME, HARBOR_ADMIN_PASSWORD, HARBOR_API_URL, REGISTRY_API_URL, REGISTRY_API_PASSWORD, REGISTRY_API_USERNAME, REGISTRY_CO_ID

harbor_api = HarborAPI(HARBOR_API_URL, (HARBOR_ADMIN_USERNAME, HARBOR_ADMIN_PASSWORD))
comanage_api = ComanageAPI(REGISTRY_API_URL, REGISTRY_CO_ID, (REGISTRY_API_USERNAME, REGISTRY_API_PASSWORD))


TEST_PROJECT = "test-project-11"

@pytest.fixture
def app() -> flask.Flask:
    app = create_app()
    app.debug = True

    yield app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


class TestUtil:

    def test_get_harbor_user(self, app):
        with app.test_request_context():
            assert util.get_harbor_user() is not None

    def test_get_user_from_ldap(self, app):
        with app.test_request_context():
            util.get_comanage_groups()

    def test_get_harbor_projects(self, app):
        with app.test_request_context():
            assert len(util.get_harbor_projects()) == 2

    def test_create_project(self, app):
        with app.test_request_context():

            project_name = "test-project-12"

            util.create_project(project_name, False)

            # Harbor
            ## Test that all the Harbor groups are appropriately allocated
            project = harbor_api.get_project(project_name)

            valid_group_names = {
                f'soteria-{project_name}-owners',
                f'soteria-{project_name}-maintainers',
                f'soteria-{project_name}-developers',
                f'soteria-{project_name}-guests'
            }
            project_members = harbor_api.get_all_project_members(project_id=project['project_id'])

            assert len(project_members) == 5

            for member in project_members:
                assert member['entity_name'] in valid_group_names or member['entity_name'] == "admin"

                # Clean up as we go
                if member['entity_name'] in valid_group_names:
                    harbor_api.delete_usergroup(member['entity_id'])

            harbor_api.delete_project(project_name)

            # Comanage
            coperson_id = util.get_coperson_id()

            response = comanage_api.get_groups(co_person_id=coperson_id)

            cogroups = response.json()['CoGroups']
            soteria_cogroups = [*filter(lambda x: x['Name'] in valid_group_names, cogroups)]

            for cogroup in soteria_cogroups:
                group_members_response = comanage_api.get_group_members(co_group_id=cogroup['Id'])
                group_members = group_members_response.json()['CoGroupMembers']

                assert group_members[0]['Person']['Id'] == coperson_id
                assert group_members[0]['Member'] == True
                if cogroup['Name'] != f'soteria-{project_name}-owners':
                    assert group_members[0]['Owner'] == True
                else:
                    assert group_members[0]['Owner'] == False

                # Clean up as we go
                comanage_api.delete_group(cogroup['Id'])

