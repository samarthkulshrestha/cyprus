"""Tests for Article 52: Transparency Obligations for GPAI."""
from cyprus.policies.eu_ai_act.tests.conftest import solve_model


def test_chat_requires_transparency():
    mc = solve_model(model_id="chat_model", capabilities=["chat"])
    assert mc.transparency_required is True


def test_content_gen_requires_transparency():
    mc = solve_model(model_id="content_model", use_case="content_generation",
                     capabilities=["image_generation"])
    assert mc.transparency_required is True


def test_non_interactive_no_transparency():
    mc = solve_model(model_id="batch_model", use_case="research",
                     capabilities=["reasoning"])
    assert mc.transparency_required is False
