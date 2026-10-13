import csv
import io
import json

from rich.table import Table
from rich.console import Console

from cyprus.engine.result import ComplianceResult, ComplianceStatus


def format_result(result: ComplianceResult, fmt: str = "table", verbose: bool = False) -> str:
    """
    Format a ComplianceResult for output.

    Args:
        result: ComplianceResult to format
        fmt: One of "table", "json", "csv", "markdown"
        verbose: If True, include violation details per model

    Returns:
        Formatted string
    """
    if fmt == "json":
        return _format_json(result, verbose)
    elif fmt == "csv":
        return _format_csv(result, verbose)
    elif fmt == "markdown":
        return _format_markdown(result, verbose)
    else:
        return _format_table(result, verbose)


def _format_json(result: ComplianceResult, verbose: bool) -> str:
    data = {}
    for mid, mc in result.models.items():
        entry: dict = {
            "status": mc.status.value,
            "can_deploy": mc.can_deploy,
        }
        if verbose:
            entry["prohibited"] = [
                {"article": v.article, "reason": v.reason} for v in mc.prohibited
            ]
            entry["unmet_requirements"] = [
                {"reason": v.reason} for v in mc.unmet_requirements
            ]
            entry["systemic_risk"] = mc.systemic_risk
            entry["high_risk"] = mc.high_risk
            entry["transparency_required"] = mc.transparency_required
        data[mid] = entry
    return json.dumps(data, indent=2)


def _format_csv(result: ComplianceResult, verbose: bool) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    header = ["model_id", "status", "can_deploy"]
    if verbose:
        header.extend(["systemic_risk", "high_risk", "violations"])
    writer.writerow(header)

    for mid, mc in result.models.items():
        row = [mid, mc.status.value, mc.can_deploy]
        if verbose:
            violations = "; ".join(
                v.reason for v in mc.prohibited + mc.unmet_requirements
            )
            row.extend([mc.systemic_risk, mc.high_risk, violations])
        writer.writerow(row)
    return output.getvalue()


def _format_markdown(result: ComplianceResult, verbose: bool) -> str:
    lines = []
    lines.append("| Model | Status | Deploy |")
    lines.append("|-------|--------|--------|")
    for mid, mc in result.models.items():
        lines.append(f"| {mid} | {mc.status.value} | {'Yes' if mc.can_deploy else 'No'} |")
        if verbose and mc.violation_count > 0:
            for v in mc.prohibited + mc.unmet_requirements:
                lines.append(f"| | {v.severity}: {v.reason} | |")
    return "\n".join(lines)


def _format_table(result: ComplianceResult, verbose: bool) -> str:
    table = Table(title="Compliance Results")
    table.add_column("Model", style="bold")
    table.add_column("Status")
    table.add_column("Deploy?")
    if verbose:
        table.add_column("Details")

    for mid, mc in result.models.items():
        status_style = {
            ComplianceStatus.COMPLIANT: "green",
            ComplianceStatus.PROHIBITED: "red bold",
            ComplianceStatus.REQUIRES_ACTION: "yellow",
            ComplianceStatus.NON_COMPLIANT: "red",
        }.get(mc.status, "")

        row = [
            mid,
            f"[{status_style}]{mc.status.value}[/{status_style}]",
            "Yes" if mc.can_deploy else "No",
        ]
        if verbose:
            details = "\n".join(
                v.reason for v in mc.prohibited + mc.unmet_requirements
            ) or "—"
            row.append(details)
        table.add_row(*row)

    buf = io.StringIO()
    console = Console(file=buf, force_terminal=True)
    console.print(table)
    return buf.getvalue()
