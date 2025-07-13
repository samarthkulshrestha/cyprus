from fastapi import FastAPI
from cyprus.api.endpoints import router as api_router

app = FastAPI(
    title="Cyprus Policy Engine API",
    description="An API for checking AI model compliance against symbolic policies.",
    version="0.1.0",
)

# Include the API endpoints
app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the Cyprus API. Docs are available at /docs"}
