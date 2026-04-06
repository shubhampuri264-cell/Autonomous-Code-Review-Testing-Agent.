"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestRunEndpoints:
    @pytest.mark.skip(reason="Requires auth setup")
    def test_trigger_run_requires_auth(self):
        response = client.post("/api/runs/trigger", json={"repository_id": "test"})
        assert response.status_code == 401

    @pytest.mark.skip(reason="Requires auth setup")
    def test_get_run_not_found(self):
        response = client.get("/api/runs/nonexistent")
        assert response.status_code == 404
