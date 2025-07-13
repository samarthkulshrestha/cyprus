% --- EU AI Act Policy Rules (Illustrative) ---

:- dynamic model/4.
:- dynamic red_teamed/1.

% --- Version-Specific Logic ---

% For v1, the threshold is simple.
applies_restriction(v1, C, R) :- C > 1e25, R > 0.7.

% For v2, the compute threshold is lower.
applies_restriction(v2, C, R) :- C > 5e24, R > 0.7.

% --- Core Rules ---

% Default rule: uses the latest policy version (v2).
restricted(Model) :-
    restricted(Model, v2).

% Versioned rule for 'restricted'
restricted(Model, PolicyVersion) :-
    model(Model, _, compute(C), risk_score(R, _)),
    applies_restriction(PolicyVersion, C, R).

% Rule: A model is "potentially restricted" if it meets the criteria,
% factoring in the confidence of the risk score. Uses latest policy version.
potentially_restricted(Model, Confidence) :-
    model(Model, _, compute(C), risk_score(R, confidence(Conf))),
    applies_restriction(v2, C, R), % Hardcoded to latest version for this example
    Confidence is Conf * 0.9. % Policy uncertainty reduces confidence

% Rule: A model can be deployed if its risk score is 0.5 or less.
can_deploy(Model) :-
    model(Model, _, _, risk_score(R, _)),
    R =< 0.5.

% Rule: A model with a risk score over 0.5 can only be deployed
% if it has been explicitly verified through red teaming.
can_deploy(Model) :-
    model(Model, _, _, risk_score(R, _)),
    R > 0.5,
    red_teamed(Model).
