# Policy Encoding in Prolog

The power of Cyprus comes from its use of Prolog to define flexible and symbolic rules for AI policy compliance. This guide explains how to write the facts and rules that the reasoning engine uses.

All policy logic is stored in `.pl` files within the `cyprus/policies/` directory.

---

## Declaring Dynamic Facts

Because model data is loaded dynamically at runtime from the `registry.json` file, any fact that is generated from this data must be declared as **`dynamic`** at the top of your rule file. This tells the Prolog engine that the definitions for these facts can change.

```prolog
:- dynamic model/10.
:- dynamic training_data/5.
:- dynamic bias_assessment/5.
:- dynamic performance_metrics/6.
:- dynamic security_measures/4.
```

---

## Core Data Structures (Facts)

The engine relies on a set of predefined "facts" to represent the state of the world. These are asserted into the Prolog database from the `registry.json` file.

### `model/10`

This is the primary fact structure for describing an AI model.

*   **Format:** `model(ModelID, Org, Compute, RiskScore, DeploymentRegions, Alignment, Capabilities, RedTeamingStatus, RiskCategory, UseCase).`

*   **Arguments:**
    1.  `ModelID`: An atom for the model's unique ID (e.g., `gpt4_turbo`).
    2.  `Org`: A compound term for the organization (e.g., `org('openai')`).
    3.  `Compute`: A compound term for training compute in FLOPs (e.g., `compute(2.8e25)`).
    4.  `RiskScore`: A compound term for the calculated risk score (e.g., `risk_score(0.82)`).
    5.  `DeploymentRegions`: A Prolog list of region atoms (e.g., `['us', 'eu']`).
    6.  `Alignment`: A Prolog list of alignment method atoms (e.g., `['rlhf']`).
    7.  `Capabilities`: A Prolog list of capability atoms (e.g., `['text_generation', 'chat']`).
    8.  `RedTeamingStatus`: The status of red teaming (e.g., `red_teaming_status('completed')`).
    9.  `RiskCategory`: The assigned risk category (e.g., `risk_category('high_risk')`).
    10. `UseCase`: The intended use case atom (e.g., `use_case('general_purpose')`).

### Governance Facts

Detailed governance findings are stored in separate facts, linked by `ModelID`.

*   `training_data(ModelID, Source, Size, DateRange, QualityScore).`
*   `bias_assessment(ModelID, TestDate, BiasMetrics, AffectedGroups, MitigationStatus).`
*   `performance_metrics(ModelID, Accuracy, Precision, Recall, F1Score, EvaluationDate).`
*   `security_measures(ModelID, EncryptionAtRest, EncryptionInTransit, AccessControls).`

---

## Writing Compliance Rules

Rules are standard Prolog clauses that infer new knowledge. They are the core of the policy engine.

### Important: Quoting Strings

The Python `ModelRegistry` loader automatically converts JSON string values into **quoted Prolog atoms**. When writing rules, you must match against these quoted atoms.

*   **Correct:** `red_teaming_status('completed')`
*   **Incorrect:** `red_teaming_status(completed)`

### Example 1: A Simple Rule

This rule identifies models that are subject to high-risk compliance requirements based on their `risk_category`.

```prolog
% A model requires high-risk compliance if its category is 'high_risk'.
requires_high_risk_compliance(Model) :-
    model(Model, _, _, _, _, _, _, _, risk_category('high_risk'), _).
```

### Example 2: A Multi-Condition Rule

This rule defines a "systemic risk" model based on its training compute, as per the EU AI Act.

```prolog
% A model is a systemic risk if its training compute exceeds 10^25 FLOPs.
is_systemic_risk(Model) :-
    model(Model, _, compute(C), _, _, _, _, _, _, _), % Deconstruct the model fact to get C
    C > 1e25.                                        % Apply the condition
```

### Example 3: Rules with Multiple Clauses

A predicate can be defined by multiple rules. A query will succeed if *any* of the clauses are true. This is perfect for defining complex concepts like "deployability."

```prolog
% Rule 1: A model can be deployed if it's not prohibited and not high-risk.
can_deploy(Model) :-
    model(Model, _, _, _, _, _, _, _, _, _), % 1. Get a model from the knowledge base.
    \+ prohibited_deployment(Model),         % 2. Check if it is NOT prohibited.
    \+ requires_high_risk_compliance(Model). % 3. Check if it does NOT require compliance.

% Rule 2: A high-risk model can ALSO be deployed if it has completed red teaming.
can_deploy(Model) :-
    model(Model, _, _, _, _, _, _, red_teaming_status('completed'), _, _),
    requires_high_risk_compliance(Model),   % It IS high-risk...
    \+ prohibited_deployment(Model).        % ...but it is not prohibited.
```

**Note on Negation (`\+`):** Always ensure the variables in a negated goal (like `\+ prohibited_deployment(Model)`) are "instantiated" (i.e., have a value) before the negation is called. This is why we first call `model(Model, ...)` to bind `Model` to an actual model from the database.