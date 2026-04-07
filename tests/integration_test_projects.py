"""
Integration tests for Projects Service
"""
import requests
import uuid

BASE_URL = "http://localhost:8007"

class TestHealthEndpoints:
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/health/")
        assert response.status_code == 200

class TestProjectEndpoints:
    def test_list_projects_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/projects/projects/")
        assert response.status_code in [401, 403]
    
    def test_create_project_requires_auth(self):
        response = requests.post(f"{BASE_URL}/api/projects/projects/", json={})
        assert response.status_code in [400, 401, 403]
    
    def test_project_detail_requires_auth(self):
        project_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/projects/projects/{project_id}/")
        assert response.status_code in [401, 403, 404]

class TestTaskEndpoints:
    def test_list_tasks_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/projects/tasks/")
        assert response.status_code in [401, 403]
    
    def test_create_task_requires_auth(self):
        response = requests.post(f"{BASE_URL}/api/projects/tasks/", json={})
        assert response.status_code in [400, 401, 403]
    
    def test_task_detail_requires_auth(self):
        task_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/projects/tasks/{task_id}/")
        assert response.status_code in [401, 403, 404]

class TestIssueEndpoints:
    def test_list_issues_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/projects/issues/")
        assert response.status_code in [401, 403]
    
    def test_create_issue_requires_auth(self):
        response = requests.post(f"{BASE_URL}/api/projects/issues/", json={})
        assert response.status_code in [400, 401, 403]
    
    def test_issue_detail_requires_auth(self):
        issue_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/projects/issues/{issue_id}/")
        assert response.status_code in [401, 403, 404]

class TestTimelogEndpoints:
    def test_list_timelogs_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/projects/timelogs/")
        assert response.status_code in [401, 403]
    
    def test_create_timelog_requires_auth(self):
        response = requests.post(f"{BASE_URL}/api/projects/timelogs/", json={})
        assert response.status_code in [400, 401, 403]
