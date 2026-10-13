% ============================================================================
% EU AI Act — Article 51: Classification as GPAI with Systemic Risk
% Regulation (EU) 2024/1689, Article 51(1)-(2)
% ============================================================================
%
% TRACEABILITY:
%   art51_1 → Article 51(1): GPAI model is systemic risk if "high impact
%             capabilities" — currently defined as cumulative compute > 10^25 FLOPs
%   art51_2 → Article 51(2): Commission may designate based on other criteria
%             (modeled as: multiple high-impact capabilities)
% ============================================================================

% Article 51(1): Compute threshold — 10^25 FLOPs
% compute_flops is stored as log10(flops) * 100, so 10^25 = 2500
systemic_risk(M, art51_1) :-
    model(M),
    model_attr(M, compute_flops, C),
    C > 2500.

% Article 51(2): Multi-capability high-impact designation
systemic_risk(M, art51_2) :-
    model(M),
    #count { Cap : model_attr(M, capability, Cap) } >= 5.

#show systemic_risk/2.
