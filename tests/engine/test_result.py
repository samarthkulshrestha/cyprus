from datetime import datetime

from cyprus.engine.result import (
    ComplianceResult, ComplianceStatus, ModelCompliance, Violation,
)


def test_violation_creation():
    v = Violation(article="art5_1a", title="Article 5(1)(a)",
                  reason="Social scoring", severity="prohibited")
    assert v.article == "art5_1a"
    assert v.severity == "prohibited"


def test_model_compliance_defaults():
    mc = ModelCompliance(model_id="test", status=ComplianceStatus.COMPLIANT)
    assert mc.violation_count == 0
    assert mc.prohibited == []
    assert mc.can_deploy is False


def test_model_compliance_with_violations():
    v = Violation(article="art5_1a", title="Art 5", reason="test", severity="prohibited")
    mc = ModelCompliance(
        model_id="test",
        status=ComplianceStatus.PROHIBITED,
        prohibited=[v],
    )
    assert mc.violation_count == 1


def test_compliance_result_counts():
    m1 = ModelCompliance(model_id="a", status=ComplianceStatus.COMPLIANT, can_deploy=True)
    m2 = ModelCompliance(model_id="b", status=ComplianceStatus.PROHIBITED)
    m3 = ModelCompliance(model_id="c", status=ComplianceStatus.COMPLIANT, can_deploy=True)

    result = ComplianceResult(
        models={"a": m1, "b": m2, "c": m3},
        policy_name="Test",
        policy_version="1.0",
        timestamp=datetime.now(),
        articles_evaluated=["art5"],
    )
    assert result.total_models == 3
    assert result.prohibited_count == 1
    assert result.compliant_count == 2
