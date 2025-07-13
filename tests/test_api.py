import pytest
from fastapi.testclient import TestClient
from cyprus.api.server import app

@pytest.fixture
def client():
    """Provides a test client for the API."""
    return TestClient(app)

def test_read_root(client):
    """Test the root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Cyprus API. Docs are available at /docs"}

def test_get_all_models(client):
    """Test the main /models endpoint."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check for one of the models from the registry
    assert any(item['model_id'] == 'gpt4_turbo' for item in data)

def test_get_restricted_models(client):
    """Test the /models/restricted endpoint."""
    response = client.get("/api/v1/models/restricted")
    assert response.status_code == 200
    # Based on our rules, gpt4_turbo should be restricted
    assert "gpt4_turbo" in response.json()

def test_get_governance_report_success(client):
    """Test successfully retrieving a governance report."""
    response = client.get("/api/v1/models/gpt4_turbo/governance_report")
    assert response.status_code == 200
    data = response.json()
    assert data['model_id'] == 'gpt4_turbo'
    assert 'training_data' in data
    assert data['training_data']['Source'] == 'web_crawl'
    assert 'bias_assessment' in data
    assert data['bias_assessment']['Status'] == 'partially_mitigated'

def test_get_governance_report_not_found(client):
    """Test requesting a report for a non-existent model."""
    response = client.get("/api/v1/models/non_existent_model/governance_report")
    assert response.status_code == 404
    assert response.json() == {"detail": "Model 'non_existent_model' not found in registry."}
