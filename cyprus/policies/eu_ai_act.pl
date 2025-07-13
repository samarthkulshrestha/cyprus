% --- EU AI Act Policy Rules (Illustrative) ---
% These rules are simplified and focus on the new model/8 structure.

:- dynamic model/8.
:- dynamic red_teamed/1.

% --- Core EU AI Act Rules ---

% Rule: A model is considered "high_risk" if its capabilities include
% critical applications (e.g., reasoning) and it is deployed in the EU.
is_high_risk(Model) :-
    model(Model, _, _, _, deployment_region(Regions), _, capabilities(Caps), _),
    member(eu, Regions),
    member(reasoning, Caps).

% Rule: A model is "restricted" if it is high_risk and its risk score is > 0.7.
restricted(Model) :-
    is_high_risk(Model),
    model(Model, _, _, risk_score(R), _, _, _, _),
    R > 0.7.

% Rule: A model can be deployed if it is not high_risk.
can_deploy(Model) :-
    model(Model, _, _, _, _, _, _, _), % First, bind Model to an existing model
    \+ is_high_risk(Model).

% Rule: A high-risk model can be deployed if it has completed red teaming.
can_deploy(Model) :-
    is_high_risk(Model),
    red_teamed(Model).