"""Test that policy modules are well-formed and load correctly."""

from cyprus.engine.solver import Solver


def test_eu_ai_act_loads(policy_dir):
    solver = Solver(policy_dir=policy_dir)
    assert solver._manifest["name"] == "EU AI Act"
    assert len(solver._rule_files) > 0


def test_eu_ai_act_has_all_rule_files(policy_dir):
    rules_dir = policy_dir / "rules"
    expected = [
        "article5.lp", "article6.lp", "article9.lp", "article10.lp",
        "article13.lp", "article51.lp", "article52.lp", "deployment.lp",
    ]
    actual = [f.name for f in sorted(rules_dir.glob("*.lp"))]
    for exp in expected:
        assert exp in actual, f"Missing rule file: {exp}"


def test_eu_ai_act_traceability_exists(policy_dir):
    assert (policy_dir / "traceability.yaml").exists()
