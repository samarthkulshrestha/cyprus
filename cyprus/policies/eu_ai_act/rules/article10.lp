% ============================================================================
% EU AI Act — Article 10: Data and Data Governance
% Regulation (EU) 2024/1689, Article 10(1)-(2)
% ============================================================================
%
% TRACEABILITY:
%   art10_1  → Article 10(1): Training data shall be subject to governance practices
%   art10_2a → Article 10(2)(a): Design choices for training data
%   art10_2b → Article 10(2)(b): Data collection processes
%   art10_2f → Article 10(2)(f): Examination for possible biases
% ============================================================================

% Article 10(1): Data governance required for high-risk models
unmet_requirement(M, "Data governance: training data quality below threshold (Article 10(1))") :-
    requires_high_risk_compliance(M, _),
    model_governance(M, training_data_quality, Q),
    Q < 85.

% Article 10(2)(a): Design choices — documentation must be complete
unmet_requirement(M, "Data governance: training data documentation incomplete (Article 10(2)(a))") :-
    requires_high_risk_compliance(M, _),
    model_governance(M, training_documentation_status, "incomplete").

% Article 10(2)(b): Data collection — source must be documented
unmet_requirement(M, "Data governance: training data source undocumented (Article 10(2)(b))") :-
    requires_high_risk_compliance(M, _),
    model_governance(M, training_data_source, "undocumented").

% Article 10(2)(f): Bias examination
unmet_requirement(M, "Data governance: bias examination not completed (Article 10(2)(f))") :-
    requires_high_risk_compliance(M, _),
    model_governance(M, bias_status, "not_started").

#show unmet_requirement/2.
