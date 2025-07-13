import re
from typing import Dict, Any

def estimate_compute(model_data: Dict[str, Any]) -> float:
    """
    Estimates the training compute (FLOPs) for a model using heuristics
    based on rich model card data.
    """
    # --- Stage 1: Look for parameter counts in tags ---
    tags = model_data.get("tags", [])
    for tag in tags:
        # Look for tags like "8b", "70b", "250m"
        param_match = re.search(r'(\d+)([bm])', tag)
        if param_match:
            num = int(param_match.group(1))
            unit = param_match.group(2)

            num_params = 0
            if unit == 'b':
                num_params = num * 1e9
            elif unit == 'm':
                num_params = num * 1e6

            if num_params > 0:
                # Scaling Law: FLOPs ≈ 6 * N * D
                # Assume D (tokens) is 20 * N for optimal training.
                return 120 * (num_params ** 2)

    # --- Stage 2: Fallback to model ID regex (less reliable) ---
    model_id = model_data.get("model_id", "").lower()
    param_match = re.search(r'(\d+)([bm])', model_id)
    if param_match:
        num = int(param_match.group(1))
        unit = param_match.group(2)
        num_params = num * (1e9 if unit == 'b' else 1e6)
        return 120 * (num_params ** 2)

    # --- Stage 3: Fallback to keyword-based estimation ---
    if "large" in model_id:
        return 5e24
    if "base" in model_id:
        return 1e24

    return 1e22 # Default low value
