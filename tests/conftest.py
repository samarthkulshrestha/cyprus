import pytest
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

@pytest.fixture(scope="function")
def engine():
    """
    A core fixture that provides a managed PrologEngine instance for each test function.
    It uses the engine as a context manager to ensure the Prolog
    session is properly halted after the test completes.
    """
    with PrologEngine() as e:
        yield e

@pytest.fixture
def configured_engine(engine):
    """
    Provides a PrologEngine instance loaded with the base registry
    and EU AI Act rules for policy testing.
    """
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/base_registry.pl")
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/eu_ai_act.pl")
    return engine

@pytest.fixture
def governance_engine(engine):
    """
    Provides a PrologEngine instance loaded with all data and rules
    for comprehensive governance testing.
    """
    registry = ModelRegistry("/home/czar/code/cyprus/data/models/registry.json", engine)
    registry.load_into_engine()
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/eu_ai_act.pl")
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/governance_rules.pl")
    return engine
