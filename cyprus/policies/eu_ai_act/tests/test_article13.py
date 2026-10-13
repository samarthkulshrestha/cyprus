"""Tests for Article 13: Transparency and Provision of Information."""
from cyprus.registry.schema import TrainingData
from cyprus.policies.eu_ai_act.tests.conftest import solve_model


def test_incomplete_docs_flagged():
    mc = solve_model(
        model_id="hr_no_docs",
        risk_category="high_risk",
        governance={
            "training_data": TrainingData(
                source="publicly_available", quality_score=0.95,
                size_tokens=1e12, documentation_status="partial",
            ),
        },
    )
    assert any("transparency" in v.reason.lower() or "documentation" in v.reason.lower()
               for v in mc.unmet_requirements)
