import json
from typing import List, Dict, Any
from cyprus.core.prolog_engine import PrologEngine

class ModelRegistry:
    """
    Manages loading model data from a JSON registry into the Prolog engine.
    """
    def __init__(self, registry_path: str, engine: PrologEngine):
        self.registry_path = registry_path
        self.engine = engine
        self.models = self._load_from_json()

    def _load_from_json(self) -> List[Dict[str, Any]]:
        """Loads the model registry from a JSON file."""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading model registry from {self.registry_path}: {e}")
            return []

    def _sanitize_prolog_term(self, value: Any) -> str:
        """
        Recursively sanitizes a Python value into a valid Prolog term string.
        - Quotes strings that aren't valid numbers.
        - Converts Python lists to Prolog lists.
        """
        if isinstance(value, str):
            # If it can be a number, don't quote it.
            try:
                float(value)
                return value
            except (ValueError, TypeError):
                # Otherwise, quote it to make it a valid Prolog atom.
                return f"'{value}'"
        if isinstance(value, list):
            # Recursively sanitize list elements and format as a Prolog list.
            return f"[{', '.join(self._sanitize_prolog_term(v) for v in value)}]"
        # For numbers, bools, etc., just convert to string.
        return str(value).lower() # .lower() for true/false

    def _format_model_fact(self, model_data: Dict[str, Any]) -> str:
        """Formats the core model data into a model/10 Prolog fact string."""
        model_id = self._sanitize_prolog_term(model_data.get("model_id", "unknown"))
        org = self._sanitize_prolog_term(model_data.get("organization", "unknown"))
        compute = self._sanitize_prolog_term(model_data.get("compute_flops", 0))
        risk = self._sanitize_prolog_term(model_data.get("risk_score", 0))

        deployment_region = self._sanitize_prolog_term(model_data.get("deployment_region", []))
        alignment = self._sanitize_prolog_term(model_data.get("alignment_methodology", []))
        capabilities = self._sanitize_prolog_term(model_data.get("capabilities", []))
        red_teaming = self._sanitize_prolog_term(model_data.get("red_teaming_status", "unknown"))

        # New fields for EU AI Act
        risk_category = self._sanitize_prolog_term(model_data.get("risk_category", "minimal_risk"))
        use_case = self._sanitize_prolog_term(model_data.get("use_case", "unknown"))

        return (f"model({model_id}, org({org}), compute({compute}), risk_score({risk}), "
                f"deployment_region({deployment_region}), alignment_methodology({alignment}), "
                f"capabilities({capabilities}), red_teaming_status({red_teaming}), "
                f"risk_category({risk_category}), use_case({use_case}))")

    def load_into_engine(self):
        """
        Loads all models and their associated governance facts from the
        JSON registry into the Prolog engine.
        """
        # Retract all old facts before asserting new ones
        self.engine.retractall("model(_,_,_,_,_,_,_,_,_,_)") # Updated for model/10
        self.engine.retractall("red_teamed(_)")
        self.engine.retractall("training_data(_,_,_,_,_)")
        self.engine.retractall("bias_assessment(_,_,_,_,_)")
        self.engine.retractall("performance_metrics(_,_,_,_,_,_)")
        self.engine.retractall("security_measures(_,_,_,_)")

        for model_data in self.models:
            model_id_sanitized = self._sanitize_prolog_term(model_data['model_id'])

            # Assert the main model/10 fact
            model_fact = self._format_model_fact(model_data)
            self.engine.assertz(model_fact)

            # Assert the simple red_teamed fact for backward compatibility
            if model_data.get("red_teaming_status") == "completed":
                self.engine.assertz(f"red_teamed({model_id_sanitized})")

            # Assert detailed governance facts
            gov_facts = model_data.get("governance_facts", {})

            if "training_data" in gov_facts:
                td = gov_facts["training_data"]
                fact = (f"training_data({model_id_sanitized}, {self._sanitize_prolog_term(td.get('data_source'))}, "
                        f"{self._sanitize_prolog_term(td.get('data_size'))}, {self._sanitize_prolog_term(td.get('data_date_range'))}, "
                        f"{self._sanitize_prolog_term(td.get('data_quality_score'))})")
                self.engine.assertz(fact)

            if "bias_assessment" in gov_facts:
                ba = gov_facts["bias_assessment"]
                groups = self._sanitize_prolog_term(ba.get('affected_groups', []))
                fact = (f"bias_assessment({model_id_sanitized}, {self._sanitize_prolog_term(ba.get('test_date'))}, "
                        f"{self._sanitize_prolog_term(ba.get('bias_metrics'))}, {groups}, "
                        f"{self._sanitize_prolog_term(ba.get('mitigation_status'))})")
                self.engine.assertz(fact)

            if "performance_metrics" in gov_facts:
                pm = gov_facts["performance_metrics"]
                fact = (f"performance_metrics({model_id_sanitized}, {self._sanitize_prolog_term(pm.get('accuracy'))}, {self._sanitize_prolog_term(pm.get('precision'))}, "
                        f"{self._sanitize_prolog_term(pm.get('recall'))}, {self._sanitize_prolog_term(pm.get('f1_score'))}, {self._sanitize_prolog_term(pm.get('evaluation_date'))})")
                self.engine.assertz(fact)

            if "security_measures" in gov_facts:
                sm = gov_facts["security_measures"]
                fact = (f"security_measures({model_id_sanitized}, {self._sanitize_prolog_term(sm.get('encryption_at_rest'))}, "
                        f"{self._sanitize_prolog_term(sm.get('encryption_in_transit'))}, {self._sanitize_prolog_term(sm.get('access_controls'))})")
                self.engine.assertz(fact)
