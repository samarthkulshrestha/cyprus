import math

from cyprus.registry.schema import ModelEntry


def _asp_safe_id(name: str) -> str:
    """Ensure an identifier is a valid ASP constant (must start with a lowercase letter)."""
    if name and not name[0].isalpha():
        return f"m_{name}"
    return name


def compile_models(models: list[ModelEntry]) -> str:
    """
    Convert validated model data into ASP fact strings.

    Each model becomes:
    - One model/1 fact: model(model_id).
    - One model_attr/3 fact per scalar attribute: model_attr(model_id, attr, value).
    - Multiple model_attr/3 facts for list attributes (one per item).
    - model_governance/3 facts for governance sub-attributes.

    Note: All floating-point values are scaled to integers for Clingo compatibility:
    - Scores (0.0-1.0) are scaled by 100 (e.g., 0.85 -> 85)
    - compute_flops is stored as log10 exponent * 100 (e.g., 1e20 -> 2000)
    ASP rules must use the same scale.
    """
    lines: list[str] = []
    for m in models:
        mid = _asp_safe_id(m.model_id)
        lines.append(f"model({mid}).")

        # Scalar attributes
        lines.append(f'model_attr({mid}, organization, "{m.organization}").')
        # compute_flops stored as log10 * 100 to avoid Clingo integer overflow
        compute_log = int(math.log10(m.compute_flops) * 100) if m.compute_flops > 0 else 0
        lines.append(f"model_attr({mid}, compute_flops, {compute_log}).")
        lines.append(f"model_attr({mid}, risk_score, {int(m.risk_score * 100)}).")
        lines.append(f"model_attr({mid}, risk_category, {m.risk_category.value}).")
        lines.append(f"model_attr({mid}, use_case, {m.use_case.value}).")
        lines.append(f"model_attr({mid}, red_teaming_status, {m.red_teaming_status.value}).")

        # Multi-valued: deployment regions
        for region in m.deployment_regions:
            lines.append(f"model_attr({mid}, deployment_region, {region}).")

        # Multi-valued: capabilities
        for cap in m.capabilities:
            lines.append(f"model_attr({mid}, capability, {cap}).")

        # Governance facts (scores scaled by 100)
        g = m.governance
        lines.append(f"model_governance({mid}, training_data_quality, {int(g.training_data.quality_score * 100)}).")
        lines.append(f'model_governance({mid}, training_data_source, "{g.training_data.source}").')
        lines.append(f"model_governance({mid}, training_data_size_tokens, {int(g.training_data.size_tokens)}).")
        lines.append(f'model_governance({mid}, training_documentation_status, "{g.training_data.documentation_status}").')
        lines.append(f'model_governance({mid}, bias_methodology, "{g.bias_assessment.methodology}").')
        lines.append(f'model_governance({mid}, bias_status, "{g.bias_assessment.status}").')
        lines.append(f"model_governance({mid}, bias_score, {int(g.bias_assessment.score * 100)}).")
        lines.append(f"model_governance({mid}, f1_score, {int(g.performance.f1_score * 100)}).")
        lines.append(f'model_governance({mid}, benchmark, "{g.performance.benchmark}").')
        lines.append(f'model_governance({mid}, access_control, "{g.security.access_control}").')
        lines.append(f"model_governance({mid}, audit_logging, {str(g.security.audit_logging).lower()}).")

        lines.append("")  # Blank line between models

    return "\n".join(lines)
