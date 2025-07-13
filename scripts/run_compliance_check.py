import argparse
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

def run_check(policy_files: list, registry_path: str):
    """
    Loads policies and the model registry, then runs a comprehensive
    set of compliance and governance queries.
    """
    engine = PrologEngine()
    
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
    print("\n--- Compliance & Governance Report ---")

    # Query for all models
    all_models_sol = engine.query("model(Model, _, _, _, _, _, _, _)")
    all_models = {sol['Model'] for sol in all_models_sol}
    
    # Query for restricted models (EU AI Act)
    restricted_sol = engine.query("restricted(Model)")
    restricted_models = {sol['Model'] for sol in restricted_sol}

    # Query for deployable models (EU AI Act)
    deployable_sol = engine.query("can_deploy(Model)")
    deployable_models = {sol['Model'] for sol in deployable_sol}
    
    # Query for models that are not production ready (Governance Rules)
    not_ready_sol = engine.query("not_production_ready(Model)")
    not_ready_models = {sol['Model'] for sol in not_ready_sol}


    print(f"\nTotal Models: {len(all_models)}")
    print(sorted(list(all_models)))

    print(f"\nRestricted by EU AI Act ({len(restricted_models)}):")
    print(sorted(list(restricted_models)) or "(None)")

    print(f"\nDeployable by EU AI Act ({len(deployable_models)}):")
    print(sorted(list(deployable_models)) or "(None)")
        
    print(f"\nFlagged as 'Not Production Ready' ({len(not_ready_models)}):")
    print(sorted(list(not_ready_models)) or "(None)")

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

    # If no policy files are specified, load both default sets of rules.
    if not args.policy_files:
        args.policy_files = [
            "cyprus/policies/eu_ai_act.pl",
            "cyprus/policies/governance_rules.pl"
        ]

    run_check(args.policy_files, args.registry)


if __name__ == "__main__":
    main()