# Cyprus v2

Symbolic reasoning engine for automated AI regulatory compliance using Answer Set Programming (ASP).

Cyprus encodes EU AI Act compliance rules as formal logic (via the [Clingo](https://potassco.org/clingo/) solver), evaluates AI model metadata against them, and produces compliance assessments with clause-level traceability to the legal text.

## What it does

Given AI model metadata (use case, compute, risk category, governance data, etc.), Cyprus determines:

- Which models are prohibited under Article 5 (social scoring, cognitive manipulation, biometric surveillance)
- Which models require high-risk compliance under Article 6 (healthcare, law enforcement, critical infrastructure, etc.)
- Which models pose systemic risk under Article 51 (compute threshold, capability breadth)
- Which models have unmet requirements under Articles 9, 10, 13 (risk management, data governance, transparency)
- Which models can deploy (no prohibitions, all requirements satisfied)

## Installation

Requires Python 3.11+ and a working Clingo installation.

```bash
# Clone
git clone https://github.com/samarthkulshrestha/cyprus.git
cd cyprus

# Install with uv
uv venv && uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

For evaluation benchmarks (accuracy, scalability, inter-annotator agreement):

```bash
uv pip install -e ".[eval]"
```

## Quickstart

### Check compliance

```bash
# Single file
cyprus check models.yaml

# Directory of model files
cyprus check data/real_models/

# Single model, verbose output
cyprus check models.yaml --model meta_llama3_8b --verbose

# JSON output for pipelines
cyprus check models.yaml --output json
```

### Generate a compliance report

```bash
cyprus report models.yaml --output markdown
cyprus report models.yaml --traceability --output markdown > report.md
```

### Validate model data

```bash
cyprus validate data/real_models/
```

### Manage policy modules

```bash
cyprus policy list
cyprus policy validate eu_ai_act
cyprus policy init my_new_regulation
```

## Model data format

Models are defined in YAML (or JSON). Example:

```yaml
model_id: meta_llama3_8b
organization: Meta
compute_flops: 1.8e23
risk_score: 0.35
risk_category: limited_risk
use_case: general_purpose
red_teaming_status: completed
deployment_regions: [eu, us]
capabilities: [chat, code_generation]
governance:
  training_data:
    source: publicly_available
    quality_score: 0.91
    size_tokens: 15e12
    documentation_status: complete
  bias_assessment:
    methodology: red_teaming
    status: completed
    score: 0.88
  performance:
    f1_score: 0.93
    benchmark: mmlu
    task: general
  security:
    access_control: rbac
    audit_logging: true
```

Multiple models can be provided as a YAML list or in a `models:` wrapper.

## Architecture

```
CLI (click)
  │
  ▼
Policy Engine (Python)
  │  Model ingestion & validation (Pydantic)
  │  ASP fact compilation
  │  Result interpretation & reporting
  │
  ▼
ASP Reasoning Core (Clingo)
   Model facts + policy rules → answer sets
```

Clingo only does the reasoning: it gets ground facts and rules and returns answer sets. Validation, the CLI, reporting and evaluation are all in Python.

Each regulation lives in its own directory under `cyprus/policies/` with its ASP rules, a manifest, a traceability mapping and tests. Adding a regulation means adding a directory; the core engine doesn't change.

Model data is compiled to facts of the form `model_attr(model_id, attribute, value).`, so adding a new attribute doesn't break existing rules.

## EU AI Act coverage

| Article | Title | Clauses encoded |
|---------|-------|-----------------|
| Art. 5 | Prohibited AI Practices | 3/8 |
| Art. 6 | High-Risk Classification | 2/3 |
| Art. 9 | Risk Management System | 3/12 |
| Art. 10 | Data and Data Governance | 4/11 |
| Art. 13 | Transparency | 1/4 |
| Art. 51 | Systemic Risk (GPAI) | 2/3 |
| Art. 52 | GPAI Obligations | 1/3 |

Generate the full traceability matrix:

```bash
cyprus report models.yaml --traceability
```

## Evaluation

There are also commands for evaluating the engine:

```bash
# Accuracy against ground truth (with heuristic + keyword baselines)
cyprus evaluate accuracy ground_truth.yaml data/real_models/

# Scalability benchmarks
cyprus evaluate scalability data/synthetic_models/ --sizes 10,50,100,500,1000

# Inter-annotator agreement
cyprus evaluate agreement data/ground_truth/annotations/
```

### Generating synthetic models

```bash
python data/synthetic_models/generate.py
```

Produces 1000 deterministic synthetic models from configurable distributions for scalability testing.

## Development

```bash
# Run tests
pytest -v

# Lint
ruff check cyprus/ tests/

# Type check
mypy cyprus/
```

## Project structure

```
cyprus/
├── engine/          # Clingo solver wrapper, result types
├── registry/        # Pydantic schema, YAML loader, ASP fact compiler
├── policies/        # Policy modules (eu_ai_act, _template)
├── reporting/       # Compliance reports, traceability matrix, formatters
├── evaluation/      # Accuracy, scalability, agreement benchmarks
├── data/scrapers/   # HuggingFace model card scraper
└── cli.py           # Click CLI
```

## License

MIT
