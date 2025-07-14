% --- Comprehensive AI Governance Rules ---

:- dynamic training_data/5.
:- dynamic bias_assessment/5.
:- dynamic performance_metrics/6.
:- dynamic security_measures/4.

% Rule: Flag models with low-quality training data.
low_quality_data(Model) :-
    training_data(Model, _, _, _, QualityScore),
    QualityScore < 0.85.

% Rule: Flag models where bias mitigation is incomplete.
incomplete_bias_mitigation(Model) :-
    bias_assessment(Model, _, _, _, MitigationStatus),
    MitigationStatus \= 'completed'.

% Rule: Identify models that are "underperforming" based on F1 score.
is_underperforming(Model) :-
    performance_metrics(Model, _, _, _, F1Score, _),
    F1Score < 0.9.

% Rule: Check for models lacking basic security measures.
inadequate_security(Model) :-
    security_measures(Model, _, _, AccessControls),
    AccessControls \= 'rbac'. % Role-Based Access Control is required.

% Rule: A model is "not_production_ready" if it has any of these issues.
not_production_ready(Model) :- low_quality_data(Model).
not_production_ready(Model) :- incomplete_bias_mitigation(Model).
not_production_ready(Model) :- is_underperforming(Model).
not_production_ready(Model) :- inadequate_security(Model).
