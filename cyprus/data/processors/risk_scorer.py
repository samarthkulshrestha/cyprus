from typing import Dict, Any
import re

def score_risk(model_data: Dict[str, Any]) -> float:
    """
    Assigns a risk score to a model based on a detailed, weighted rubric.

    The scoring starts with a baseline and is adjusted based on various
    factors derived from the model's metadata. The final score is clamped
    between 0.0 and 1.0.

    Rubric Factors:
    - Baseline Risk: Starts at 0.5 (neutral).
    - Organization Type:
        - Major SOTA labs (e.g., OpenAI): +0.3
        - Open-source leaders (e.g., Meta): +0.1
        - Internal/local models: -0.2
    - Model Size (Compute):
        - Very large models (>1e25 FLOPs): +0.2
        - Large models (>1e24 FLOPs): +0.1
    - Potential Capabilities (inferred from name):
        - "code" or "agent" in name: +0.2 (higher potential for misuse)
        - "chat" or "instruct" in name: +0.1 (general purpose)

    Args:
        model_data: A dictionary containing model metadata.

    Returns:
        A float risk score between 0.0 and 1.0.
    """
    # Baseline risk score
    risk = 0.5

    # --- Factor: Organization Type ---
    organization = model_data.get("organization", "unknown").lower()
    source = model_data.get("source", "unknown").lower()

    if organization in ["openai", "google", "anthropic", "deepmind"]:
        risk += 0.3  # Major labs developing SOTA models
    elif organization in ["meta-llama", "mistralai", "huggingface", "meta"]:
        risk += 0.1  # Major open-source contributors
    elif source == "local_model_card":
        risk -= 0.2  # Assumed to be internal, more controlled

    # --- Factor: Model Size (Compute) ---
    compute = model_data.get("compute_flops", 0)
    if compute > 1e25:
        risk += 0.2  # Very large, frontier models
    elif compute > 1e24:
        risk += 0.1  # Large models

    # --- Factor: Potential Capabilities (inferred from name) ---
    model_id = model_data.get("model_id", "").lower()
    if re.search(r'\b(code|agent)\b', model_id):
        risk += 0.2  # Higher potential for misuse
    elif re.search(r'\b(chat|instruct)\b', model_id):
        risk += 0.1  # General-purpose conversational models

    # --- Finalization: Clamp the score between 0.0 and 1.0 ---
    return max(0.0, min(1.0, risk))
