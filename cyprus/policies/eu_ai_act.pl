% --- EU AI Act Policy Rules (Illustrative) ---

:- dynamic model/4.
:- dynamic red_teamed/1.

% Rule: A model is considered "restricted" if its compute is over 1e25 FLOPs
% and its risk score is greater than 0.7.
% We ignore confidence here for a hard threshold.
restricted(Model) :-
    model(Model, _, compute(C), risk_score(R, _)),
    C > 1e25,
    R > 0.7.

% Rule: A model is "potentially restricted" if it meets the criteria,
% factoring in the confidence of the risk score.
potentially_restricted(Model, Confidence) :-
    model(Model, _, compute(C), risk_score(R, confidence(Conf))),
    C > 1e25,
    R > 0.7,
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
