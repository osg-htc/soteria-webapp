import pytest

from registry.harbor import HarborAPI
from config import HARBOR_ADMIN_USERNAME, HARBOR_ADMIN_PASSWORD, HARBOR_API_URL

api = HarborAPI(HARBOR_API_URL, (HARBOR_ADMIN_USERNAME, HARBOR_ADMIN_PASSWORD))


class TestHarborApi:

    def test__get(self):
        response = api._get("/projects")

        assert response.status_code == 200

    def test_create_project(self):
        response = api.create_project("pytest-create-project", public=True)

        assert response['name'] == "pytest-create-project"

    def test_create_project_member(self):
        response = api.create_project_member("pytest-create-project", 4, group_name="pytest-create-project-member")

        assert response.status_code == 201

    def test_get_project_member(self):
        project = api.get_project("pytest-create-project")

        response = api.get_all_project_members(project['project_id'])

        assert isinstance(response, list)
        assert "pytest-create-project-member" in set([x['entity_name'] for x in response])

    def test_delete_usergroup(self):
        project = api.get_project("pytest-create-project")

        response = api.get_all_project_members(project['project_id'])

        test_group = [*filter(lambda x: x["entity_name"] == "pytest-create-project-member", response)][0]

        response = api.delete_usergroup(test_group['entity_id'])

        assert response.status_code == 200

    def test_delete_project(self):
        response = api.delete_project("pytest-create-project")

        assert response.status_code == 200
