"""Tests for Article 9: Risk Management System."""
from cyprus.policies.eu_ai_act.tests.conftest import solve_model


def test_incomplete_red_teaming_flagged():
    mc = solve_model(model_id="hr_no_rt", risk_category="high_risk",
                     red_teaming_status="not_started")
    assert mc.can_deploy is False
    assert any("red teaming" in v.reason.lower() for v in mc.unmet_requirements)


def test_completed_red_teaming_passes():
    mc = solve_model(model_id="hr_rt_done", risk_category="high_risk",
                     red_teaming_status="completed")
    # Should not have red teaming unmet requirement
    assert not any("red teaming" in v.reason.lower() for v in mc.unmet_requirements)


def test_suspiciously_low_risk_score_flagged():
    mc = solve_model(model_id="hr_low_risk", risk_category="high_risk",
                     risk_score=0.05)
    assert any("risk score" in v.reason.lower() for v in mc.unmet_requirements)


def test_missing_bias_assessment_flagged():
    from cyprus.registry.schema import BiasAssessment
    mc = solve_model(
        model_id="hr_no_bias",
        risk_category="high_risk",
        governance={
            "bias_assessment": BiasAssessment(
                methodology="unknown", status="not_started", score=0.0,
            ),
        },
    )
    assert any("bias assessment" in v.reason.lower() for v in mc.unmet_requirements)
