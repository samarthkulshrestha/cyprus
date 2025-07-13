# Cyprus - A Symbolic Reasoning Engine for AI Policy Compliance.

## High-level System Design:

```
+---------------------------+
|     User-defined Policy   |  (in a Prolog-friendly format)
+---------------------------+
            |
            v
+---------------------------+
|  Prolog Reasoning Engine  |  (applies rules to LLM registry)
+---------------------------+
            |
            v
+---------------------------+
|   Model / Org Registry    |  (facts: compute used, risk score, org, etc.)
+---------------------------+
            |
            v
+---------------------------+
| Python Wrapper / API      |  (for data scraping, JSON I/O, frontend bridge)
+---------------------------+
            |
            v
+---------------------------+
| Optional JS/D3 Frontend   |  (interactive reports / policy dashboard)
+---------------------------+
```

## Core Components Breakdown:

### 1. Model Registry (Facts)

Language: Prolog
Purpose: Store facts like:

```prolog
model(gpt4, org(openai), compute(1.8e25), risk_score(0.85)).
model(cloudia, org(anthropic), compute(5e24), risk_score(0.45)).
model(customllm, org(you), compute(3e24), risk_score(0.30)).
```

You can expand this with:
+ Deployment region
+ Alignment methodology
+ Capabilities
+ Red teaming status

### 2. Policy Rule Engine (Rules)

Translate EU AI Act fragments into symbolic prolog rules.
Define symbolic rules like:

```prolog
% Rule: No deployment if compute > 1e25 and risk > 0.7
restricted(Model) :-
    model(Model, _, compute(C), risk_score(R)),
    C > 1e25,
    R > 0.7.

% Rule: Only models with verified red teaming can be deployed if risk_score > 0.5
can_deploy(Model) :-
    model(Model, _, _, risk_score(R)),
    R =< 0.5.

can_deploy(Model) :-
    model(Model, _, _, risk_score(R)),
    R > 0.5,
    red_teamed(Model).
```

You’re building a symbolic interpreter for policy.

### 3. Python Wrapper / Tooling

Why? Prolog can be painful for:
+ Scraping model metadata
+ Working with APIs (e.g., HuggingFace, paperswithcode)
+ Serializing results (e.g., JSON)

Use:
+ `pyswip` or `prologpy` to run Prolog queries from Python
+ `requests`, `beautifulsoup4`, etc. to auto-populate model data
+ `matplotlib`/`plotly` if you want static charts instead of a web UI

### 4. Interactive Dashboard (Optional but Sexy)

Language: TypeScript + D3 or Observable notebooks
Functionality:
+ Slider to adjust policy thresholds (compute cap, risk)
+ Dynamic update of "Compliant vs Non-Compliant" model lists
+ Sankey flow of model → org → policy outcome
+ This could be a single-page dashboard that loads query results from Python/Prolog backend.

## Leveling Up:

+ Plug in formal ontologies (e.g., FOAF, OWL) to reason about org hierarchies.
+ Support temporal logic: policies changing over time.
+ Hook in risk prediction models using ML (for hybrid symbolic-neural combo).
+ Publish as an open-source tool or Colab demo. Call it Cyrpus.
