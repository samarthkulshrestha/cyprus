import pytest
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

def test_is_high_risk(configured_engine):
    """
    Tests the 'is_high_risk' rule.
    gpt4_turbo is high risk because it has 'reasoning' and is deployed in 'eu'.
    cloudia_v2 is not, because it is not deployed in 'eu'.
    """
    solutions = configured_engine.query("is_high_risk(Model)")
    high_risk_models = {sol['Model'] for sol in solutions}
    assert high_risk_models == {'gpt4_turbo'}

def test_is_not_high_risk(configured_engine):
    """Tests that cloudia_v2 is correctly identified as not high_risk."""
    solutions = configured_engine.query("is_high_risk(cloudia_v2)")
    assert len(solutions) == 0

def test_restricted_model(configured_engine):
    """
    Tests the 'restricted' rule.
    gpt4_turbo is high_risk and its risk score (0.82) is > 0.7.
    """
    solutions = configured_engine.query("restricted(Model)")
    restricted_models = {sol['Model'] for sol in solutions}
    assert restricted_models == {'gpt4_turbo'}

def test_can_deploy(configured_engine):
    """
    Tests the 'can_deploy' rule.
    - cloudia_v2 can be deployed because it's not high_risk.
    - gpt4_turbo is high_risk, but can be deployed because it is red_teamed.
    """
    solutions = configured_engine.query("can_deploy(Model)")
    deployable_models = {sol['Model'] for sol in solutions}
    assert 'gpt4_turbo' in deployable_models
    assert 'cloudia_v2' in deployable_models
    assert len(deployable_models) == 2

def test_model_registry_loading_model8():
    """
    Tests loading the new model/8 format from the JSON registry.
    """
    engine = PrologEngine()
    registry = ModelRegistry("/home/czar/code/cyprus/data/models/registry.json", engine)
    registry.load_into_engine()
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/eu_ai_act.pl")

    # Check that gpt4_turbo was loaded correctly and is restricted
    solutions = engine.query("restricted(gpt4_turbo)")
    assert len(solutions) > 0, "gpt4_turbo should be restricted after loading from JSON"

    # Check that cloudia_v2 was loaded and is deployable
    solutions = engine.query("can_deploy(cloudia_v2)")
    assert len(solutions) > 0, "cloudia_v2 should be deployable after loading from JSON"