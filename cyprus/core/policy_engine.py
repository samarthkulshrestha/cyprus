import json
from typing import List, Dict, Set, Optional, Any

from cyprus.core.prolog_engine import PrologEngine
from cyprus.core.model_registry import ModelRegistry, ModelRegistryError


def create_policy_engine_from_files(
    policy_files: List[str], registry_path: str
) -> "PolicyEngine":
    """
    Factory function to create a PolicyEngine from policy and registry files.
    """
    policy_rules = []
    for policy_file in policy_files:
        with open(policy_file, "r") as f:
            policy_rules.append(f.read())

    try:
        with open(registry_path, "r") as f:
            model_data = json.load(f)
    except FileNotFoundError:
        raise ModelRegistryError(f"Model registry not found at {registry_path}")
    except json.JSONDecodeError as e:
        raise ModelRegistryError(f"Error decoding JSON from {registry_path}: {e}")

    return PolicyEngine(policy_rules, model_data)


class PolicyEngine:
    """
    A high-level interface for running compliance checks.

    This engine encapsulates the Prolog backend and the model registry,
    providing simple methods to query for compliance status.
    """

    def __init__(self, policy_rules: List[str], model_data: List[Dict[str, Any]]):
        self.engine = PrologEngine()

        # Load policies and rules
        for rule in policy_rules:
            self.engine.consult_string(rule)

        # Load model data
        self.registry = ModelRegistry(model_data, self.engine)
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
        if not list(self.engine.query(f"model('{model_id}', _, _, _, _, _, _, _, _, _)")):
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

        query_and_add('training_data', "training_data('{model_id}', Source, Size, DateRange, Quality)")
        query_and_add('bias_assessment', "bias_assessment('{model_id}', Date, Metrics, Groups, Status)")
        query_and_add('performance', "performance_metrics('{model_id}', Acc, Prec, Rec, F1, Date)")
        query_and_add('security', "security_measures('{model_id}', AtRest, InTransit, Access)")

        return report

    def get_model_details(self, model_id: str) -> Optional[Dict]:
        """
        Returns all available details from the model/10 fact for a given model,
        mirroring the structure used by get_all_models(), plus compliance flags.
        """
        compliance_status = self.get_model_compliance_status(model_id)
        if not compliance_status:
            return None

        query = (
            f"model('{model_id}', org(Org), compute(Compute), risk_score(Risk), "
            f"deployment_region(Regions), alignment_methodology(Align), capabilities(Caps), "
            f"red_teaming_status(RT), risk_category(RiskCategory), use_case(UseCase))"
        )
        solutions = self.engine.query(query)

        if not solutions:
            return { **compliance_status }

        s = solutions[0]
        def deatom(v):
            return v.strip("'") if isinstance(v, str) else v

        return {
            **compliance_status,
            "organization": deatom(s.get('Org','unknown')),
            "compute": deatom(s.get('Compute', 0)),
            "risk_score": deatom(s.get('Risk', 0)),
            "deployment_region": deatom(s.get('Regions', [])),
            "alignment_methodology": deatom(s.get('Align', [])),
            "capabilities": deatom(s.get('Caps', [])),
            "red_teaming_status": deatom(s.get('RT', 'unknown')),
            "risk_category": deatom(s.get('RiskCategory', 'unknown')),
            "use_case": deatom(s.get('UseCase', 'unknown')),
        }

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
        Checks the compliance status of a single model efficiently.

        Args:
            model_id: The ID of the model to check.

        Returns:
            A dictionary with compliance details, or None if the model is not found.
        """
        # Check if model exists
        if not list(self.engine.query(f"model('{model_id}', _, _, _, _, _, _, _, _, _)")):
            return None

        is_restricted = bool(self.engine.query(f"prohibited_deployment('{model_id}')"))
        is_deployable = bool(self.engine.query(f"can_deploy('{model_id}')"))

        return {
            "model_id": model_id,
            "is_compliant": is_deployable,
            "is_restricted": is_restricted,
            "is_deployable": is_deployable,
        }
