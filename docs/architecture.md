# Cyprus System Architecture

The Cyprus project is designed as a modular system for evaluating AI models against symbolic policy rules. It follows a pipeline architecture where data is collected, processed, stored, and then evaluated by a core reasoning engine. The entire system is exposed via a web API for easy integration.

## Core Components

The system is composed of four main layers:

1.  **Data Pipeline (Scrapers & Processors):** This layer is responsible for gathering raw data about AI models from various sources and enriching it with calculated metadata.
    *   **Scrapers (`cyprus/data/scrapers/`):** Python scripts that fetch model information from external sources (e.g., Hugging Face, Papers with Code) or internal sources (e.g., local Markdown model cards).
    *   **Processors (`cyprus/data/processors/`):** Scripts that take the raw scraped data and generate higher-level attributes, such as an estimated `risk_score` or `compute_flops`.

2.  **Model Registry (`data/models/registry.json`):** A central JSON file that acts as the "database" of facts for the system. It stores the list of all known models and their associated metadata. This file is the primary output of the data pipeline.

3.  **Reasoning Engine (Prolog & Python Wrapper):** This is the heart of Cyprus.
    *   **Prolog Policies (`cyprus/policies/`):** A collection of `.pl` files containing the symbolic logic for compliance. Facts (like `model/4`) and rules (like `restricted/1`) are defined here. Predicates that are modified at runtime are declared `dynamic`.
    *   **Prolog Engine (`cyprus/core/prolog_engine.py`):** A Python class that wraps the `pyswip` library, providing a clean interface for loading Prolog files, asserting facts, and executing queries.
    *   **Model Registry Loader (`cyprus/core/model_registry.py`):** A utility that reads the `registry.json` file and dynamically asserts the model data as facts into the Prolog engine. It also handles data sanitization (e.g., quoting strings with spaces).
    *   **High-Level Policy Engine (`cyprus/core/policy_engine.py`):** An abstraction layer that simplifies compliance checks into straightforward Python methods (e.g., `get_deployable_models()`), hiding the underlying Prolog queries.

4.  **API Layer (FastAPI):** This layer exposes the reasoning engine's capabilities to external clients.
    *   **Server (`cyprus/api/server.py`):** The main FastAPI application entry point.
    *   **Endpoints (`cyprus/api/endpoints.py`):** Defines all the API routes (e.g., `/api/v1/models`, `/api/v1/models/{model_id}/compliance`) and connects them to the high-level `PolicyEngine`.

## Data Flow

The typical data flow through the system is as follows:

1.  A user runs the `scripts/scrape_models.py` script, pointing it to a data source (Hugging Face, a local file, etc.).
2.  The relevant scraper fetches the data.
3.  The data processors estimate the risk score and compute requirements.
4.  The script adds the new, enriched model data to the `data/models/registry.json` file.
5.  When the API server is running, it initializes the `PolicyEngine`.
6.  The `PolicyEngine` loads the Prolog rule files (`.pl`) and then uses the `ModelRegistry` to load all models from `registry.json` as facts into the Prolog database.
7.  A client sends a request to a FastAPI endpoint.
8.  The endpoint calls the appropriate method on the `PolicyEngine`.
9.  The `PolicyEngine` executes a Prolog query (e.g., `can_deploy(Model).`).
10. The results are returned as JSON to the client.
