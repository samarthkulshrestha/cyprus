import re
from typing import Dict, Any

def estimate_compute(model_data: Dict[str, Any]) -> float:
    """
    Estimates the compute required for a model based on its name.
    This is a heuristic-based placeholder. A real implementation would be
    far more complex.
    """
    model_id = model_data.get("model_id", "").lower()

    # Look for parameter counts in the name (e.g., "7b", "70b")
    param_match = re.search(r'(\d+)b', model_id)
    if param_match:
        num_params = int(param_match.group(1))
        # Using Chinchilla's scaling law: FLOPs ≈ 2 * N * D
        # where N is params and D is tokens. Assume 20 tokens per param.
        # This is a very rough approximation.
        return 2 * (num_params * 1e9) * (20 * num_params * 1e9)

    # Look for size keywords
    if "large" in model_id:
        return 5e24
    if "base" in model_id:
        return 1e24
    if "small" in model_id:
        return 5e23

    # Default value if no other information is found
    return 1e23
