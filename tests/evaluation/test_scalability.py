from cyprus.evaluation.scalability import TimingResult


def test_timing_result():
    t = TimingResult(
        model_count=100,
        total_time_ms=150.0,
        grounding_time_ms=100.0,
        solving_time_ms=50.0,
        memory_mb=64.0,
    )
    assert t.model_count == 100
    assert t.total_time_ms == 150.0
