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

@router.get("/models/restricted", summary="Get Restricted Models", response_model=List[str])
def get_restricted_models(policy_version: Optional[str] = None):
    """
    Retrieves a list of all models flagged as 'restricted'.
    You can optionally specify a `policy_version` (e.g., "v1", "v2").
    """
    models = policy_engine.get_restricted_models(policy_version=policy_version)
    return sorted(list(models))

@router.get("/models/potentially_restricted", summary="Get Potentially Restricted Models with Confidence")
def get_potentially_restricted_models():
    """
    Retrieves a mapping of models that are 'potentially restricted'
    to the confidence level of that assessment.
    """
    return policy_engine.get_potentially_restricted_models()

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
