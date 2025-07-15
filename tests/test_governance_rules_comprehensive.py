import pytest
from cyprus.core.prolog_engine import PrologEngine

@pytest.fixture
def engine():
    """Provides a clean PrologEngine instance for each test."""
    return PrologEngine()

@pytest.fixture
def load_rules(engine):
    """Loads the governance rules into the engine."""
    engine.load_file("/home/czar/code/cyprus/cyprus/policies/governance_rules.pl")

def test_low_quality_data_boundary(engine, load_rules):
    """Tests the boundary condition for low-quality data."""
    engine.assertz("training_data(model_good, 'src', '1gb', '2024', 0.85)")
    engine.assertz("training_data(model_bad, 'src', '1gb', '2024', 0.84)")

    solutions = engine.query("low_quality_data(Model)")
    flagged_models = {sol['Model'] for sol in solutions}

    assert 'model_good' not in flagged_models
    assert 'model_bad' in flagged_models

def test_bias_mitigation_status(engine, load_rules):
    """Tests different bias mitigation statuses."""
    engine.assertz("bias_assessment(model_completed, 'date', [], [], 'completed')")
    engine.assertz("bias_assessment(model_ongoing, 'date', [], [], 'ongoing')")
    engine.assertz("bias_assessment(model_pending, 'date', [], [], 'pending')")

    solutions = engine.query("incomplete_bias_mitigation(Model)")
    flagged_models = {sol['Model'] for sol in solutions}

    assert 'model_completed' not in flagged_models
    assert 'model_ongoing' in flagged_models
    assert 'model_pending' in flagged_models

def test_underperforming_boundary(engine, load_rules):
    """Tests the boundary condition for the F1 score."""
    engine.assertz("performance_metrics(model_ok, 1, 1, 1, 0.9, 'date')")
    engine.assertz("performance_metrics(model_bad, 1, 1, 1, 0.89, 'date')")

    solutions = engine.query("is_underperforming(Model)")
    flagged_models = {sol['Model'] for sol in solutions}

    assert 'model_ok' not in flagged_models
    assert 'model_bad' in flagged_models

def test_inadequate_security_logic(engine, load_rules):
    """Tests the security measures for required access controls."""
    engine.assertz("security_measures(model_good, true, true, 'rbac')")
    engine.assertz("security_measures(model_bad, true, true, 'acl')")
    engine.assertz("security_measures(model_none, true, true, 'none')")

    solutions = engine.query("inadequate_security(Model)")
    flagged_models = {sol['Model'] for sol in solutions}

    assert 'model_good' not in flagged_models
    assert 'model_bad' in flagged_models
    assert 'model_none' in flagged_models

def test_not_production_ready_combinations(engine, load_rules):
    """Tests that any single failing rule makes a model not production ready."""
    # Model that fails only on data quality
    engine.assertz("training_data(model_bad_data, 'src', '1gb', '2024', 0.7)")
    engine.assertz("bias_assessment(model_bad_data, 'date', [], [], 'completed')")
    engine.assertz("performance_metrics(model_bad_data, 1, 1, 1, 0.95, 'date')")
    engine.assertz("security_measures(model_bad_data, true, true, 'rbac')")

    # Model that fails only on bias
    engine.assertz("training_data(model_bad_bias, 'src', '1gb', '2024', 0.9)")
    engine.assertz("bias_assessment(model_bad_bias, 'date', [], [], 'incomplete')")
    engine.assertz("performance_metrics(model_bad_bias, 1, 1, 1, 0.95, 'date')")
    engine.assertz("security_measures(model_bad_bias, true, true, 'rbac')")

    # A model that passes everything
    engine.assertz("training_data(model_perfect, 'src', '1gb', '2024', 0.9)")
    engine.assertz("bias_assessment(model_perfect, 'date', [], [], 'completed')")
    engine.assertz("performance_metrics(model_perfect, 1, 1, 1, 0.95, 'date')")
    engine.assertz("security_measures(model_perfect, true, true, 'rbac')")

    solutions = engine.query("not_production_ready(Model)")
    not_ready_models = {sol['Model'] for sol in solutions}

    assert 'model_bad_data' in not_ready_models
    assert 'model_bad_bias' in not_ready_models
    assert 'model_perfect' not in not_ready_models