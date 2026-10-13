import pytest
from pydantic import ValidationError

from cyprus.registry.schema import ModelEntry, GovernanceFacts, TrainingData, BiasAssessment, PerformanceMetrics, SecurityMeasures


def _make_governance(**overrides):
    defaults = {
        "training_data": TrainingData(
            source="publicly_available", quality_score=0.9,
            size_tokens=1e12, documentation_status="complete",
        ),
        "bias_assessment": BiasAssessment(
            methodology="red_teaming", status="completed", score=0.85,
        ),
        "performance": PerformanceMetrics(
            f1_score=0.9, benchmark="mmlu", task="general",
        ),
        "security": SecurityMeasures(access_control="rbac", audit_logging=True),
    }
    defaults.update(overrides)
    return GovernanceFacts(**defaults)


def test_valid_model():
    m = ModelEntry(
        model_id="test_model",
        organization="TestOrg",
        compute_flops=1e20,
        risk_score=0.5,
        risk_category="minimal_risk",
        use_case="general_purpose",
        red_teaming_status="completed",
        deployment_regions=["eu"],
        capabilities=["chat"],
        governance=_make_governance(),
    )
    assert m.model_id == "test_model"


def test_invalid_model_id():
    with pytest.raises(ValidationError):
        ModelEntry(
            model_id="Invalid-ID",
            organization="TestOrg",
            compute_flops=1e20,
            risk_score=0.5,
            risk_category="minimal_risk",
            use_case="general_purpose",
            red_teaming_status="completed",
            deployment_regions=["eu"],
            capabilities=["chat"],
            governance=_make_governance(),
        )


def test_invalid_region():
    with pytest.raises(ValidationError):
        ModelEntry(
            model_id="test",
            organization="TestOrg",
            compute_flops=1e20,
            risk_score=0.5,
            risk_category="minimal_risk",
            use_case="general_purpose",
            red_teaming_status="completed",
            deployment_regions=["mars"],
            capabilities=["chat"],
            governance=_make_governance(),
        )


def test_risk_score_bounds():
    with pytest.raises(ValidationError):
        ModelEntry(
            model_id="test",
            organization="TestOrg",
            compute_flops=1e20,
            risk_score=1.5,
            risk_category="minimal_risk",
            use_case="general_purpose",
            red_teaming_status="completed",
            deployment_regions=["eu"],
            capabilities=["chat"],
            governance=_make_governance(),
        )


def test_empty_capabilities():
    with pytest.raises(ValidationError):
        ModelEntry(
            model_id="test",
            organization="TestOrg",
            compute_flops=1e20,
            risk_score=0.5,
            risk_category="minimal_risk",
            use_case="general_purpose",
            red_teaming_status="completed",
            deployment_regions=["eu"],
            capabilities=[],
            governance=_make_governance(),
        )
