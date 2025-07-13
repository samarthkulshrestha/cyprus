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

    def _format_fact(self, model_data: Dict[str, Any]) -> str:
        """Formats model data into a Prolog fact string for model/8."""

        def sanitize(value):
            """Sanitize values for Prolog."""
            if isinstance(value, str):
                # Quote strings with spaces or special chars
                if ' ' in value or '-' in value or '.' in value:
                    return f"'{value}'"
                return value
            if isinstance(value, list):
                # Convert Python list to Prolog list
                return f"[{', '.join(map(sanitize, value))}]"
            return str(value)

        # Core model/8 attributes
        model_id = sanitize(model_data.get("model_id", "unknown"))
        org = sanitize(model_data.get("organization", "unknown"))
        compute = model_data.get("compute_flops", 0)
        risk = model_data.get("risk_score", 0)

        deployment_region = sanitize(model_data.get("deployment_region", []))
        alignment = sanitize(model_data.get("alignment_methodology", []))
        capabilities = sanitize(model_data.get("capabilities", []))
        red_teaming = sanitize(model_data.get("red_teaming_status", "unknown"))

        return (f"model({model_id}, org({org}), compute({compute}), risk_score({risk}), "
                f"deployment_region({deployment_region}), alignment_methodology({alignment}), "
                f"capabilities({capabilities}), red_teaming_status({red_teaming}))")

    def load_into_engine(self):
        """
        Loads all models from the JSON registry into the Prolog engine as facts.
        It clears any pre-existing model facts to ensure a clean slate.
        """
        # Clear existing model and red_teamed facts before loading new ones
        self.engine.retractall("model(_,_,_,_,_,_,_,_)") # Updated for model/8
        self.engine.retractall("red_teamed(_)")

        for model_data in self.models:
            # Assert the main model fact
            fact = self._format_fact(model_data)
            self.engine.assertz(fact)

            # Assert the simple red_teamed fact for backward compatibility with some rules
            if model_data.get("red_teaming_status") == "completed":
                self.engine.assertz(f"red_teamed({model_data['model_id']})")
