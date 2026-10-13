from cyprus.evaluation.benchmark import PredicateMetrics


def test_predicate_metrics_perfect():
    m = PredicateMetrics("test", true_positives=10, false_positives=0, false_negatives=0)
    assert m.precision == 1.0
    assert m.recall == 1.0
    assert m.f1 == 1.0


def test_predicate_metrics_zero():
    m = PredicateMetrics("test", true_positives=0, false_positives=0, false_negatives=0)
    assert m.precision == 0.0
    assert m.recall == 0.0
    assert m.f1 == 0.0


def test_predicate_metrics_mixed():
    m = PredicateMetrics("test", true_positives=8, false_positives=2, false_negatives=1)
    assert abs(m.precision - 0.8) < 0.01
    assert abs(m.recall - 8/9) < 0.01
    assert m.f1 > 0
