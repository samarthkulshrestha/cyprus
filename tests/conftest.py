"""Top-level pytest fixtures."""
from pathlib import Path

import pytest

from cyprus.registry.schema import (
    ModelEntry, GovernanceFacts, TrainingData,
    BiasAssessment, PerformanceMetrics, SecurityMeasures,
)


POLICY_DIR = Path(__file__).parent.parent / "cyprus" / "policies" / "eu_ai_act"


@pytest.fixture
def policy_dir():
    return POLICY_DIR


@pytest.fixture
def compliant_model() -> ModelEntry:
    """A minimal-risk model that should pass all checks."""
    return ModelEntry(
        model_id="test_compliant",
        organization="TestOrg",
        compute_flops=1e20,
        risk_score=0.35,
        risk_category="minimal_risk",
        use_case="general_purpose",
        red_teaming_status="completed",
        deployment_regions=["eu"],
        capabilities=["chat"],
        governance=GovernanceFacts(
            training_data=TrainingData(
                source="publicly_available",
                quality_score=0.95,
                size_tokens=1e12,
                documentation_status="complete",
            ),
            bias_assessment=BiasAssessment(
                methodology="red_teaming",
                status="completed",
                score=0.90,
            ),
            performance=PerformanceMetrics(
                f1_score=0.92,
                benchmark="mmlu",
                task="general",
            ),
            security=SecurityMeasures(
                access_control="rbac",
                audit_logging=True,
            ),
        ),
    )


@pytest.fixture
def prohibited_model() -> ModelEntry:
    """A model with a prohibited use case."""
    return ModelEntry(
        model_id="test_prohibited",
        organization="TestOrg",
        compute_flops=1e20,
        risk_score=0.80,
        risk_category="unacceptable_risk",
        use_case="social_scoring",
        red_teaming_status="completed",
        deployment_regions=["eu"],
        capabilities=["chat"],
        governance=GovernanceFacts(
            training_data=TrainingData(
                source="publicly_available",
                quality_score=0.95,
                size_tokens=1e12,
                documentation_status="complete",
            ),
            bias_assessment=BiasAssessment(
                methodology="red_teaming",
                status="completed",
                score=0.90,
            ),
            performance=PerformanceMetrics(
                f1_score=0.92,
                benchmark="mmlu",
                task="general",
            ),
            security=SecurityMeasures(
                access_control="rbac",
                audit_logging=True,
            ),
        ),
    )


@pytest.fixture
def high_risk_model() -> ModelEntry:
    """A high-risk model with all requirements met."""
    return ModelEntry(
        model_id="test_high_risk",
        organization="TestOrg",
        compute_flops=1e22,
        risk_score=0.65,
        risk_category="high_risk",
        use_case="healthcare",
        red_teaming_status="completed",
        deployment_regions=["eu"],
        capabilities=["chat", "reasoning"],
        governance=GovernanceFacts(
            training_data=TrainingData(
                source="publicly_available",
                quality_score=0.95,
                size_tokens=1e12,
                documentation_status="complete",
            ),
            bias_assessment=BiasAssessment(
                methodology="red_teaming",
                status="completed",
                score=0.90,
            ),
            performance=PerformanceMetrics(
                f1_score=0.92,
                benchmark="mmlu",
                task="general",
            ),
            security=SecurityMeasures(
                access_control="rbac",
                audit_logging=True,
            ),
        ),
    )
