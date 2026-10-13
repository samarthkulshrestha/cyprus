"""Shared fixtures for EU AI Act policy tests."""
from pathlib import Path

from cyprus.engine.solver import Solver
from cyprus.registry.compiler import compile_models
from cyprus.registry.schema import (
    ModelEntry, GovernanceFacts, TrainingData,
    BiasAssessment, PerformanceMetrics, SecurityMeasures,
)

POLICY_DIR = Path(__file__).parent.parent


def _default_governance(**overrides) -> GovernanceFacts:
    td = overrides.get("training_data", TrainingData(
        source="publicly_available", quality_score=0.95,
        size_tokens=1e12, documentation_status="complete",
    ))
    ba = overrides.get("bias_assessment", BiasAssessment(
        methodology="red_teaming", status="completed", score=0.90,
    ))
    pm = overrides.get("performance", PerformanceMetrics(
        f1_score=0.92, benchmark="mmlu", task="general",
    ))
    sm = overrides.get("security", SecurityMeasures(
        access_control="rbac", audit_logging=True,
    ))
    return GovernanceFacts(training_data=td, bias_assessment=ba, performance=pm, security=sm)


def make_model(**overrides) -> ModelEntry:
    """Create a model with sensible defaults, overriding specific fields."""
    defaults = {
        "model_id": "test_model",
        "organization": "TestOrg",
        "compute_flops": 1e20,
        "risk_score": 0.35,
        "risk_category": "minimal_risk",
        "use_case": "general_purpose",
        "red_teaming_status": "completed",
        "deployment_regions": ["eu"],
        "capabilities": ["chat"],
        "governance": _default_governance(),
    }
    # Handle governance overrides specially
    if "governance" in overrides and isinstance(overrides["governance"], dict):
        overrides["governance"] = _default_governance(**overrides["governance"])
    defaults.update(overrides)
    return ModelEntry(**defaults)


def solve_model(**model_overrides):
    """Create a model, compile it, solve, and return the ModelCompliance."""
    model = make_model(**model_overrides)
    facts = compile_models([model])
    solver = Solver(policy_dir=POLICY_DIR)
    solver.load_model_facts(facts)
    result = solver.solve()
    return result.models[model.model_id]
