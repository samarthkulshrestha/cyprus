from typing import Dict, Any

def score_risk(model_data: Dict[str, Any]) -> float:
    """
    Assigns a risk score based on model metadata.
    This is a heuristic-based placeholder. A real implementation would use a
    sophisticated rubric.
    """
    organization = model_data.get("organization", "unknown").lower()
    source = model_data.get("source", "unknown").lower()

    # High-risk score for powerful, closed-source models from large labs
    if organization in ["openai", "google", "anthropic", "deepmind"]:
        return 0.8

    # Moderate risk for well-known open-source providers
    if organization in ["meta-llama", "mistralai", "huggingface"]:
        return 0.6

    # Lower risk for models from local cards (implies internal control)
    if source == "local_model_card":
        return 0.3

    # Default medium risk
    return 0.5
