import re
from typing import Dict, Any

def estimate_compute(model_data: Dict[str, Any]) -> float:
    """
    Estimates the training compute (FLOPs) for a model using heuristics.

    This implementation uses a multi-stage approach:
    1.  It first looks for explicit parameter counts in the model's name
        (e.g., "llama-3-8b", "gemma-250m").
    2.  If found, it applies a variant of the Chinchilla scaling law, which
        approximates the required training FLOPs. The formula used is:
        FLOPs ≈ 6 * Num_Parameters * Num_Training_Tokens.
        We assume an optimal training dataset size of 20 tokens per parameter.
    3.  If no parameter count is found, it falls back to keyword-based
        estimation based on model size descriptors like "large" or "base".
    4.  If no information can be inferred, it returns a default low value.

    Args:
        model_data: A dictionary containing model metadata, including 'model_id'.

    Returns:
        An estimated float value for the training FLOPs.
    """
    model_id = model_data.get("model_id", "").lower()

    # --- Stage 1 & 2: Estimate from parameter count ---
    param_match = re.search(r'(\d+)([bm])', model_id)
    if param_match:
        num = int(param_match.group(1))
        unit = param_match.group(2)

        num_params = 0
        if unit == 'b':
            num_params = num * 1e9  # Billions
        elif unit == 'm':
            num_params = num * 1e6  # Millions

        if num_params > 0:
            # Scaling Law: FLOPs ≈ 6 * N * D
            # We assume D (tokens) is 20 * N for optimal training (Chinchilla rule).
            # So, FLOPs ≈ 6 * N * (20 * N) = 120 * N^2
            # This is a high-level estimate and the real value can vary significantly.
            return 120 * (num_params ** 2)

    # --- Stage 3: Fallback to keyword-based estimation ---
    if "large" in model_id:
        return 5e24
    if "base" in model_id:
        return 1e24
    if "medium" in model_id:
        return 5e23
    if "small" in model_id:
        return 1e23
    if "tiny" in model_id or "distil" in model_id:
        return 5e22

    # --- Stage 4: Default value ---
    return 1e22
