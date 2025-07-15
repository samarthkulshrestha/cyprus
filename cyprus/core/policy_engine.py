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
        solutions = self.engine.query("model(Model, _, _, _, _, _, _, _, _, _)")
        return {sol['Model'] for sol in solutions}

    def get_restricted_models(self, policy_version: Optional[str] = None, interpretation: Optional[str] = None) -> Set[str]:
        """This method is deprecated as 'restricted' is no longer a primary rule."""
        # This now points to the new 'prohibited_deployment' rule for a basic check.
        solutions = self.engine.query("prohibited_deployment(Model)")
        return {sol['Model'] for sol in solutions}

    def get_governance_report(self, model_id: str) -> Optional[Dict]:
        """
        Compiles a full governance report for a single model.

        Args:
            model_id: The ID of the model to report on.

        Returns:
            A dictionary containing all known facts for the model, or None.
        """
        # First, check if the model exists
        if not list(self.engine.query(f"model({model_id}, _, _, _, _, _, _, _, _, _)")):
            return None

        report = {'model_id': model_id}

        # Helper to query for facts and add them to the report
        def query_and_add(key, query_template):
            solutions = list(self.engine.query(query_template.format(model_id=model_id)))
            if solutions:
                # De-sanitize the Prolog atoms back into normal strings
                cleaned_solution = {k: (v.strip("'") if isinstance(v, str) else v)
                                    for k, v in solutions[0].items()}
                report[key] = {k: v for k, v in cleaned_solution.items() if k != 'Model'}

        query_and_add('training_data', f"training_data({model_id}, Source, Size, DateRange, Quality)")
        query_and_add('bias_assessment', f"bias_assessment({model_id}, Date, Metrics, Groups, Status)")
        query_and_add('performance', f"performance_metrics({model_id}, Acc, Prec, Rec, F1, Date)")
        query_and_add('security', f"security_measures({model_id}, AtRest, InTransit, Access)")

        return report

    def get_potentially_restricted_models(self) -> Dict[str, float]:
        """
        Returns a dictionary of models that are 'potentially restricted',
        mapping model ID to the calculated confidence level.
        """
        solutions = self.engine.query("potentially_restricted(Model, Confidence)")
        return {sol['Model']: sol['Confidence'] for sol in solutions}

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
