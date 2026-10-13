"""Tests for Article 10: Data and Data Governance."""
from cyprus.registry.schema import TrainingData, BiasAssessment
from cyprus.policies.eu_ai_act.tests.conftest import solve_model


def test_low_training_quality_flagged():
    mc = solve_model(
        model_id="hr_low_quality",
        risk_category="high_risk",
        governance={
            "training_data": TrainingData(
                source="publicly_available", quality_score=0.70,
                size_tokens=1e12, documentation_status="complete",
            ),
        },
    )
    assert any("training data quality" in v.reason.lower() for v in mc.unmet_requirements)


def test_adequate_training_quality_passes():
    mc = solve_model(model_id="hr_good_quality", risk_category="high_risk")
    assert not any("training data quality" in v.reason.lower() for v in mc.unmet_requirements)


def test_incomplete_documentation_flagged():
    mc = solve_model(
        model_id="hr_bad_docs",
        risk_category="high_risk",
        governance={
            "training_data": TrainingData(
                source="publicly_available", quality_score=0.95,
                size_tokens=1e12, documentation_status="incomplete",
            ),
        },
    )
    assert any("documentation incomplete" in v.reason.lower() for v in mc.unmet_requirements)


def test_undocumented_source_flagged():
    mc = solve_model(
        model_id="hr_no_source",
        risk_category="high_risk",
        governance={
            "training_data": TrainingData(
                source="undocumented", quality_score=0.95,
                size_tokens=1e12, documentation_status="complete",
            ),
        },
    )
    assert any("source undocumented" in v.reason.lower() for v in mc.unmet_requirements)


def test_missing_bias_exam_flagged():
    mc = solve_model(
        model_id="hr_no_bias_exam",
        risk_category="high_risk",
        governance={
            "bias_assessment": BiasAssessment(
                methodology="unknown", status="not_started", score=0.0,
            ),
        },
    )
    assert any("bias examination" in v.reason.lower() or "bias assessment" in v.reason.lower()
               for v in mc.unmet_requirements)
