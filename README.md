# Cyprus: An AI Policy Compliance Engine

Cyprus is a symbolic reasoning engine designed to help organizations govern their AI models by checking them against a set of clear, auditable, and extensible policy rules. It translates complex regulatory frameworks, like the EU AI Act, and internal governance standards into machine-readable logic.

This allows you to automatically classify models, identify risks, and determine deployment readiness across your entire AI inventory.

## Key Features

*   **Symbolic Policy Rules:** Define compliance using the power and expressiveness of Prolog.
*   **Central Model Registry:** Maintain a single source of truth for all your AI models and their metadata.
*   **Automated Compliance Checks:** Run checks via a simple command-line script to get a full report.
*   **REST API:** Integrate Cyprus with your existing MLOps pipelines, dashboards, and tools.
*   **Extensible:** Easily add new policy rules, data sources, and governance checks.

---

## Getting Started

Follow these steps to get Cyprus up and running on your local machine.

### Prerequisites

*   Python 3.9+
*   [Pipenv](https://pipenv.pypa.io/en/latest/) for managing dependencies.
*   SWI-Prolog: The core reasoning engine.
    *   **Ubuntu/Debian:** `sudo apt-get install swi-prolog`
    *   **macOS (Homebrew):** `brew install swi-prolog`

### 1. Installation

Clone the repository and install the required Python packages using Pipenv.

```bash
git clone <repository-url>
cd cyprus
pipenv install
pipenv shell
```

### 2. Run a Compliance Check

You can immediately run a compliance check on the example models included in the registry. This script will load all policies and evaluate all models.

```bash
python3 scripts/run_compliance_check.py
```

You should see a report that looks like this:

```
--- Compliance & Governance Report ---

Total Models: 3
['customer_chatbot_v3', 'gpt4_turbo', 'social_scorer_v1']

Prohibited by EU AI Act (1):
['social_scorer_v1']

Deployable by EU AI Act (2):
['customer_chatbot_v3', 'gpt4_turbo']

Flagged as 'Not Production Ready' (1):
['gpt4_turbo']

--- End of Report ---
```

### 3. Run the API Server

To interact with Cyprus programmatically, start the FastAPI server.

```bash
uvicorn cyprus.api.server:app --host 0.0.0.0 --port 8000
```

The API is now available at `http://localhost:8000`. You can explore the interactive Swagger UI documentation at `http://localhost:8000/docs`.

---

## How It Works

Cyprus is built on a simple but powerful architecture:

1.  **Model Registry (`data/models/registry.json`):** This JSON file is the heart of the system, acting as a database of "facts" about your AI models. It stores everything from the model's name and compute requirements to detailed governance information like bias assessments and security measures.

2.  **Policy Rules (`cyprus/policies/`):** These are Prolog (`.pl`) files that define the logic for your compliance checks. For example, a rule might state that a model is "high-risk" if it's used in a specific context, or "prohibited" if it performs social scoring.

3.  **Reasoning Engine (`cyprus/core/`):** A Python wrapper around a Prolog engine that loads the model data from the registry as facts and then applies the policy rules to them. It answers questions like, "Which models are deployable?" or "Is `gpt4_turbo` considered a systemic risk?"

4.  **Tools & API (`scripts/`, `cyprus/api/`):** A set of command-line scripts and a REST API provide easy ways to interact with the engine, whether you're running a manual check or integrating Cyprus into an automated workflow.

## Extending Cyprus

Cyprus is designed to be easily extended.

### Adding a New Model

You can add a new model to the system by:
1.  **Scraping it:** Use the `scrape_models.py` script to fetch data from a source like Hugging Face.
    ```bash
    python3 scripts/scrape_models.py "meta-llama/Meta-Llama-3-8B"
    ```
2.  **Manually adding it:** Add a new JSON object to the `data/models/registry.json` file, following the existing structure.

### Writing a New Policy

To add a new governance check, you can create a new rule in one of the existing `.pl` files or add a new policy file altogether. For example, to flag any model that hasn't been red-teamed, you could add this rule to `governance_rules.pl`:

```prolog
% Flag models that have not completed red teaming.
requires_red_teaming(Model) :-
    model(Model, _, _, _, _, _, _, red_teaming_status(Status), _, _),
    Status \= 'completed'.
```

For more details on the architecture and how to write policies, see the documentation in the `/docs` directory.