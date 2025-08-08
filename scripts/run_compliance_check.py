import argparse

from cyprus.core.policy_engine import create_policy_engine_from_files
from cyprus.config import DEFAULT_POLICY_FILES, DEFAULT_REGISTRY_PATH


def run_check(policy_files: list, registry_path: str):
    """
    Loads policies and the model registry, then runs a comprehensive
    set of compliance and governance queries.
    """
    print("Loading policies and model registry...")
    try:
        policy_engine = create_policy_engine_from_files(policy_files, registry_path)
        print(f"  - Loaded {len(policy_files)} policy files.")
        print(f"  - Loaded {len(policy_engine.registry.models)} models.")
    except Exception as e:
        print(f"Error creating policy engine: {e}")
        return

    # --- Run Compliance Queries ---
    print("\n--- Compliance & Governance Report ---")

    # Query for all models using the new model/10 predicate
    all_models = policy_engine.get_all_models()
    
    # Query for prohibited models (EU AI Act)
    prohibited_models = policy_engine.get_restricted_models()

    # Query for deployable models (EU AI Act)
    deployable_models = policy_engine.get_deployable_models()
    
    # Query for models that are not production ready (Governance Rules)
    not_ready_sol = policy_engine.engine.query("not_production_ready(Model)")
    not_ready_models = {sol['Model'] for sol in not_ready_sol}


    print(f"\nTotal Models: {len(all_models)}")
    print(sorted(list(all_models)))

    print(f"\nProhibited by EU AI Act ({len(prohibited_models)}):")
    print(sorted(list(prohibited_models)) or "(None)")

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
        default=DEFAULT_REGISTRY_PATH,
        help="Path to the model registry JSON file.",
    )
    args = parser.parse_args()

    # If no policy files are specified, load both default sets of rules.
    if not args.policy_files:
        args.policy_files = DEFAULT_POLICY_FILES

    run_check(args.policy_files, args.registry)


if __name__ == "__main__":
    main()
