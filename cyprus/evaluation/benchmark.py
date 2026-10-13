import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from cyprus.engine.solver import Solver
from cyprus.registry.loader import load_models
from cyprus.registry.compiler import compile_models


@dataclass
class PredicateMetrics:
    """Precision/recall/F1 for a single predicate."""
    predicate: str
    true_positives: int
    false_positives: int
    false_negatives: int

    @property
    def precision(self) -> float:
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom > 0 else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


@dataclass
class AccuracyResult:
    """Results from an accuracy benchmark run."""
    cyprus_metrics: dict[str, PredicateMetrics]
    baseline_metrics: dict[str, dict[str, PredicateMetrics]]
    confusion_matrices: dict[str, list[list[int]]]


def run_accuracy_benchmark(
    ground_truth_path: Path,
    models_path: Path,
    policy_dir: Path,
    baselines: str = "all",
) -> AccuracyResult:
    """Evaluate Cyprus accuracy against ground truth annotations."""
    # Load ground truth
    with open(ground_truth_path) as f:
        gt = yaml.safe_load(f)
    gt_models = gt.get("models", {})

    # Run Cyprus
    models = load_models(models_path)
    facts = compile_models(models)
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    # Compare per predicate
    predicates = ["prohibited", "high_risk", "systemic_risk", "can_deploy"]
    cyprus_metrics: dict[str, PredicateMetrics] = {}
    confusion: dict[str, list[list[int]]] = {}

    for pred in predicates:
        tp = fp = fn = 0
        for mid, gt_labels in gt_models.items():
            gt_val = gt_labels.get(pred, False)
            if mid in result.models:
                mc = result.models[mid]
                if pred == "prohibited":
                    pred_val = mc.status.value == "prohibited"
                elif pred == "high_risk":
                    pred_val = mc.high_risk
                elif pred == "systemic_risk":
                    pred_val = mc.systemic_risk
                else:
                    pred_val = mc.can_deploy
            else:
                pred_val = False

            if gt_val and pred_val:
                tp += 1
            elif pred_val and not gt_val:
                fp += 1
            elif gt_val and not pred_val:
                fn += 1

        cyprus_metrics[pred] = PredicateMetrics(pred, tp, fp, fn)
        confusion[pred] = [[tp, fp], [fn, 0]]

    # Baselines
    baseline_metrics: dict[str, dict[str, PredicateMetrics]] = {}
    if baselines in ("all", "heuristic"):
        heuristic = _run_heuristic_baseline(models)
        baseline_metrics["heuristic"] = _compute_baseline_metrics(heuristic, gt_models, predicates)
    if baselines in ("all", "keyword"):
        keyword = _run_keyword_baseline(models)
        baseline_metrics["keyword"] = _compute_baseline_metrics(keyword, gt_models, predicates)

    return AccuracyResult(cyprus_metrics, baseline_metrics, confusion)


def _compute_baseline_metrics(
    predictions: dict[str, dict[str, bool]],
    gt_models: dict,
    predicates: list[str],
) -> dict[str, PredicateMetrics]:
    metrics = {}
    for pred in predicates:
        tp = fp = fn = 0
        for mid, gt_labels in gt_models.items():
            gt_val = gt_labels.get(pred, False)
            pred_val = predictions.get(mid, {}).get(pred, False)
            if gt_val and pred_val:
                tp += 1
            elif pred_val and not gt_val:
                fp += 1
            elif gt_val and not pred_val:
                fn += 1
        metrics[pred] = PredicateMetrics(pred, tp, fp, fn)
    return metrics


def _run_heuristic_baseline(models: list) -> dict[str, dict[str, bool]]:
    """Simple Python if/else rules implementing the same articles."""
    results = {}
    prohibited_uses = {"social_scoring", "cognitive_manipulation", "biometric_surveillance"}
    high_risk_uses = {"healthcare", "law_enforcement", "critical_infrastructure", "employment", "education"}

    for m in models:
        mid = m.model_id
        is_prohibited = m.use_case.value in prohibited_uses
        is_high_risk = m.risk_category.value == "high_risk" or m.use_case.value in high_risk_uses
        is_systemic = m.compute_flops > 1e25 or len(m.capabilities) >= 5

        can_deploy = not is_prohibited
        if is_high_risk and can_deploy:
            can_deploy = (
                m.red_teaming_status.value == "completed"
                and m.governance.training_data.quality_score >= 0.85
                and m.governance.bias_assessment.status == "completed"
                and m.governance.training_data.documentation_status == "complete"
            )

        results[mid] = {
            "prohibited": is_prohibited,
            "high_risk": is_high_risk,
            "systemic_risk": is_systemic,
            "can_deploy": can_deploy,
        }
    return results


def _run_keyword_baseline(models: list) -> dict[str, dict[str, bool]]:
    """Naive keyword matching on use_case and capability fields."""
    results = {}
    prohibited_keywords = {"social", "scoring", "manipulation", "surveillance", "biometric"}
    high_risk_keywords = {"health", "law", "enforcement", "infrastructure", "employment", "education"}

    for m in models:
        mid = m.model_id
        use_str = m.use_case.value.lower()
        cap_str = " ".join(m.capabilities).lower()
        all_text = use_str + " " + cap_str

        is_prohibited = any(kw in all_text for kw in prohibited_keywords)
        is_high_risk = any(kw in all_text for kw in high_risk_keywords)

        results[mid] = {
            "prohibited": is_prohibited,
            "high_risk": is_high_risk,
            "systemic_risk": False,
            "can_deploy": not is_prohibited,
        }
    return results


def format_accuracy_result(result: AccuracyResult, fmt: str = "table") -> str:
    """Format accuracy results for display."""
    if fmt == "json":
        data = {
            "cyprus": {
                k: {"precision": v.precision, "recall": v.recall, "f1": v.f1}
                for k, v in result.cyprus_metrics.items()
            },
            "baselines": {
                name: {
                    k: {"precision": v.precision, "recall": v.recall, "f1": v.f1}
                    for k, v in metrics.items()
                }
                for name, metrics in result.baseline_metrics.items()
            },
        }
        return json.dumps(data, indent=2)

    # Table/CSV format
    from rich.table import Table
    from rich.console import Console
    import io

    table = Table(title="Accuracy Benchmark")
    table.add_column("Method")
    table.add_column("Predicate")
    table.add_column("Precision", justify="right")
    table.add_column("Recall", justify="right")
    table.add_column("F1", justify="right")

    for pred, m in result.cyprus_metrics.items():
        table.add_row("Cyprus", pred, f"{m.precision:.3f}", f"{m.recall:.3f}", f"{m.f1:.3f}")

    for name, metrics in result.baseline_metrics.items():
        for pred, m in metrics.items():
            table.add_row(name, pred, f"{m.precision:.3f}", f"{m.recall:.3f}", f"{m.f1:.3f}")

    buf = io.StringIO()
    console = Console(file=buf, force_terminal=True)
    console.print(table)
    return buf.getvalue()
