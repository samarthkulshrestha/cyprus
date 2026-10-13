import pytest
from pathlib import Path

import yaml

from cyprus.registry.loader import load_models


def test_load_single_model(tmp_path):
    model_data = {
        "model_id": "test_model",
        "organization": "TestOrg",
        "compute_flops": 1e20,
        "risk_score": 0.5,
        "risk_category": "minimal_risk",
        "use_case": "general_purpose",
        "red_teaming_status": "completed",
        "deployment_regions": ["eu"],
        "capabilities": ["chat"],
        "governance": {
            "training_data": {
                "source": "publicly_available",
                "quality_score": 0.9,
                "size_tokens": 1e12,
                "documentation_status": "complete",
            },
            "bias_assessment": {
                "methodology": "red_teaming",
                "status": "completed",
                "score": 0.85,
            },
            "performance": {
                "f1_score": 0.9,
                "benchmark": "mmlu",
                "task": "general",
            },
            "security": {
                "access_control": "rbac",
                "audit_logging": True,
            },
        },
    }

    f = tmp_path / "model.yaml"
    f.write_text(yaml.dump(model_data))

    models = load_models(f)
    assert len(models) == 1
    assert models[0].model_id == "test_model"


def test_load_multiple_models(tmp_path):
    data = {
        "models": [
            {
                "model_id": "model_a",
                "organization": "Org",
                "compute_flops": 1e20,
                "risk_score": 0.5,
                "risk_category": "minimal_risk",
                "use_case": "general_purpose",
                "red_teaming_status": "completed",
                "deployment_regions": ["eu"],
                "capabilities": ["chat"],
                "governance": {
                    "training_data": {"source": "public", "quality_score": 0.9,
                                      "size_tokens": 1e12, "documentation_status": "complete"},
                    "bias_assessment": {"methodology": "rt", "status": "completed", "score": 0.8},
                    "performance": {"f1_score": 0.9, "benchmark": "mmlu", "task": "general"},
                    "security": {"access_control": "rbac", "audit_logging": True},
                },
            },
            {
                "model_id": "model_b",
                "organization": "Org",
                "compute_flops": 1e21,
                "risk_score": 0.6,
                "risk_category": "high_risk",
                "use_case": "healthcare",
                "red_teaming_status": "completed",
                "deployment_regions": ["eu", "us"],
                "capabilities": ["chat", "reasoning"],
                "governance": {
                    "training_data": {"source": "public", "quality_score": 0.95,
                                      "size_tokens": 1e12, "documentation_status": "complete"},
                    "bias_assessment": {"methodology": "rt", "status": "completed", "score": 0.9},
                    "performance": {"f1_score": 0.93, "benchmark": "mmlu", "task": "general"},
                    "security": {"access_control": "rbac", "audit_logging": True},
                },
            },
        ]
    }

    f = tmp_path / "models.yaml"
    f.write_text(yaml.dump(data))

    models = load_models(f)
    assert len(models) == 2


def test_load_directory(tmp_path):
    model_data = {
        "model_id": "dir_model",
        "organization": "Org",
        "compute_flops": 1e20,
        "risk_score": 0.5,
        "risk_category": "minimal_risk",
        "use_case": "general_purpose",
        "red_teaming_status": "completed",
        "deployment_regions": ["eu"],
        "capabilities": ["chat"],
        "governance": {
            "training_data": {"source": "public", "quality_score": 0.9,
                              "size_tokens": 1e12, "documentation_status": "complete"},
            "bias_assessment": {"methodology": "rt", "status": "completed", "score": 0.8},
            "performance": {"f1_score": 0.9, "benchmark": "mmlu", "task": "general"},
            "security": {"access_control": "rbac", "audit_logging": True},
        },
    }

    (tmp_path / "model1.yaml").write_text(yaml.dump(model_data))
    model_data["model_id"] = "dir_model2"
    (tmp_path / "model2.yaml").write_text(yaml.dump(model_data))

    models = load_models(tmp_path)
    assert len(models) == 2


def test_load_nonexistent_path():
    with pytest.raises(FileNotFoundError):
        load_models(Path("/nonexistent/path"))
