% ============================================================================
% EU AI Act — Article 52: Transparency Obligations for GPAI
% Regulation (EU) 2024/1689, Article 52(1)
% ============================================================================
%
% TRACEABILITY:
%   art52_1 → Article 52(1): Providers of AI systems intended to interact
%             with natural persons shall ensure the system is designed and
%             developed so that persons are informed they are interacting with AI.
% ============================================================================

% Article 52(1): Chat-capable models require transparency disclosure
requires_transparency(M, art52_1) :-
    model(M),
    model_attr(M, capability, chat).

% Content generation models also require disclosure
requires_transparency(M, art52_1) :-
    model(M),
    model_attr(M, use_case, content_generation).

#show requires_transparency/2.
