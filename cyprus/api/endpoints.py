from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List, Dict, Optional

from cyprus.core.policy_engine import create_policy_engine_from_files
from cyprus.config import DEFAULT_POLICY_FILES, DEFAULT_REGISTRY_PATH

# --- Engine Initialization ---
# This creates a global engine instance for the API to use.
policy_engine = create_policy_engine_from_files(
    policy_files=DEFAULT_POLICY_FILES, registry_path=DEFAULT_REGISTRY_PATH
)

# --- API Router ---
router = APIRouter()

# --- Dependencies ---
def get_model_or_404(model_id: str = Path(..., description="The ID of the model to check.")):
    """
    Dependency to get a model by ID, raising a 404 if it doesn't exist.
    """
    if not list(policy_engine.engine.query(f"model('{model_id}', _, _, _, _, _, _, _, _, _)")):
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found in registry.")
    return model_id

@router.get("/", summary="API Health Check")
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Cyprus Policy Engine API is running."}

@router.get("/models", summary="Get All Models and Their Compliance")
def get_all_models(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """
    Retrieves a paginated list of models and their compliance status.
    total_models reflects the number returned in this response.
    """
    all_model_ids = sorted(list(policy_engine.get_all_models()))
    paginated_ids = all_model_ids[skip : skip + limit]
    models_details = [policy_engine.get_model_details(m) for m in paginated_ids]
    return {
        "total_models": len(models_details),
        "models": models_details
    }

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
def get_model_compliance(model_id: str = Depends(get_model_or_404)):
    """
    Checks the compliance status of a single, specified model.
    """
    return policy_engine.get_model_compliance_status(model_id)

@router.get("/models/{model_id}/governance_report", summary="Get Full Governance Report for a Model")
def get_governance_report(model_id: str = Depends(get_model_or_404)):
    """
    Retrieves a comprehensive governance report containing all known
    facts for a single, specified model.
    """
    return policy_engine.get_governance_report(model_id)

@router.post("/reload", summary="Reload Policies and Model Registry")
def reload_engine():
    """
    Reloads the policy engine with the latest policies and model data from disk.
    """
    global policy_engine
    try:
        policy_engine = create_policy_engine_from_files(
            policy_files=DEFAULT_POLICY_FILES, registry_path=DEFAULT_REGISTRY_PATH
        )
        return {"status": "ok", "message": "Policy engine reloaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload policy engine: {e}")
