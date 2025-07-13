import argparse
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

def run_check(policy_files: list, registry_path: str):
    """
    Loads policies and the model registry, then runs compliance queries.
    """
    engine = PrologEngine()

    # Load all specified policy and rule files
    print("Loading policies...")
    for policy_file in policy_files:
        try:
            engine.load_file(policy_file)
            print(f"  - Loaded {policy_file}")
        except Exception as e:
            print(f"  - Failed to load {policy_file}: {e}")
            return

    # Load models from the JSON registry
    print(f"\nLoading model registry from '{registry_path}'...")
    registry = ModelRegistry(registry_path, engine)
    registry.load_into_engine()
    print(f"  - Loaded {len(registry.models)} models.")

    # --- Run Compliance Queries ---
    print("\n--- Compliance Report ---")

    # Query for all models
    all_models_sol = engine.query("model(Model, _, _, _)")
    all_models = {sol['Model'] for sol in all_models_sol}

    # Query for restricted models
    restricted_sol = engine.query("restricted(Model)")
    restricted_models = {sol['Model'] for sol in restricted_sol}

    # Query for deployable models
    deployable_sol = engine.query("can_deploy(Model)")
    deployable_models = {sol['Model'] for sol in deployable_sol}

    print(f"\nTotal Models: {len(all_models)}")
    print(list(all_models))

    print(f"\nRestricted Models ({len(restricted_models)}):")
    if restricted_models:
        for model in restricted_models:
            print(f"  - {model}")
    else:
        print("  (None)")

    print(f"\nPotentially Restricted Models ({len(potentially_restricted_models)}):")
    if potentially_restricted_models:
        for model, confidence in potentially_restricted_models.items():
            print(f"  - {model} (Confidence: {confidence:.2f})")
    else:
        print("  (None)")

    print(f"\nDeployable Models ({len(deployable_models)}):")
    if deployable_models:
        for model in deployable_models:
            print(f"  - {model}")
    else:
        print("  (None)")

    non_deployable = all_models - deployable_models
    print(f"\nNon-Deployable Models ({len(non_deployable)}):")
    if non_deployable:
        for model in non_deployable:
            print(f"  - {model}")
    else:
        print("  (None)")

    print("\n--- End of Report ---")


def main():
    parser = argparse.ArgumentParser(description="Run compliance checks against the model registry.")
    parser.add_argument(
        "--policy",
        action="append",
        dest="policy_files",
        default=[],
        help="Path to a policy or rule file to load. Can be specified multiple times.",
    )
    parser.add_argument(
        "--registry",
        default="data/models/registry.json",
        help="Path to the model registry JSON file.",
    )
    args = parser.parse_args()

    # If no policy files are specified, use the default one.
    if not args.policy_files:
        args.policy_files = ["cyprus/policies/eu_ai_act.pl"]

    run_check(args.policy_files, args.registry)


if __name__ == "__main__":
    main()
