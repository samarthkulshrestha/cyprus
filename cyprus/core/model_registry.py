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
        """Formats model data into a Prolog fact string."""
        
        def sanitize(value):
            """Quote strings with spaces to make them valid Prolog atoms."""
            if isinstance(value, str) and any(char in value for char in ' -.'):
                return f"'{value}'"
            return value

        model_id = sanitize(model_data.get("model_id", "unknown"))
        org = sanitize(model_data.get("organization", "unknown"))
        compute = model_data.get("compute_flops", 0)
        risk = model_data.get("risk_score", 0)
        confidence = model_data.get("risk_confidence", 0.5) # Default confidence
        
        return f"model({model_id}, org({org}), compute({compute}), risk_score({risk}, confidence({confidence})))"

    def load_into_engine(self):
        """
        Loads all models from the JSON registry into the Prolog engine as facts.
        It clears and pre-existing model facts to ensure a clean slate.
        """
        # Clear existing model and red_teamed facts
        self.engine.retractall("model(_,_,_,_)")
        self.engine.retractall("red_teamed(_)")

        for model_data in self.models:
            # Assert the main model fact
            fact = self._format_fact(model_data)
            self.engine.assertz(fact)

            # Assert additional facts like red_teamed status
            if model_data.get("red_teamed", False):
                self.engine.assertz(f"red_teamed({model_data['model_id']})")
