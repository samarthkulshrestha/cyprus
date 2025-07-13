from typing import Dict, Any

def score_risk(model_data: Dict[str, Any]) -> float:
    """
    Assigns a risk score based on a detailed, weighted rubric using
    rich model card data.
    """
    risk = 0.5  # Baseline risk

    # --- Factor: Organization Type ---
    organization = model_data.get("organization", "unknown").lower()
    if organization in ["openai", "google", "anthropic", "deepmind"]:
        risk += 0.2
    elif organization in ["meta", "mistralai", "meta-llama"]:
        risk += 0.1

    # --- Factor: Model Capabilities ---
    capabilities = model_data.get("capabilities", [])
    if "multimodal" in capabilities or "agent" in capabilities:
        risk += 0.2
    if "code" in capabilities:
        risk += 0.1

    # --- Factor: License Type ---
    # Restrictive licenses might imply the author knows of risks.
    license = model_data.get("license", "unknown").lower()
    if "restrictive" in license or "research-only" in license:
        risk += 0.15
    elif "open" in license or "mit" in license:
        risk -= 0.1

    # --- Factor: Compute Size ---
    compute = model_data.get("compute_flops", 0)
    if compute > 1e25:
        risk += 0.2
    elif compute > 1e24:
        risk += 0.1

    # --- Finalization: Clamp the score ---
    return max(0.0, min(1.0, risk))
