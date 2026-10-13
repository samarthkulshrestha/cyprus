import math
import re
from typing import Any

import requests


def scrape_model(model_id: str) -> dict[str, Any]:
    """
    Scrape model metadata from HuggingFace and return a dict
    conforming to the ModelEntry schema.
    """
    resp = requests.get(f"https://huggingface.co/api/models/{model_id}")
    resp.raise_for_status()
    info = resp.json()

    sanitized_id = _sanitize_model_id(model_id)
    compute = _estimate_compute(info)
    risk_score = _estimate_risk_score(info, compute)

    # Infer use case from pipeline_tag
    pipeline_tag = info.get("pipeline_tag", "")
    use_case = _infer_use_case(pipeline_tag)

    # Infer capabilities
    capabilities = _infer_capabilities(info)

    # Organization
    org = model_id.split("/")[0] if "/" in model_id else "unknown"

    return {
        "model_id": sanitized_id,
        "organization": org,
        "compute_flops": compute,
        "risk_score": round(risk_score, 2),
        "risk_category": "minimal_risk",
        "use_case": use_case,
        "red_teaming_status": "not_started",
        "deployment_regions": ["global"],
        "capabilities": capabilities if capabilities else ["general"],
        "governance": {
            "training_data": {
                "source": "publicly_available",
                "quality_score": 0.5,
                "size_tokens": 1e12,
                "documentation_status": "incomplete",
            },
            "bias_assessment": {
                "methodology": "unknown",
                "status": "not_started",
                "score": 0.5,
            },
            "performance": {
                "f1_score": 0.5,
                "benchmark": "unknown",
                "task": "general",
            },
            "security": {
                "access_control": "none",
                "audit_logging": False,
            },
        },
        "_needs_review": True,
    }


def _estimate_compute(model_info: dict) -> float:
    """Estimate training compute in FLOPs."""
    # Try safetensors metadata for parameter count
    safetensors = model_info.get("safetensors", {})
    params = safetensors.get("total", 0) if isinstance(safetensors, dict) else 0

    if not params:
        # Try to parse from model name
        model_id = model_info.get("modelId", "")
        params = _parse_param_count(model_id)

    if params > 0:
        # Chinchilla-optimal: tokens ~ 20 * params
        tokens = 20 * params
        return 6.0 * params * tokens

    return 0.0


def _parse_param_count(model_id: str) -> int:
    """Parse parameter count from model name patterns like '7B', '13B', '70B'."""
    match = re.search(r"(\d+\.?\d*)\s*[bB]", model_id)
    if match:
        return int(float(match.group(1)) * 1e9)
    return 0


def _estimate_risk_score(model_info: dict, compute: float) -> float:
    """Estimate risk score (0.0-1.0) using a weighted rubric."""
    score = 0.0

    # Compute magnitude (0.25 weight)
    if compute > 0:
        log_compute = math.log10(compute)
        compute_norm = min(max((log_compute - 18) / 9, 0), 1)  # Normalize 1e18 to 1e27
        score += 0.25 * compute_norm

    # Downloads as deployment breadth proxy (0.10 weight)
    downloads = model_info.get("downloads", 0)
    if downloads > 0:
        dl_norm = min(math.log10(downloads + 1) / 7, 1.0)
        score += 0.10 * dl_norm

    # License permissiveness (0.15 weight)
    tags = model_info.get("tags", [])
    license_tags = [t for t in tags if t.startswith("license:")]
    if license_tags:
        lic = license_tags[0].split(":", 1)[1]
        if lic in ("apache-2.0", "mit", "bsd"):
            score += 0.15 * 0.3
        elif lic in ("gpl", "agpl"):
            score += 0.15 * 0.5
        else:
            score += 0.15 * 0.6

    # Base score for having a model
    score += 0.20

    return min(score, 1.0)


def _infer_use_case(pipeline_tag: str) -> str:
    """Infer use case from HuggingFace pipeline tag."""
    mapping = {
        "text-generation": "general_purpose",
        "text2text-generation": "general_purpose",
        "conversational": "general_purpose",
        "text-classification": "general_purpose",
        "image-classification": "general_purpose",
        "object-detection": "general_purpose",
        "text-to-image": "content_generation",
        "image-to-text": "content_generation",
        "summarization": "general_purpose",
        "translation": "general_purpose",
    }
    return mapping.get(pipeline_tag, "general_purpose")


def _infer_capabilities(model_info: dict) -> list[str]:
    """Infer capabilities from model metadata."""
    caps = set()
    pipeline_tag = model_info.get("pipeline_tag", "")

    if pipeline_tag in ("text-generation", "conversational", "text2text-generation"):
        caps.add("chat")
    if pipeline_tag in ("text-to-image", "image-to-text"):
        caps.add("image_generation")
    if "code" in model_info.get("modelId", "").lower():
        caps.add("code_generation")

    tags = model_info.get("tags", [])
    if "summarization" in tags:
        caps.add("summarization")
    if "translation" in tags:
        caps.add("translation")

    return sorted(caps) if caps else ["general"]


def _sanitize_model_id(model_id: str) -> str:
    """Convert HuggingFace model ID to a valid ASP atom."""
    sanitized = model_id.lower()
    sanitized = re.sub(r"[/\-.\s]+", "_", sanitized)
    sanitized = re.sub(r"[^a-z0-9_]", "", sanitized)
    return sanitized
