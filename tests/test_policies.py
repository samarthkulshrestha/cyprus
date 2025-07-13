import pytest
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

@pytest.fixture
def configured_engine():
    """
    Provides a PrologEngine instance loaded with the base registry
    and EU AI Act rules.
    """
    engine = PrologEngine()
    # Note: Adjust paths if tests are run from a different directory
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/base_registry.pl")
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/eu_ai_act.pl")
    return engine

def test_restricted_model(configured_engine):
    """
    Tests the 'restricted' rule. gpt4 should be restricted.
    """
    solutions = configured_engine.query("restricted(Model)")
    # The only model matching the restricted criteria from base_registry.pl
    assert solutions == [{'Model': 'gpt4'}]

def test_can_deploy_low_risk(configured_engine):
    """
    Tests the 'can_deploy' rule for low-risk models.
    cloudia and customllm should be deployable based on risk score <= 0.5.
    """
    solutions = configured_engine.query("can_deploy(Model)")
    
    # Extract model names from solutions
    deployed_models = {sol['Model'] for sol in solutions}

    # cloudia and customllm have risk_score <= 0.5
    # gpt4 has risk > 0.5 but is red_teamed, so it should also be deployable
    assert 'cloudia' in deployed_models
    assert 'customllm' in deployed_models

def test_can_deploy_high_risk_red_teamed(configured_engine):
    """
    Tests that a high-risk model can be deployed if it's red_teamed.
    gpt4 has risk > 0.7 but is red_teamed, so it should be deployable.
    """
    solutions = configured_engine.query("can_deploy(gpt4)")
    assert len(solutions) > 0, "gpt4 should be deployable because it is red_teamed"

def test_model_registry_loading():
    """
    Tests loading models from the JSON registry into the engine.
    """
    engine = PrologEngine()
    # Assuming registry.json and policy files are in the correct paths
    # relative to the project root.
    registry = ModelRegistry("/home/czar/code/cyprus/data/models/registry.json", engine)
    registry.load_into_engine()

    # === Debugging Step ===
    # Verify that the red_teamed fact for gpt4 was asserted correctly.
    # This is the key condition for the failing part of the can_deploy rule.
    assert list(engine.query("red_teamed(gpt4)")) == [{}], \
        "The fact 'red_teamed(gpt4)' was not found after loading from JSON."

    engine.load_file("/home/czar/code/cyprus/cyprus/policies/eu_ai_act.pl")

    # Query for a model from the JSON file
    solutions = engine.query("model(cloudia, org(anthropic), _, _)")
    assert len(solutions) > 0

    # Check compliance rules against JSON-loaded data
    restricted_solutions = engine.query("restricted(Model)")
    assert restricted_solutions == [{'Model': 'gpt4'}]

    potentially_restricted_solutions = engine.query("potentially_restricted(Model, Confidence)")
    assert potentially_restricted_solutions[0]['Model'] == 'gpt4'
    assert potentially_restricted_solutions[0]['Confidence'] == pytest.approx(0.81)

    deployable_solutions = engine.query("can_deploy(Model)")
    deployable_models = {sol['Model'] for sol in deployable_solutions}
    # gpt4 is deployable because it is red_teamed.
    # The others are deployable because their risk is <= 0.5
    assert deployable_models == {'gpt4', 'cloudia', 'customllm', 'distilbert_distilgpt2', 'my_internal_model'}
