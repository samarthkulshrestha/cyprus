import pytest
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

@pytest.fixture
def engine():
    """Provides a clean PrologEngine instance for each test."""
    engine = PrologEngine()
    registry = ModelRegistry("/home/czar/code/cyprus/data/models/registry.json", engine)
    registry.load_into_engine()
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/eu_ai_act.pl")
    return engine

@pytest.fixture
def load_rules(engine):
    """Loads the EU AI Act rules into the engine."""
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/eu_ai_act.pl")

def test_prohibited_use_cases(engine, load_rules):
    """Tests all defined prohibited use cases."""

# model(gpt4_turbo, org(openai), compute(2.8e25), risk_score(0.82),
#       deployment_region([us, eu, uk]),
#       alignment_methodology([rlhf, 'constitutional_ai']),
#       capabilities([text_generation, reasoning, coding, multimodal]),
#       red_teaming_status(completed)
# ).
    engine.assertz("model(model1, org, 1, 1, [], [], [], 'n/a', 'unacceptable', use_case('social_scoring'))")
    engine.assertz("model(model2, org, 1, 1, [], [], [], 'n/a', 'unacceptable', use_case('cognitive_manipulation'))")
    engine.assertz("model(model3, org, 1, 1, [], [], [], 'n/a', 'unacceptable', use_case('biometric_surveillance'))")
    engine.assertz("model(model4, org, 1, 1, [], [], [], 'n/a', 'low', use_case('general_purpose'))")

    solutions = engine.query("prohibited_deployment(Model)")
    prohibited_models = {sol['Model'] for sol in solutions}

    assert 'model1' in prohibited_models
    assert 'model2' in prohibited_models
    assert 'model3' in prohibited_models
    assert 'model4' not in prohibited_models

def test_systemic_risk_threshold(engine, load_rules):
    """Tests the systemic risk compute threshold accurately."""
    engine.assertz("model(model_high, org, compute(1.1e25), 0.8, [], [], [], 'n/a', 'high_risk', 'general')")
    engine.assertz("model(model_exact, org, compute(1e25), 0.8, [], [], [], 'n/a', 'moderate_risk', 'general')")
    engine.assertz("model(model_low, org, compute(9.9e24), 0.8, [], [], [], 'n/a', 'low_risk', 'general')")

    solutions = engine.query("is_systemic_risk(Model)")
    systemic_models = {sol['Model'] for sol in solutions}

    assert 'model_high' in systemic_models
    assert 'model_exact' not in systemic_models
    assert 'model_low' not in systemic_models

def test_high_risk_compliance_logic(engine, load_rules):
    """Tests the logic for identifying high-risk systems."""
    engine.assertz("model(hr_model, org, 1, 1, [], [], [], 'n/a', risk_category('high_risk'), 'employment')")
    engine.assertz("model(lr_model, org, 1, 1, [], [], [], 'n/a', risk_category('limited_risk'), 'chatbot')")

    solutions = engine.query("requires_high_risk_compliance(Model)")
    high_risk_models = {sol['Model'] for sol in solutions}

    assert 'hr_model' in high_risk_models
    assert 'lr_model' not in high_risk_models

def test_transparency_disclosure_logic(engine, load_rules):
    """Tests the transparency disclosure for chat-capable models."""
    engine.assertz("model(chat_model, org, 1, 1, [], [], capabilities(['chat', 'qa']), 'n/a', 'limited_risk', 'support')")
    engine.assertz("model(no_chat_model, org, 1, 1, [], [], capabilities(['qa', 'summarization']), 'n/a', 'limited_risk', 'backend')")

    solutions = engine.query("requires_transparency_disclosure(Model)")
    disclosure_models = {sol['Model'] for sol in solutions}

    assert 'chat_model' in disclosure_models
    assert 'no_chat_model' not in disclosure_models

def test_deployment_readiness_scenarios(engine, load_rules):
    """Tests the nuanced deployment readiness rules."""
    engine.assertz("model(low_risk_ok, org, 1, 1, [], [], [], red_teaming_status('n/a'), risk_category('minimal_risk'), use_case('internal_tool'))")
    engine.assertz("model(high_risk_red_teamed, org, 1, 1, [], [], [], red_teaming_status('completed'), risk_category('high_risk'), use_case('medical_diagnosis'))")
    engine.assertz("model(high_risk_not_red_teamed, org, 1, 1, [], [], [], red_teaming_status('pending'), risk_category('high_risk'), use_case('credit_scoring'))")
    engine.assertz("model(prohibited_red_teamed, org, 1, 1, [], [], [], red_teaming_status('completed'), risk_category('unacceptable'), use_case('social_scoring'))")

    solutions = engine.query("can_deploy(Model)")
    deployable_models = {sol['Model'] for sol in solutions}

    assert 'low_risk_ok' in deployable_models
    assert 'high_risk_red_teamed' in deployable_models
    assert 'high_risk_not_red_teamed' not in deployable_models
    assert 'prohibited_red_teamed' not in deployable_models
