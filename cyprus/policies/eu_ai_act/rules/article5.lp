% ============================================================================
% EU AI Act — Article 5: Prohibited Artificial Intelligence Practices
% Regulation (EU) 2024/1689, Article 5(1)
% ============================================================================
%
% Encodes three prohibited use cases from Article 5(1).
% Each rule produces a prohibited/3 atom with:
%   - Model ID
%   - Article/clause reference
%   - Human-readable reason string
%
% TRACEABILITY:
%   art5_1a → Article 5(1)(a): Social scoring by public authorities
%   art5_1b → Article 5(1)(b): Exploitation of vulnerabilities / cognitive manipulation
%   art5_1c → Article 5(1)(c): Real-time remote biometric identification
%
% NOT YET ENCODED:
%   art5_1d — Untargeted scraping of facial images
%   art5_1e — Emotion recognition in workplace/education
%   art5_1f — Biometric categorization (race, political opinions, etc.)
%   art5_1g — Predictive policing (individual level)
%   art5_1h — Predictive policing (profiling)
% ============================================================================

% Article 5(1)(a): Social scoring systems
prohibited(M, art5_1a, "Prohibited: social scoring system (Article 5(1)(a))") :-
    model(M),
    model_attr(M, use_case, social_scoring).

% Article 5(1)(b): Exploitation of vulnerabilities
prohibited(M, art5_1b, "Prohibited: cognitive manipulation (Article 5(1)(b))") :-
    model(M),
    model_attr(M, use_case, cognitive_manipulation).

% Article 5(1)(c): Real-time remote biometric identification
prohibited(M, art5_1c, "Prohibited: biometric surveillance (Article 5(1)(c))") :-
    model(M),
    model_attr(M, use_case, biometric_surveillance).

% Show directive: include prohibited atoms in answer set
#show prohibited/3.
