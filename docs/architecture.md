# Cyprus System Architecture

Cyprus is designed as a modular system for evaluating AI models against symbolic policy rules. It follows a clear data flow where model information is centralized, loaded into a reasoning engine, and evaluated against policies written in Prolog.

This architecture separates the data (the *what*) from the logic (the *how*), making the system transparent, auditable, and easy to extend.

## Architectural Diagram

```
+--------------------------------+      +--------------------------------+
|   External Sources (e.g. HF)   |      |   Internal Sources (e.g. MD)   |
+--------------------------------+      +--------------------------------+
              |                                      |
              v                                      v
+-------------------------------------------------------------------------+
| 1. Data Pipeline (`cyprus/data/scrapers/`, `cyprus/data/processors/`)    |
|   - Scrapes raw model data.                                             |
|   - Processes and enriches it (e.g., estimates risk, compute).          |
+-------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------+
| 2. Model Registry (`data/models/registry.json`)                         |
|   - Central JSON file storing all model facts.                          |
|   - The single source of truth for the reasoning engine.                |
+-------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------+
| 3. Reasoning Engine (`cyprus/core/`)                                    |
|   - `ModelRegistry`: Loads `registry.json` into Prolog facts.           |
|   - `PrologEngine`: Wraps SWI-Prolog to run queries.                    |
|   - `PolicyEngine`: High-level API for compliance checks.               |
+-------------------------------------------------------------------------+
              |                                      ^
              v                                      |
+--------------------------------+      +--------------------------------+
| 4. API Layer (`cyprus/api/`)     |      | 5. Policies (`cyprus/policies/`) |
|   - Exposes the engine via REST. |      |   - Prolog rules for compliance. |
|   - Endpoints for queries.       |----->|   - e.g., `eu_ai_act.pl`       |
+--------------------------------+      +--------------------------------+

```

## Core Components

### 1. Data Pipeline

This layer is responsible for populating the Model Registry.
*   **Scrapers (`cyprus/data/scrapers/`):** Python scripts that fetch model metadata from external sources like the Hugging Face Hub or internal sources like Markdown model cards.
*   **Processors (`cyprus/data/processors/`):** Scripts that enrich the raw data with derived attributes. For example, `compute_estimator.py` uses heuristics to estimate training FLOPs, and `risk_scorer.py` assigns a risk score based on a weighted rubric.

### 2. Model Registry

The **`data/models/registry.json`** file is the central database for the system. It is a simple JSON array of model objects, where each object contains a comprehensive set of facts, including:
*   Core identifiers (`model_id`, `organization`).
*   Technical specifications (`compute_flops`, `capabilities`).
*   Governance attributes (`risk_score`, `red_teaming_status`, `risk_category`).
*   Detailed governance evidence (`training_data`, `bias_assessment`, etc.).

This file is the single source of truth that the reasoning engine consumes.

### 3. Reasoning Engine

This is the heart of Cyprus, composed of three key Python classes in `cyprus/core/`:
*   **`PrologEngine`:** A low-level wrapper around the `pyswip` library. It provides the fundamental capabilities to load Prolog files (`.pl`), assert facts into the knowledge base, and execute queries.
*   **`ModelRegistry`:** This class is responsible for bridging the gap between the JSON registry and the Prolog engine. It reads `registry.json`, sanitizes the data into valid Prolog terms (e.g., converting Python strings to quoted atoms), and asserts them as `model/10` and other facts into the Prolog knowledge base.
*   **`PolicyEngine`:** This is the primary high-level interface for the system. It orchestrates the loading of policies and data, and it exposes simple, business-friendly methods like `get_deployable_models()` or `get_governance_report()`, hiding the complexity of the underlying Prolog queries.

### 4. API Layer

The `cyprus/api/` directory contains a **FastAPI** application that exposes the `PolicyEngine`'s functionality through a REST API. This allows for easy integration with other systems, such as CI/CD pipelines, internal dashboards, or other automated workflows. The API provides endpoints for listing models by compliance status, checking individual models, and retrieving full governance reports.

### 5. Policies

The **`cyprus/policies/`** directory contains the logic of the compliance framework, written as Prolog rule files (`.pl`). These files define the conditions under which a model is considered, for example, "prohibited," "high-risk," or "deployable." Because the rules are decoupled from the application code, they can be easily modified, audited, and extended without changing the core Python application.