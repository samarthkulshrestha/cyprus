% ============================================================================
% EU AI Act — Article 6: Classification Rules for High-Risk AI Systems
% Regulation (EU) 2024/1689, Article 6(1)-(2)
% ============================================================================
%
% TRACEABILITY:
%   art6_1 → Article 6(1): Systems listed in Annex III are high-risk
%   art6_2 → Article 6(2): Exception — not high-risk if no significant risk
% ============================================================================

% Article 6(1): High-risk classification by risk category
requires_high_risk_compliance(M, art6_1) :-
    model(M),
    model_attr(M, risk_category, high_risk).

% Article 6(2): High-risk by use case domain
requires_high_risk_compliance(M, art6_2) :-
    model(M),
    model_attr(M, use_case, healthcare).

requires_high_risk_compliance(M, art6_2) :-
    model(M),
    model_attr(M, use_case, law_enforcement).

requires_high_risk_compliance(M, art6_2) :-
    model(M),
    model_attr(M, use_case, critical_infrastructure).

requires_high_risk_compliance(M, art6_2) :-
    model(M),
    model_attr(M, use_case, employment).

requires_high_risk_compliance(M, art6_2) :-
    model(M),
    model_attr(M, use_case, education).

#show requires_high_risk_compliance/2.
