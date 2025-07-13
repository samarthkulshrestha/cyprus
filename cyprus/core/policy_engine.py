from typing import List, Dict, Set, Optional
from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry

class PolicyEngine:
    """
    A high-level interface for running compliance checks.

    This engine encapsulates the Prolog backend and the model registry,
    providing simple methods to query for compliance status.
    """
    def __init__(self, policy_files: List[str], registry_path: str):
        self.engine = PrologEngine()
        self.registry_path = registry_path

        # Load policies and rules
        for policy_file in policy_files:
            self.engine.load_file(policy_file)

        # Load model data
        self.registry = ModelRegistry(self.registry_path, self.engine)
        self.registry.load_into_engine()

    def get_all_models(self) -> Set[str]:
        """Returns a set of all model IDs in the registry."""
        solutions = self.engine.query("model(Model, _, _, _)")
        return {sol['Model'] for sol in solutions}

    def get_restricted_models(self) -> Set[str]:
        """Returns a set of all models flagged as 'restricted'."""
        solutions = self.engine.query("restricted(Model)")
        return {sol['Model'] for sol in solutions}

    def get_deployable_models(self) -> Set[str]:
        """Returns a set of all models that are 'deployable'."""
        solutions = self.engine.query("can_deploy(Model)")
        return {sol['Model'] for sol in solutions}

    def get_model_compliance_status(self, model_id: str) -> Optional[Dict]:
        """
        Checks the compliance status of a single model.

        Args:
            model_id: The ID of the model to check.

        Returns:
            A dictionary with compliance details, or None if the model is not found.
        """
        all_models = self.get_all_models()
        if model_id not in all_models:
            return None

        is_restricted = model_id in self.get_restricted_models()
        is_deployable = model_id in self.get_deployable_models()

        return {
            "model_id": model_id,
            "is_compliant": is_deployable, # Simple definition of compliance
            "is_restricted": is_restricted,
            "is_deployable": is_deployable,
        }
