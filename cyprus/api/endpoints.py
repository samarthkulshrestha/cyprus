from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Optional
from cyprus.core.policy_engine import PolicyEngine

# --- Configuration ---
# In a real app, these would come from a config file
POLICY_FILES = ["cyprus/policies/eu_ai_act.pl"]
REGISTRY_PATH = "data/models/registry.json"

# --- Engine Initialization ---
# This creates a global engine instance for the API to use.
policy_engine = PolicyEngine(policy_files=POLICY_FILES, registry_path=REGISTRY_PATH)

# --- API Router ---
router = APIRouter()

@router.get("/", summary="API Health Check")
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Cyprus Policy Engine API is running."}

@router.get("/models", summary="Get All Models and Their Compliance")
def get_all_models():
    """
    Retrieves a list of all models in the registry and their compliance status.
    """
    all_models = policy_engine.get_all_models()
    return [policy_engine.get_model_compliance_status(m) for m in sorted(list(all_models))]

@router.get("/models/prohibited", summary="Get Prohibited Models", response_model=List[str])
def get_prohibited_models():
    """
    Retrieves a list of all models flagged as 'prohibited' by Article 5
    of the EU AI Act.
    """
    # The old get_restricted_models now maps to the new core prohibition rule
    models = policy_engine.get_restricted_models()
    return sorted(list(models))

@router.get("/models/systemic_risk", summary="Get Systemic Risk Models", response_model=List[str])
def get_systemic_risk_models():
    """Retrieves a list of models classified as systemic risk."""
    solutions = policy_engine.engine.query("is_systemic_risk(Model)")
    return sorted([sol['Model'] for sol in solutions])

@router.get("/models/deployable", summary="Get Deployable Models", response_model=List[str])
def get_deployable_models():
    """Retrieves a list of all models that are 'deployable'."""
    return sorted(list(policy_engine.get_deployable_models()))

@router.get("/models/{model_id}/compliance", summary="Get Compliance Status for a Single Model")
def get_model_compliance(model_id: str = Path(..., description="The ID of the model to check.")):
    """
    Checks the compliance status of a single, specified model.
    """
    status = policy_engine.get_model_compliance_status(model_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found in registry.")
    return status

@router.get("/models/{model_id}/governance_report", summary="Get Full Governance Report for a Model")
def get_governance_report(model_id: str = Path(..., description="The ID of the model to report on.")):
    """
    Retrieves a comprehensive governance report containing all known
    facts for a single, specified model.
    """
    report = policy_engine.get_governance_report(model_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found in registry.")
    return report
