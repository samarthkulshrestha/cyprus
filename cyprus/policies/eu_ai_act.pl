% --- EU AI Act - Comprehensive Rule Set ---
% Based on the specification from data/policies/eu_ai_act_fragments.json

:- dynamic model/10.

% --- Article 5: Prohibited AI Practices (Unacceptable Risk) ---
% A model is prohibited if its use case falls into one of the banned categories.
prohibited_deployment(Model) :-
    model(Model, _, _, _, _, _, _, _, _, use_case('social_scoring')).

prohibited_deployment(Model) :-
    model(Model, _, _, _, _, _, _, _, _, use_case('cognitive_manipulation')).

prohibited_deployment(Model) :-
    model(Model, _, _, _, _, _, _, _, _, use_case('biometric_surveillance')).

% --- Article 51: Systemic Risk Models ---
is_systemic_risk(Model) :-
    model(Model, _, compute(C), _, _, _, _, _, _, _),
    C > 1e25.

% --- Article 6: High-Risk AI Systems ---
requires_high_risk_compliance(Model) :-
    model(Model, _, _, _, _, _, _, _, risk_category('high_risk'), _).

% --- Article 52: Transparency Obligations ---
requires_transparency_disclosure(Model) :-
    model(Model, _, _, _, _, _, capabilities(Caps), _, _, _),
    member('chat', Caps).

% --- Deployment Readiness ---

% A model can be deployed if it is not prohibited AND it is not high-risk.
can_deploy(Model) :-
    model(Model, _, _, _, _, _, _, _, _, _), % First, bind Model to an existing model.
    \+ prohibited_deployment(Model),
    \+ requires_high_risk_compliance(Model).

% A model can ALSO be deployed if it is not prohibited, IS high-risk, but has completed red teaming.
can_deploy(Model) :-
    model(Model, _, _, _, _, _, _, red_teaming_status('completed'), _, _), % Bind Model to a red-teamed model.
    \+ prohibited_deployment(Model),
    requires_high_risk_compliance(Model).
