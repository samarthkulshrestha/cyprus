import pytest
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

@pytest.fixture
def eu_act_engine():
    """
    Provides a PrologEngine instance loaded with the new comprehensive
    EU AI Act rules and corresponding data.
    """
    engine = PrologEngine()
    registry = ModelRegistry("/home/czar/code/cyprus/data/models/registry.json", engine)
    registry.load_into_engine()
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/eu_ai_act.pl")
    return engine

def test_prohibited_deployment(eu_act_engine):
    """
    Tests the 'prohibited_deployment' rule.
    The 'social_scorer_v1' model should be prohibited.
    """
    solutions = eu_act_engine.query("prohibited_deployment(Model)")
    models = {sol['Model'] for sol in solutions}
    assert 'social_scorer_v1' in models
    assert 'gpt4_turbo' not in models

def test_is_systemic_risk(eu_act_engine):
    """
    Tests the 'is_systemic_risk' rule (compute > 1e25).
    'gpt4_turbo' should be classified as systemic risk.
    """
    solutions = eu_act_engine.query("is_systemic_risk(Model)")
    models = {sol['Model'] for sol in solutions}
    assert 'gpt4_turbo' in models
    assert 'social_scorer_v1' not in models

def test_requires_high_risk_compliance(eu_act_engine):
    """
    Tests the 'requires_high_risk_compliance' rule.
    'gpt4_turbo' is in the 'high_risk' category.
    """
    solutions = eu_act_engine.query("requires_high_risk_compliance(Model)")
    models = {sol['Model'] for sol in solutions}
    assert 'gpt4_turbo' in models

def test_requires_transparency_disclosure(eu_act_engine):
    """
    Tests the 'requires_transparency_disclosure' rule.
    The customer chatbot has the 'chat' capability.
    """
    solutions = eu_act_engine.query("requires_transparency_disclosure(Model)")
    models = {sol['Model'] for sol in solutions}
    assert 'customer_chatbot_v3' in models

def test_can_deploy_logic(eu_act_engine):
    """
    Tests the 'can_deploy' logic.
    - social_scorer_v1 is prohibited, so it cannot be deployed.
    - gpt4_turbo is high-risk but is red_teamed, so it can be.
    - customer_chatbot_v3 is not prohibited and not high-risk, so it can be.
    """
    solutions = eu_act_engine.query("can_deploy(Model)")
    models = {sol['Model'] for sol in solutions}
    
    assert 'social_scorer_v1' not in models
    assert 'gpt4_turbo' in models
    assert 'customer_chatbot_v3' in models
