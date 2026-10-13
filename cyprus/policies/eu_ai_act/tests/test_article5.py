"""Tests for Article 5: Prohibited AI Practices."""
from cyprus.policies.eu_ai_act.tests.conftest import solve_model


def test_social_scoring_prohibited():
    mc = solve_model(model_id="social_scorer", use_case="social_scoring",
                     risk_category="unacceptable_risk")
    assert mc.can_deploy is False
    assert any("social scoring" in v.reason.lower() for v in mc.prohibited)


def test_cognitive_manipulation_prohibited():
    mc = solve_model(model_id="manipulator", use_case="cognitive_manipulation",
                     risk_category="unacceptable_risk")
    assert mc.can_deploy is False
    assert any("cognitive manipulation" in v.reason.lower() for v in mc.prohibited)


def test_biometric_surveillance_prohibited():
    mc = solve_model(model_id="surveillance", use_case="biometric_surveillance",
                     risk_category="unacceptable_risk")
    assert mc.can_deploy is False
    assert any("biometric surveillance" in v.reason.lower() for v in mc.prohibited)


def test_non_social_scoring_not_prohibited():
    mc = solve_model(model_id="safe_model", use_case="general_purpose")
    assert len(mc.prohibited) == 0
    assert mc.can_deploy is True
