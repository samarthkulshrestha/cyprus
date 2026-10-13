"""Tests for deployment.lp: Aggregate deployment logic."""
from cyprus.policies.eu_ai_act.tests.conftest import solve_model


def test_compliant_model_can_deploy():
    mc = solve_model(model_id="good_model", use_case="general_purpose",
                     risk_category="minimal_risk")
    assert mc.can_deploy is True


def test_prohibited_model_cannot_deploy():
    mc = solve_model(model_id="bad_model", use_case="social_scoring",
                     risk_category="unacceptable_risk")
    assert mc.can_deploy is False


def test_high_risk_with_unmet_requirements_cannot_deploy():
    mc = solve_model(model_id="hr_incomplete", risk_category="high_risk",
                     red_teaming_status="not_started")
    assert mc.can_deploy is False


def test_high_risk_fully_compliant_can_deploy():
    mc = solve_model(model_id="hr_complete", risk_category="high_risk",
                     red_teaming_status="completed")
    assert mc.can_deploy is True
