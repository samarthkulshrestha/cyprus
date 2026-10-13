import json
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AgreementResult:
    """Inter-annotator agreement metrics."""
    overall_kappa: float
    per_predicate_kappa: dict[str, float]
    annotator_count: int
    model_count: int


def compute_agreement(annotations_dir: Path) -> AgreementResult:
    """
    Compute inter-annotator agreement using Fleiss' kappa.

    Each annotator file is a YAML file with the same format as ground truth.
    """
    # Load all annotator files
    annotator_files = sorted(annotations_dir.glob("*.yaml")) + sorted(annotations_dir.glob("*.yml"))
    if len(annotator_files) < 2:
        raise ValueError(f"Need at least 2 annotator files, found {len(annotator_files)}")

    annotators = []
    for f in annotator_files:
        data = yaml.safe_load(f.read_text())
        annotators.append(data.get("models", {}))

    # Get all model IDs
    all_models = set()
    for a in annotators:
        all_models.update(a.keys())

    predicates = ["prohibited", "high_risk", "systemic_risk", "can_deploy"]
    n_annotators = len(annotators)

    per_pred_kappa: dict[str, float] = {}
    all_kappas = []

    for pred in predicates:
        # Build rating matrix: for each model, count how many annotators said True/False
        ratings = []
        for mid in sorted(all_models):
            true_count = sum(
                1 for a in annotators if a.get(mid, {}).get(pred, False)
            )
            false_count = n_annotators - true_count
            ratings.append([true_count, false_count])

        kappa = _fleiss_kappa(ratings, n_annotators)
        per_pred_kappa[pred] = kappa
        all_kappas.append(kappa)

    overall = sum(all_kappas) / len(all_kappas) if all_kappas else 0.0

    return AgreementResult(
        overall_kappa=overall,
        per_predicate_kappa=per_pred_kappa,
        annotator_count=n_annotators,
        model_count=len(all_models),
    )


def _fleiss_kappa(ratings: list[list[int]], n_raters: int) -> float:
    """
    Compute Fleiss' kappa from a rating matrix.

    ratings: list of [count_category_0, count_category_1, ...] per subject
    n_raters: number of raters
    """
    n_subjects = len(ratings)
    if n_subjects == 0 or n_raters < 2:
        return 0.0

    n_categories = len(ratings[0])

    # P_i for each subject
    p_i_list = []
    for row in ratings:
        p_i = (sum(n_j * (n_j - 1) for n_j in row)) / (n_raters * (n_raters - 1))
        p_i_list.append(p_i)

    p_bar = sum(p_i_list) / n_subjects

    # p_j for each category
    total_ratings = n_subjects * n_raters
    p_j = []
    for j in range(n_categories):
        col_sum = sum(row[j] for row in ratings)
        p_j.append(col_sum / total_ratings)

    p_e = sum(pj * pj for pj in p_j)

    if abs(1.0 - p_e) < 1e-10:
        return 1.0 if abs(p_bar - 1.0) < 1e-10 else 0.0

    return (p_bar - p_e) / (1.0 - p_e)


def format_agreement_result(result: AgreementResult, fmt: str = "table") -> str:
    """Format agreement results for display."""
    if fmt == "json":
        data = {
            "overall_kappa": result.overall_kappa,
            "per_predicate": result.per_predicate_kappa,
            "annotator_count": result.annotator_count,
            "model_count": result.model_count,
        }
        return json.dumps(data, indent=2)

    from rich.table import Table
    from rich.console import Console
    import io

    table = Table(title="Inter-Annotator Agreement")
    table.add_column("Predicate")
    table.add_column("Fleiss' kappa", justify="right")
    table.add_column("Interpretation")

    for pred, kappa in result.per_predicate_kappa.items():
        interp = _interpret_kappa(kappa)
        table.add_row(pred, f"{kappa:.3f}", interp)

    table.add_row("[bold]Overall[/bold]", f"[bold]{result.overall_kappa:.3f}[/bold]",
                  _interpret_kappa(result.overall_kappa), style="bold")

    buf = io.StringIO()
    console = Console(file=buf, force_terminal=True)
    console.print(table)
    console.print(f"\nAnnotators: {result.annotator_count}, Models: {result.model_count}")
    return buf.getvalue()


def _interpret_kappa(kappa: float) -> str:
    if kappa < 0:
        return "Poor"
    elif kappa < 0.20:
        return "Slight"
    elif kappa < 0.40:
        return "Fair"
    elif kappa < 0.60:
        return "Moderate"
    elif kappa < 0.80:
        return "Substantial"
    else:
        return "Almost perfect"
