# Policy Encoding in Prolog

The power of Cyprus comes from its use of Prolog to define flexible and symbolic rules for AI policy compliance. This guide explains how to write the facts and rules that the reasoning engine uses.

## Core Data Structures (Facts)

The engine relies on a set of predefined "facts" to represent the state of the world. These facts are asserted into the Prolog database, either from a `.pl` file or dynamically from the `registry.json` via the Python wrapper.

### `model/4`

This is the primary fact structure for describing a model.

*   **Format:** `model(ModelID, Organization, Compute, RiskScore).`
*   **Arguments:**
    1.  `ModelID`: A Prolog atom representing the unique name of the model (e.g., `gpt4`).
    2.  `Organization`: A compound term `org(Name)` (e.g., `org(openai)`). If the name contains spaces, it must be quoted (e.g., `org('Cygnus Research')`).
    3.  `Compute`: A compound term `compute(Value)` where `Value` is a number representing FLOPs (e.g., `compute(1.8e25)`).
    4.  `RiskScore`: A compound term `risk_score(Value)` where `Value` is a number between 0 and 1 (e.g., `risk_score(0.85)`).

**Example:**
```prolog
model(gpt4, org(openai), compute(1.8e25), risk_score(0.85)).
```

### `red_teamed/1`

A simple fact indicating that a model has undergone and passed red teaming.

*   **Format:** `red_teamed(ModelID).`
*   **Example:**
```prolog
red_teamed(gpt4).
```

## Dynamic Predicates

Because model facts are asserted at runtime from the `registry.json` file, the predicates must be declared as `dynamic` in any rule file that uses them. This tells Prolog that the definitions of these predicates can change.

Add this to the top of your rule file:
```prolog
:- dynamic model/4.
:- dynamic red_teamed/1.
```

## Writing Compliance Rules

Rules are the core of the policy engine. They are standard Prolog clauses that conclude a new fact based on existing ones.

### Example 1: `restricted/1`

A model is "restricted" if its compute is above a certain threshold and its risk score is high.

```prolog
% A model is restricted if its compute is > 1e25 and risk > 0.7
restricted(Model) :-
    model(Model, _, compute(C), risk_score(R)), % Deconstruct the model fact
    C > 1e25,                                  % Check compute
    R > 0.7.                                   % Check risk
```

### Example 2: `can_deploy/1`

A model can be deployed if it meets one of several conditions. This is a good example of using multiple clauses to define a rule.

```prolog
% Rule 1: Any model with a low risk score can be deployed.
can_deploy(Model) :-
    model(Model, _, _, risk_score(R)),
    R =< 0.5.

% Rule 2: A model with a higher risk score can ONLY be deployed
% if it has been explicitly red teamed.
can_deploy(Model) :-
    model(Model, _, _, risk_score(R)),
    R > 0.5,
    red_teamed(Model). % This condition checks for the red_teamed/1 fact
```

By combining different facts and logical conditions (`>`, `<`, `=`, etc.), you can create complex and nuanced policies to fit any governance requirement.
