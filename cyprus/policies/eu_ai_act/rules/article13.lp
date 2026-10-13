% ============================================================================
% EU AI Act — Article 13: Transparency and Provision of Information
% Regulation (EU) 2024/1689, Article 13(1)
% ============================================================================
%
% TRACEABILITY:
%   art13_1 → Article 13(1): High-risk AI systems shall be designed and
%             developed in such a way as to ensure that their operation is
%             sufficiently transparent to enable deployers to interpret the
%             system's output and use it appropriately.
% ============================================================================

% Article 13(1): High-risk models need documentation
unmet_requirement(M, "Transparency: training documentation incomplete for high-risk model (Article 13(1))") :-
    requires_high_risk_compliance(M, _),
    model_governance(M, training_documentation_status, S),
    S != "complete".

#show unmet_requirement/2.
