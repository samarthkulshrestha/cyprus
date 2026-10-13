"""End-to-end pipeline test: YAML -> schema -> facts -> solver -> result."""
from cyprus.engine.solver import Solver
from cyprus.engine.result import ComplianceStatus
from cyprus.registry.compiler import compile_models


def test_full_pipeline_compliant(policy_dir, compliant_model):
    facts = compile_models([compliant_model])
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    mc = result.models["test_compliant"]
    assert mc.status == ComplianceStatus.COMPLIANT
    assert mc.can_deploy is True
    assert mc.violation_count == 0


def test_full_pipeline_prohibited(policy_dir, prohibited_model):
    facts = compile_models([prohibited_model])
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    mc = result.models["test_prohibited"]
    assert mc.status == ComplianceStatus.PROHIBITED
    assert mc.can_deploy is False


def test_full_pipeline_high_risk_compliant(policy_dir, high_risk_model):
    facts = compile_models([high_risk_model])
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    mc = result.models["test_high_risk"]
    assert mc.high_risk is True
    # High-risk with all requirements met should be deployable
    assert mc.can_deploy is True


def test_full_pipeline_multiple_models(policy_dir, compliant_model, prohibited_model, high_risk_model):
    facts = compile_models([compliant_model, prohibited_model, high_risk_model])
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    assert result.total_models == 3
    assert result.models["test_compliant"].can_deploy is True
    assert result.models["test_prohibited"].can_deploy is False
    assert result.prohibited_count == 1
