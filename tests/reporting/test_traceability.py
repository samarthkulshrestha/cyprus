from cyprus.reporting.traceability import generate_traceability_matrix


def test_traceability_matrix(policy_dir):
    matrix = generate_traceability_matrix(policy_dir)
    assert "Traceability Matrix" in matrix
    assert "article5" in matrix
    assert "Coverage summary" in matrix
    assert "complete" in matrix.lower() or "Complete" in matrix
