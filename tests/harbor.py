import pytest
import time
from config import (
    HARBOR_ADMIN_PASSWORD,
    HARBOR_ADMIN_USERNAME,
    HARBOR_API_URL,
    MOCK_OIDC_CLAIM,
)

from registry.harbor import Harbor, HarborAPI

api = HarborAPI(HARBOR_API_URL, (HARBOR_ADMIN_USERNAME, HARBOR_ADMIN_PASSWORD))
harbor = Harbor(harbor_api=api)

TEST_PROJECT_NAME = "pytest-test-project"
TEST_ROBOT_NAME = "pytest-test-robot"


@pytest.fixture()
def project():
    """Creates then deletes a harbor project to be used for testing"""

    response = harbor.api.create_project(name=TEST_PROJECT_NAME, public=False)

    if response.status_code != 201:
        raise Exception("Error: project() fixture is broken")

    data = harbor.api.get_project(TEST_PROJECT_NAME).json()

    yield data

    response = api.delete_project(TEST_PROJECT_NAME)

    if response.status_code != 200:
        raise Exception(f"Error: Failed to delete project {TEST_PROJECT_NAME}")


@pytest.fixture()
def clean_up_project():
    response = api.delete_project(TEST_PROJECT_NAME)

    if response.status_code != 200:
        raise Exception(f"Error: Failed to delete project {TEST_PROJECT_NAME}")


@pytest.fixture()
def project_clean_up():
    """Cleans up a created project if the test fails"""

    yield None

    api.delete_project(TEST_PROJECT_NAME)


@pytest.fixture()
def robot_clean_up():
    """Cleans up a created robot it the test fails"""

    yield None

    test_robot = api.get_robots(q=f"name={TEST_ROBOT_NAME}").json()[0]
    api.delete_robot(test_robot['id'])


class TestHarbor:
    """Test the QOL harbor api wrapper"""

    def test_create_project(self, project_clean_up):

        project = harbor.create_project(TEST_PROJECT_NAME)

        assert project['name'] == TEST_PROJECT_NAME

    def test_search_for_user(self):
        subiss = MOCK_OIDC_CLAIM['OIDC_CLAIM_sub'] + MOCK_OIDC_CLAIM['OIDC_CLAIM_iss']
        email = MOCK_OIDC_CLAIM['OIDC_CLAIM_email']

        user = harbor.search_for_user(subiss=subiss, email=email)

        assert user['email'] == email
        assert user['oidc_user_meta']['subiss'] == subiss


class TestHarborApi:

    def test_project_fixture(self, project):
        assert True

    def test__get(self):
        response = api._get("/projects")

        assert response.status_code == 200

    def test_create_project(self, project_clean_up):

        response = api.create_project(TEST_PROJECT_NAME, public=True)

        assert response.status_code == 201

        response = api.get_project(TEST_PROJECT_NAME)

        assert response.status_code == 200

        response = api.delete_project(TEST_PROJECT_NAME)

        assert response.status_code == 200

    def test_create_project_member(self):
        response = api.create_project_member(
            "pytest-create-project",
            4,
            group_name="pytest-create-project-member",
        )

        assert response.status_code == 201

    def test_get_project_member(self):
        project = api.get_project("pytest-create-project").json()

        response = api.get_all_project_members(project["project_id"])

        assert "pytest-create-project-member" in set(
            [x["entity_name"] for x in [*response]]
        )

    def test_delete_usergroup(self):
        project = api.get_project("pytest-create-project").json()

        response = api.get_all_project_members(project["project_id"])

        test_group = [
            *filter(
                lambda x: x["entity_name"] == "pytest-create-project-member",
                response,
            )
        ][0]

        response = api.delete_usergroup(test_group["entity_id"])

        assert response.status_code == 200

    def test_delete_project(self):
        response = api.delete_project("pytest-create-project")

        assert response.status_code == 200

    def test_get_robots(self):
        response = api.get_robots()

        assert response.status_code == 200

        robots = response.json()

        assert len(robots) > 0

    def test_get_robot(self):
        test_robot = api.get_robots().json()[0]

        refetched_robot_response = api.get_robot(test_robot['id'])

        assert refetched_robot_response.status_code == 200

        refetched_robot = refetched_robot_response.json()

        assert test_robot == refetched_robot

    def test_create_robot(self, project, robot_clean_up):

        response = api.create_project_robot_account(
            project_name=TEST_PROJECT_NAME,
            robot_name=TEST_ROBOT_NAME,
            description="Test Description",
            list_repository=True,
            pull_repository=True,
            push_repository=True,
            delete_repository=True,
            list_artifact=True,
            read_artifact=True,
            delete_artifact=True,
            create_artifact_label=True,
            delete_artifact_label=True,
            list_tag=True,
            create_tag=True,
            delete_tag=True,
            create_scan=True,
            stop_scan=True,
            read_helm_chart=True,
            create_helm_chart_version=True,
            delete_helm_chart_version=True,
            create_helm_chart_version_label=True,
            delete_helm_chart_version_label=True
        )

        assert response.status_code == 201

        new_robot_response = api.get_robots(q=f"name={TEST_ROBOT_NAME}")

        assert new_robot_response.status_code == 200

        new_robot = new_robot_response.json()[0]

        assert new_robot['name'] == f"robot${TEST_ROBOT_NAME}"
        assert new_robot['permissions'][0]['kind'] == "project"
        assert new_robot['permissions'][0]['namespace'] == TEST_PROJECT_NAME

        robot_access = new_robot['permissions'][0]['access']

        assert {'action': 'list', 'resource': 'repository'} in robot_access
        assert {'action': 'pull', 'resource': 'repository'} in robot_access
        assert {'action': 'push', 'resource': 'repository'} in robot_access
        assert {'action': 'delete', 'resource': 'repository'} in robot_access
        assert {'action': 'list', 'resource': 'artifact'} in robot_access
        assert {'action': 'read', 'resource': 'artifact'} in robot_access
        assert {'action': 'delete', 'resource': 'artifact'} in robot_access
        assert {'action': 'create', 'resource': 'artifact-label'} in robot_access
        assert {'action': 'delete', 'resource': 'artifact-label'} in robot_access
        assert {'action': 'list', 'resource': 'tag'} in robot_access
        assert {'action': 'create', 'resource': 'tag'} in robot_access
        assert {'action': 'delete', 'resource': 'tag'} in robot_access
        assert {'action': 'create', 'resource': 'scan'} in robot_access
        assert {'action': 'stop', 'resource': 'scan'} in robot_access
        assert {'action': 'read', 'resource': 'helm-chart'} in robot_access
        assert {'action': 'create', 'resource': 'helm-chart-version'} in robot_access
        assert {'action': 'delete', 'resource': 'helm-chart-version'} in robot_access
        assert {'action': 'create', 'resource': 'helm-chart-version-label'} in robot_access
        assert {'action': 'delete', 'resource': 'helm-chart-version-label'} in robot_access

    def test_robot_permissions(self, project, robot_clean_up):

        response = api.create_project_robot_account(
            project_name=TEST_PROJECT_NAME,
            robot_name=TEST_ROBOT_NAME,
            description="Test Description",
            list_repository=True
        )

        secret = response.json()['secret']
        robot_api = HarborAPI(HARBOR_API_URL, ("robot$" + TEST_ROBOT_NAME, secret))

        response = robot_api.get_repositories(project_name=TEST_PROJECT_NAME)

        assert response.status_code == 200