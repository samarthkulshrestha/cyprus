from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cyprus.api.endpoints import router as api_router

app = FastAPI(
    title="Cyprus Policy Engine API",
    description="An API for checking AI model compliance against symbolic policies.",
    version="0.1.0",
)

# --- CORS Middleware ---
# This allows the frontend (running on localhost:3000) to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.1.13:3000", "http://0.0.0.0:3000"],  # The origin of the React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include the API endpoints
app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the Cyprus API. Docs are available at /docs"}
