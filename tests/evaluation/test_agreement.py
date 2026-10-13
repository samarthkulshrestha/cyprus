import yaml

from cyprus.evaluation.agreement import compute_agreement, _fleiss_kappa


def test_fleiss_kappa_perfect():
    # All raters agree on all subjects
    ratings = [[3, 0], [0, 3], [3, 0]]  # 3 raters, 3 subjects
    kappa = _fleiss_kappa(ratings, 3)
    assert kappa == 1.0


def test_fleiss_kappa_disagreement():
    # With 2 raters, every subject split 1-1 means perfect disagreement
    ratings = [[1, 1], [1, 1], [1, 1], [1, 1]]
    kappa = _fleiss_kappa(ratings, 2)
    assert kappa < 0  # Negative kappa = worse than chance


def test_compute_agreement(tmp_path):
    # Create two annotator files
    ann1 = {
        "annotator_id": "a1",
        "models": {
            "model_a": {"prohibited": True, "high_risk": False, "systemic_risk": False, "can_deploy": False},
            "model_b": {"prohibited": False, "high_risk": True, "systemic_risk": False, "can_deploy": True},
        }
    }
    ann2 = {
        "annotator_id": "a2",
        "models": {
            "model_a": {"prohibited": True, "high_risk": False, "systemic_risk": False, "can_deploy": False},
            "model_b": {"prohibited": False, "high_risk": True, "systemic_risk": False, "can_deploy": True},
        }
    }

    (tmp_path / "ann1.yaml").write_text(yaml.dump(ann1))
    (tmp_path / "ann2.yaml").write_text(yaml.dump(ann2))

    result = compute_agreement(tmp_path)
    assert result.annotator_count == 2
    assert result.model_count == 2
    assert result.overall_kappa == 1.0  # Perfect agreement
