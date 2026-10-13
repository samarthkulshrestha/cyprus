import json
from typing import Any

from cyprus.engine.result import ComplianceResult, ComplianceStatus


def generate_report(result: ComplianceResult, fmt: str = "markdown") -> str:
    """
    Generate a full compliance report from a ComplianceResult.

    The report includes:
    - Summary statistics (total, prohibited, compliant, requires action)
    - Per-model compliance status
    - Violation details with article references
    """
    if fmt == "json":
        return _report_json(result)
    elif fmt == "csv":
        return _report_csv(result)
    elif fmt == "table":
        return _report_table(result)
    else:
        return _report_markdown(result)


def _report_markdown(result: ComplianceResult) -> str:
    lines = []
    lines.append(f"# Compliance Report — {result.policy_name} v{result.policy_version}")
    lines.append("")
    lines.append(f"**Date:** {result.timestamp.strftime('%Y-%m-%d')}")
    lines.append(f"**Models evaluated:** {result.total_models}")
    lines.append(f"**Articles checked:** {', '.join(result.articles_evaluated)}")
    lines.append("")

    # Summary counts
    status_counts: dict[str, int] = {}
    for mc in result.models.values():
        label = mc.status.value.replace("_", " ").title()
        if mc.status == ComplianceStatus.COMPLIANT:
            label = "Compliant (can deploy)"
        status_counts[label] = status_counts.get(label, 0) + 1

    lines.append("## Summary")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    for status, count in status_counts.items():
        lines.append(f"| {status} | {count} |")
    lines.append("")

    # Prohibited models
    prohibited = [mc for mc in result.models.values() if mc.status == ComplianceStatus.PROHIBITED]
    if prohibited:
        lines.append("## Prohibited Models")
        lines.append("")
        lines.append("| Model | Article | Reason |")
        lines.append("|-------|---------|--------|")
        for mc in prohibited:
            for v in mc.prohibited:
                lines.append(f"| {mc.model_id} | {v.title} | {v.reason} |")
        lines.append("")

    # Models requiring action
    action = [mc for mc in result.models.values() if mc.status == ComplianceStatus.REQUIRES_ACTION]
    if action:
        lines.append("## Models Requiring Action")
        lines.append("")
        lines.append("| Model | Unmet Requirements |")
        lines.append("|-------|-------------------|")
        for mc in action:
            reqs = ", ".join(v.reason for v in mc.unmet_requirements)
            lines.append(f"| {mc.model_id} | {reqs} |")
        lines.append("")

    # Systemic risk models
    systemic = [mc for mc in result.models.values() if mc.systemic_risk]
    if systemic:
        lines.append("## Systemic Risk Models")
        lines.append("")
        lines.append("| Model | Systemic Risk |")
        lines.append("|-------|--------------|")
        for mc in systemic:
            lines.append(f"| {mc.model_id} | Yes |")
        lines.append("")

    return "\n".join(lines)


def _report_json(result: ComplianceResult) -> str:
    data: dict[str, Any] = {
        "policy": result.policy_name,
        "version": result.policy_version,
        "timestamp": result.timestamp.isoformat(),
        "total_models": result.total_models,
        "articles_evaluated": result.articles_evaluated,
        "models": {},
    }
    for mid, mc in result.models.items():
        data["models"][mid] = {
            "status": mc.status.value,
            "can_deploy": mc.can_deploy,
            "systemic_risk": mc.systemic_risk,
            "high_risk": mc.high_risk,
            "transparency_required": mc.transparency_required,
            "prohibited": [
                {"article": v.article, "reason": v.reason} for v in mc.prohibited
            ],
            "unmet_requirements": [
                {"reason": v.reason} for v in mc.unmet_requirements
            ],
        }
    return json.dumps(data, indent=2)


def _report_csv(result: ComplianceResult) -> str:
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "model_id", "status", "can_deploy", "systemic_risk",
        "high_risk", "violation_count", "violations"
    ])
    for mid, mc in result.models.items():
        violations = "; ".join(
            v.reason for v in mc.prohibited + mc.unmet_requirements
        )
        writer.writerow([
            mid, mc.status.value, mc.can_deploy, mc.systemic_risk,
            mc.high_risk, mc.violation_count, violations
        ])
    return output.getvalue()


def _report_table(result: ComplianceResult) -> str:
    from rich.table import Table
    from rich.console import Console
    import io

    table = Table(title=f"Compliance Report — {result.policy_name}")
    table.add_column("Model", style="bold")
    table.add_column("Status")
    table.add_column("Deploy?")
    table.add_column("Violations", justify="right")

    for mid, mc in result.models.items():
        status_style = {
            ComplianceStatus.COMPLIANT: "green",
            ComplianceStatus.PROHIBITED: "red bold",
            ComplianceStatus.REQUIRES_ACTION: "yellow",
            ComplianceStatus.NON_COMPLIANT: "red",
        }.get(mc.status, "")
        table.add_row(
            mid,
            f"[{status_style}]{mc.status.value}[/{status_style}]",
            "Yes" if mc.can_deploy else "No",
            str(mc.violation_count),
        )

    buf = io.StringIO()
    console = Console(file=buf, force_terminal=True)
    console.print(table)
    return buf.getvalue()
