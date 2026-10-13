from datetime import datetime

from cyprus.engine.result import ComplianceResult, ComplianceStatus, ModelCompliance
from cyprus.reporting.formatters import format_result


def _make_result():
    m1 = ModelCompliance(model_id="m1", status=ComplianceStatus.COMPLIANT, can_deploy=True)
    return ComplianceResult(
        models={"m1": m1},
        policy_name="Test",
        policy_version="1.0",
        timestamp=datetime.now(),
        articles_evaluated=["art5"],
    )


def test_format_json():
    result = format_result(_make_result(), fmt="json")
    assert '"m1"' in result
    assert '"compliant"' in result


def test_format_csv():
    result = format_result(_make_result(), fmt="csv")
    assert "m1" in result
    assert "compliant" in result


def test_format_markdown():
    result = format_result(_make_result(), fmt="markdown")
    assert "m1" in result


def test_format_table():
    result = format_result(_make_result(), fmt="table")
    assert "m1" in result
