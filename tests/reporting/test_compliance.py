from datetime import datetime

from cyprus.engine.result import (
    ComplianceResult, ComplianceStatus, ModelCompliance, Violation,
)
from cyprus.reporting.compliance import generate_report


def _make_result():
    m1 = ModelCompliance(model_id="good_model", status=ComplianceStatus.COMPLIANT, can_deploy=True)
    m2 = ModelCompliance(
        model_id="bad_model",
        status=ComplianceStatus.PROHIBITED,
        prohibited=[Violation("art5_1a", "Art. 5(1)(a)", "Social scoring", "prohibited")],
    )
    return ComplianceResult(
        models={"good_model": m1, "bad_model": m2},
        policy_name="EU AI Act",
        policy_version="2024.1",
        timestamp=datetime(2026, 4, 13),
        articles_evaluated=["art5"],
    )


def test_markdown_report():
    result = _make_result()
    report = generate_report(result, fmt="markdown")
    assert "# Compliance Report" in report
    assert "good_model" in report or "bad_model" in report
    assert "Prohibited" in report


def test_json_report():
    result = _make_result()
    report = generate_report(result, fmt="json")
    import json
    data = json.loads(report)
    assert "models" in data
    assert "bad_model" in data["models"]


def test_csv_report():
    result = _make_result()
    report = generate_report(result, fmt="csv")
    assert "model_id" in report
    assert "good_model" in report
