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

def test_get_prohibited_models(client):
    """Test the new /models/prohibited endpoint."""
    response = client.get("/api/v1/models/prohibited")
    assert response.status_code == 200
    # Based on our rules, social_scorer_v1 should be prohibited
    assert "social_scorer_v1" in response.json()

def test_get_systemic_risk_models(client):
    """Test the new /models/systemic_risk endpoint."""
    response = client.get("/api/v1/models/systemic_risk")
    assert response.status_code == 200
    # Based on our rules, gpt4_turbo should be systemic risk
    assert "gpt4_turbo" in response.json()

def test_get_deployable_models(client):
    """Test the /models/deployable endpoint."""
    response = client.get("/api/v1/models/deployable")
    assert response.status_code == 200
    data = response.json()
    assert "gpt4_turbo" in data
    assert "customer_chatbot_v3" in data
    assert "social_scorer_v1" not in data

def test_get_model_compliance_deployable(client):
    """Test the compliance status of a deployable model."""
    response = client.get("/api/v1/models/gpt4_turbo/compliance")
    assert response.status_code == 200
    data = response.json()
    assert data['model_id'] == 'gpt4_turbo'
    assert data['is_compliant'] is True
    assert data['is_deployable'] is True

def test_get_model_compliance_prohibited(client):
    """Test the compliance status of a prohibited model."""
    response = client.get("/api/v1/models/social_scorer_v1/compliance")
    assert response.status_code == 200
    data = response.json()
    assert data['model_id'] == 'social_scorer_v1'
    assert data['is_compliant'] is False
    assert data['is_deployable'] is False
    assert data['is_restricted'] is True

def test_get_governance_report_success(client):
    """Test successfully retrieving a governance report."""
    response = client.get("/api/v1/models/gpt4_turbo/governance_report")
    assert response.status_code == 200
    data = response.json()
    assert data['model_id'] == 'gpt4_turbo'
    # assert 'training_data' in data
    # assert data['training_data']['Source'] == "web_crawl"
    assert 'bias_assessment' in data
    assert data['bias_assessment']['Status'] == "partially_mitigated"

def test_get_governance_report_not_found(client):
    """Test requesting a report for a non-existent model."""
    response = client.get("/api/v1/models/non_existent_model/governance_report")
    assert response.status_code == 404
    assert response.json() == {"detail": "Model 'non_existent_model' not found in registry."}
