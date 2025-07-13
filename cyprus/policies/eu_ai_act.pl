% --- EU AI Act Policy Rules (Illustrative) ---

:- dynamic model/4.
:- dynamic red_teamed/1.

% --- Interpretation-Specific Logic ---
% For v1, the risk threshold changes based on interpretation.
applies_restriction(v1, C, R, conservative) :- C > 1e25, R > 0.6.
applies_restriction(v1, C, R, industry_standard) :- C > 1e25, R > 0.7.
applies_restriction(v1, C, R, liberal) :- C > 1e25, R > 0.8.

% For v2, the compute threshold changes based on interpretation.
applies_restriction(v2, C, R, conservative) :- C > 1e24, R > 0.7.
applies_restriction(v2, C, R, industry_standard) :- C > 5e24, R > 0.7.
applies_restriction(v2, C, R, liberal) :- C > 8e24, R > 0.7.


% --- Core Rules ---

% Default rule: uses latest version and industry_standard interpretation
restricted(Model) :-
    restricted(Model, v2, industry_standard).

% Versioned rule: uses industry_standard interpretation
restricted(Model, PolicyVersion) :-
    restricted(Model, PolicyVersion, industry_standard).

% Fully specified rule for 'restricted'
restricted(Model, PolicyVersion, Interpretation) :-
    model(Model, _, compute(C), risk_score(R, _)),
    applies_restriction(PolicyVersion, C, R, Interpretation).

% Rule: A model is "potentially restricted" if it meets the criteria,
% factoring in the confidence of the risk score.
% Uses latest version and industry standard for this example.
potentially_restricted(Model, Confidence) :-
    model(Model, _, compute(C), risk_score(R, confidence(Conf))),
    applies_restriction(v2, C, R, industry_standard),
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
