% ============================================================================
% EU AI Act — Article 9: Risk Management System
% Regulation (EU) 2024/1689, Article 9(1)-(2)
% ============================================================================
%
% TRACEABILITY:
%   art9_1  → Article 9(1): Risk management system shall be established
%   art9_2a → Article 9(2)(a): Identification of known risks
%   art9_2b → Article 9(2)(b): Risk estimation from intended/misuse
% ============================================================================

% Article 9(1): High-risk models must have risk management
unmet_requirement(M, "Risk management incomplete: red teaming not completed (Article 9(1))") :-
    requires_high_risk_compliance(M, _),
    model_attr(M, red_teaming_status, not_started).

unmet_requirement(M, "Risk management incomplete: red teaming in progress (Article 9(1))") :-
    requires_high_risk_compliance(M, _),
    model_attr(M, red_teaming_status, in_progress).

% Article 9(2)(a): Known risk identification
unmet_requirement(M, "Risk identification may be incomplete: high-risk model with low risk score (Article 9(2)(a))") :-
    requires_high_risk_compliance(M, _),
    model_attr(M, risk_score, S),
    S < 10.

% Article 9(2)(b): Risk from misuse
unmet_requirement(M, "Misuse risk evaluation incomplete: bias assessment pending (Article 9(2)(b))") :-
    requires_high_risk_compliance(M, _),
    model_governance(M, bias_status, "not_started").

#show unmet_requirement/2.
