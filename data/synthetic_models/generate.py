"""
Synthetic model generator for scalability evaluation.

Usage:
    python data/synthetic_models/generate.py
    python data/synthetic_models/generate.py --config custom_config.yaml --output models/

Reads generator_config.yaml, produces individual YAML model files
in the output directory. Fully deterministic given the seed.
"""
import argparse
import math
import random
from pathlib import Path

import yaml


def generate_models(config_path: Path, output_dir: Path) -> int:
    """Generate synthetic model files from a configuration."""
    with open(config_path) as f:
        config = yaml.safe_load(f)

    seed = config.get("seed", 42)
    total = config.get("total_models", 1000)
    rng = random.Random(seed)

    output_dir.mkdir(parents=True, exist_ok=True)

    distributions = config["distributions"]
    edge_cases = config.get("edge_cases", [])

    # Generate base models
    models = []
    for i in range(total):
        model = _generate_single_model(i, distributions, rng)
        models.append(model)

    # Apply edge cases
    idx = 0
    for ec in edge_cases:
        count = ec.get("count", 1)
        overrides = ec.get("overrides", {})
        for _ in range(count):
            if idx < len(models):
                models[idx].update(overrides)
                idx += 1

    # Write each model
    for model in models:
        filename = f"{model['model_id']}.yaml"
        with open(output_dir / filename, "w") as f:
            yaml.dump(model, f, default_flow_style=False, sort_keys=False)

    return len(models)


def _generate_single_model(index: int, distributions: dict, rng: random.Random) -> dict:
    """Generate a single synthetic model."""
    mid = f"synthetic_model_{index:04d}"

    # Sample from weighted distributions
    risk_category = _weighted_choice(distributions["risk_category"], rng)
    use_case = _weighted_choice(distributions["use_case"], rng)
    red_teaming = _weighted_choice(distributions["red_teaming_status"], rng)

    # Compute: log-uniform
    comp_cfg = distributions["compute_flops"]
    log_min = math.log10(comp_cfg["min"])
    log_max = math.log10(comp_cfg["max"])
    compute = 10 ** rng.uniform(log_min, log_max)

    # Risk score: beta distribution approximation
    rs_cfg = distributions["risk_score"]
    risk_score = _beta_sample(rs_cfg["alpha"], rs_cfg["beta"], rng)

    # Capabilities
    capabilities = _sample_capabilities(distributions["capabilities"], rng)
    if not capabilities:
        capabilities = ["general"]

    # Governance
    governance = _sample_governance(rng)

    regions = rng.sample(["eu", "us", "uk", "jp", "kr", "au", "ca", "global"],
                         k=rng.randint(1, 3))

    return {
        "model_id": mid,
        "organization": f"org_{rng.randint(1, 50)}",
        "compute_flops": compute,
        "risk_score": round(risk_score, 2),
        "risk_category": risk_category,
        "use_case": use_case,
        "red_teaming_status": red_teaming,
        "deployment_regions": regions,
        "capabilities": capabilities,
        "governance": governance,
    }


def _weighted_choice(weights: dict[str, float], rng: random.Random) -> str:
    """Sample from a weighted distribution."""
    items = list(weights.keys())
    probs = list(weights.values())
    return rng.choices(items, weights=probs, k=1)[0]


def _beta_sample(alpha: float, beta: float, rng: random.Random) -> float:
    """Sample from a beta distribution using the gamma method."""
    x = rng.gammavariate(alpha, 1.0)
    y = rng.gammavariate(beta, 1.0)
    return x / (x + y) if (x + y) > 0 else 0.5


def _sample_capabilities(cap_probs: dict[str, float], rng: random.Random) -> list[str]:
    """Sample capabilities independently based on per-capability probability."""
    return [cap for cap, prob in cap_probs.items() if rng.random() < prob]


def _sample_governance(rng: random.Random) -> dict:
    """Generate realistic governance facts."""
    sources = ["publicly_available", "proprietary", "mixed", "undocumented"]
    doc_statuses = ["complete", "incomplete", "partial"]
    bias_statuses = ["completed", "in_progress", "not_started"]
    methodologies = ["red_teaming", "adversarial_testing", "statistical_analysis", "unknown"]
    benchmarks = ["mmlu", "hellaswag", "winogrande", "arc", "truthfulqa"]
    access_controls = ["rbac", "api_key", "none", "oauth"]

    return {
        "training_data": {
            "source": rng.choice(sources),
            "quality_score": round(rng.uniform(0.5, 1.0), 2),
            "size_tokens": 10 ** rng.uniform(9, 14),
            "documentation_status": rng.choice(doc_statuses),
        },
        "bias_assessment": {
            "methodology": rng.choice(methodologies),
            "status": rng.choice(bias_statuses),
            "score": round(rng.uniform(0.3, 1.0), 2),
        },
        "performance": {
            "f1_score": round(rng.uniform(0.4, 0.99), 2),
            "benchmark": rng.choice(benchmarks),
            "task": "general",
        },
        "security": {
            "access_control": rng.choice(access_controls),
            "audit_logging": rng.choice([True, False]),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic model files")
    parser.add_argument("--config", type=Path,
                        default=Path(__file__).parent / "generator_config.yaml")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).parent / "models")
    args = parser.parse_args()

    count = generate_models(args.config, args.output)
    print(f"Generated {count} synthetic models in {args.output}")
