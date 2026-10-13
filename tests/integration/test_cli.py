import yaml
from pathlib import Path
from click.testing import CliRunner

from cyprus.cli import main


def _write_test_model(path: Path):
    model = {
        "model_id": "cli_test_model",
        "organization": "TestOrg",
        "compute_flops": 1e20,
        "risk_score": 0.35,
        "risk_category": "minimal_risk",
        "use_case": "general_purpose",
        "red_teaming_status": "completed",
        "deployment_regions": ["eu"],
        "capabilities": ["chat"],
        "governance": {
            "training_data": {"source": "public", "quality_score": 0.9,
                              "size_tokens": 1e12, "documentation_status": "complete"},
            "bias_assessment": {"methodology": "rt", "status": "completed", "score": 0.85},
            "performance": {"f1_score": 0.9, "benchmark": "mmlu", "task": "general"},
            "security": {"access_control": "rbac", "audit_logging": True},
        },
    }
    path.write_text(yaml.dump(model))


def test_check_command(tmp_path):
    model_file = tmp_path / "model.yaml"
    _write_test_model(model_file)

    runner = CliRunner()
    result = runner.invoke(main, ["check", str(model_file)])
    assert result.exit_code == 0


def test_check_json_output(tmp_path):
    model_file = tmp_path / "model.yaml"
    _write_test_model(model_file)

    runner = CliRunner()
    result = runner.invoke(main, ["check", str(model_file), "--output", "json"])
    assert result.exit_code == 0
    assert "cli_test_model" in result.output


def test_validate_command(tmp_path):
    model_file = tmp_path / "model.yaml"
    _write_test_model(model_file)

    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(model_file)])
    assert result.exit_code == 0
    assert "Valid" in result.output


def test_policy_list():
    runner = CliRunner()
    result = runner.invoke(main, ["policy", "list"])
    assert result.exit_code == 0
    assert "EU AI Act" in result.output


def test_policy_validate():
    runner = CliRunner()
    result = runner.invoke(main, ["policy", "validate", "eu_ai_act"])
    assert result.exit_code == 0
    assert "valid" in result.output.lower()
