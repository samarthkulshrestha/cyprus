% ============================================================================
% EU AI Act — Aggregate Deployment Logic
% Combines all article-level assessments into deployment decisions
% ============================================================================

% Integrity constraint: prohibited models CANNOT appear as deployable
:- can_deploy(M), prohibited(M, _, _).

% A model can deploy if:
% 1. It is not prohibited
% 2. It has no unmet requirements
can_deploy(M) :-
    model(M),
    not prohibited(M, _, _),
    not has_unmet_requirement(M).

% Helper: does this model have any unmet requirement?
has_unmet_requirement(M) :-
    unmet_requirement(M, _).

#show model/1.
#show can_deploy/1.
