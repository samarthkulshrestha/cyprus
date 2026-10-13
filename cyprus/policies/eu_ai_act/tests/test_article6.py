"""Tests for Article 6: High-Risk Classification."""
from cyprus.policies.eu_ai_act.tests.conftest import solve_model


def test_high_risk_category_classified():
    mc = solve_model(model_id="hr_model", risk_category="high_risk")
    assert mc.high_risk is True


def test_non_high_risk_not_classified():
    mc = solve_model(model_id="lr_model", risk_category="minimal_risk",
                     use_case="general_purpose")
    assert mc.high_risk is False


def test_healthcare_is_high_risk():
    mc = solve_model(model_id="health_model", use_case="healthcare",
                     risk_category="minimal_risk")
    assert mc.high_risk is True


def test_law_enforcement_is_high_risk():
    mc = solve_model(model_id="law_model", use_case="law_enforcement",
                     risk_category="minimal_risk")
    assert mc.high_risk is True


def test_general_purpose_not_auto_high_risk():
    mc = solve_model(model_id="gp_model", use_case="general_purpose",
                     risk_category="minimal_risk")
    assert mc.high_risk is False
