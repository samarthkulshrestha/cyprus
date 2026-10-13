from pathlib import Path

import yaml


def generate_traceability_matrix(policy_dir: Path) -> str:
    """
    Generate a traceability matrix from a policy module's traceability.yaml.

    The matrix maps: Legal clause -> ASP rule -> Test case -> Coverage status.
    """
    trace_path = policy_dir / "traceability.yaml"
    trace = yaml.safe_load(trace_path.read_text())

    lines = []
    lines.append("# Traceability Matrix")
    lines.append("")
    lines.append("| Article | Clause | Description | Rule File | Predicate | Tests | Coverage |")
    lines.append("|---------|--------|-------------|-----------|-----------|-------|----------|")

    total_clauses = 0
    encoded_clauses = 0

    for article_id, clauses in trace.items():
        for clause_id, info in clauses.items():
            total_clauses += 1
            coverage = info.get("coverage", "not_encoded")
            simplified = info.get("simplified", info.get("reason", ""))

            if coverage == "not_encoded":
                lines.append(
                    f"| {article_id} | {clause_id} | {simplified} | — | — | — | Not encoded |"
                )
            else:
                encoded_clauses += 1
                rules = info.get("rules", [])
                rule_file = rules[0]["file"] if rules else "—"
                predicate = rules[0].get("predicate", "—") if rules else "—"
                tests = info.get("test_cases", [])
                test_count = str(len(tests))
                lines.append(
                    f"| {article_id} | {clause_id} | {simplified} "
                    f"| {rule_file} | {predicate} | {test_count} | Complete |"
                )

    lines.append("")
    pct = (encoded_clauses / total_clauses * 100) if total_clauses else 0
    lines.append(
        f"**Coverage summary:** {encoded_clauses}/{total_clauses} clauses encoded ({pct:.1f}%)"
    )

    return "\n".join(lines)
