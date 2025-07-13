import pytest
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

@pytest.fixture
def governance_engine():
    """
    Provides a PrologEngine instance loaded with all data and rules
    for comprehensive governance testing.
    """
    engine = PrologEngine()
    registry = ModelRegistry("/home/czar/code/cyprus/data/models/registry.json", engine)
    registry.load_into_engine()
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/governance_rules.pl")
    return engine

def test_low_quality_data(governance_engine):
    """
    Tests the 'low_quality_data' rule.
    gpt4_turbo's training data quality score is 0.85, so it should NOT be flagged.
    The rule is QualityScore < 0.85.
    Let's add a model that should fail.
    """
    # Manually assert a model with low quality data
    governance_engine.assertz("training_data(test_model, 'src', '1gb', '2024', 0.7)")
    solutions = governance_engine.query("low_quality_data(Model)")
    models = {sol['Model'] for sol in solutions}
    assert 'test_model' in models
    assert 'gpt4_turbo' not in models

def test_incomplete_bias_mitigation(governance_engine):
    """
    Tests the 'incomplete_bias_mitigation' rule.
    gpt4_turbo has 'partially_mitigated' status.
    cloudia_v2 has 'completed' status.
    """
    solutions = governance_engine.query("incomplete_bias_mitigation(Model)")
    models = {sol['Model'] for sol in solutions}
    assert 'gpt4_turbo' in models
    assert 'cloudia_v2' not in models

def test_is_underperforming(governance_engine):
    """
    Tests the 'is_underperforming' rule (F1 score < 0.9).
    gpt4_turbo has an F1 score of 0.89, so it should be flagged.
    """
    solutions = governance_engine.query("is_underperforming(Model)")
    models = {sol['Model'] for sol in solutions}
    assert 'gpt4_turbo' in models

def test_not_production_ready(governance_engine):
    """
    Tests the omnibus 'not_production_ready' rule.
    gpt4_turbo is not production ready because its bias mitigation is
    incomplete AND it is underperforming.
    """
    solutions = governance_engine.query("not_production_ready(Model)")
    models = {sol['Model'] for sol in solutions}
    assert 'gpt4_turbo' in models
    # cloudia_v2 has no failing conditions, so it should not be in the set.
    assert 'cloudia_v2' not in models
