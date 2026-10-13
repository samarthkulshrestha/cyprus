"""Tests for Article 51: Systemic Risk Classification."""
from cyprus.policies.eu_ai_act.tests.conftest import solve_model


def test_high_compute_systemic():
    mc = solve_model(model_id="big_model", compute_flops=1e26)
    assert mc.systemic_risk is True


def test_low_compute_not_systemic():
    mc = solve_model(model_id="small_model", compute_flops=1e20)
    assert mc.systemic_risk is False


def test_boundary_compute():
    # Exactly at threshold — should NOT trigger (>1e25 required, not >=)
    mc = solve_model(model_id="boundary_model", compute_flops=1e25)
    # 1e25 is not > 1e25, so should not be systemic
    assert mc.systemic_risk is False


def test_many_capabilities_systemic():
    mc = solve_model(
        model_id="multi_cap",
        capabilities=["chat", "code_generation", "multimodal", "reasoning", "translation"],
    )
    assert mc.systemic_risk is True


def test_few_capabilities_not_systemic():
    mc = solve_model(model_id="few_cap", capabilities=["chat", "reasoning"])
    assert mc.systemic_risk is False
