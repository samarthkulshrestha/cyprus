import pytest

from cyprus.engine.solver import Solver
from cyprus.engine.result import ComplianceStatus
from cyprus.registry.compiler import compile_models


def test_solver_loads_policy(policy_dir):
    solver = Solver(policy_dir=policy_dir)
    assert solver._manifest["name"] == "EU AI Act"


def test_solver_missing_manifest(tmp_path):
    with pytest.raises(FileNotFoundError):
        Solver(policy_dir=tmp_path)


def test_solver_compliant_model(policy_dir, compliant_model):
    facts = compile_models([compliant_model])
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    assert "test_compliant" in result.models
    mc = result.models["test_compliant"]
    assert mc.can_deploy is True
    assert mc.status == ComplianceStatus.COMPLIANT


def test_solver_prohibited_model(policy_dir, prohibited_model):
    facts = compile_models([prohibited_model])
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    assert "test_prohibited" in result.models
    mc = result.models["test_prohibited"]
    assert mc.status == ComplianceStatus.PROHIBITED
    assert mc.can_deploy is False
    assert len(mc.prohibited) > 0


def test_solver_explain(policy_dir, prohibited_model):
    facts = compile_models([prohibited_model])
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)

    violations = solver.explain("test_prohibited")
    assert len(violations) > 0
    assert any("social scoring" in v.reason.lower() for v in violations)


def test_solver_explain_unknown_model(policy_dir, compliant_model):
    facts = compile_models([compliant_model])
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)

    with pytest.raises(ValueError, match="not found"):
        solver.explain("nonexistent_model")
