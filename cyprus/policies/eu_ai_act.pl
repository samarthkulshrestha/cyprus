% --- EU AI Act - Comprehensive Rule Set ---
% Based on the specification from data/policies/eu_ai_act_fragments.json

:- dynamic model/10.
:- dynamic red_teamed/1.

% --- Article 5: Prohibited AI Practices ---
% AI systems for social scoring or mass surveillance are prohibited.
prohibited_deployment(Model) :-
    model(Model, _, _, _, _, _, _, _, _, use_case(social_scoring)).

prohibited_deployment(Model) :-
    model(Model, _, _, _, _, _, _, _, _, use_case(mass_surveillance)).

% --- Article 51: Systemic Risk Models ---
% Models trained with compute > 10^25 FLOPs are considered systemic risk.
is_systemic_risk(Model) :-
    model(Model, _, compute(C), _, _, _, _, _, _, _),
    C > 1e25.

% --- Article 6: High-Risk AI Systems ---
% Systems classified as 'high_risk' require comprehensive compliance measures.
requires_high_risk_compliance(Model) :-
    model(Model, _, _, _, _, _, _, _, risk_category(high_risk), _).

% --- Article 52: Transparency Obligations ---
% Systems interacting with humans must disclose their AI nature.
% We infer this from the 'chat' capability for this example.
requires_transparency_disclosure(Model) :-
    model(Model, _, _, _, _, _, capabilities(Caps), _, _, _),
    member(chat, Caps).

% --- Deployment Readiness ---

% A model can be deployed if it is not prohibited AND it is not high-risk.
can_deploy(Model) :-
    \+ prohibited_deployment(Model),
    \+ requires_high_risk_compliance(Model).

% A model can ALSO be deployed if it is not prohibited, IS high-risk, but has been red-teamed.
can_deploy(Model) :-
    \+ prohibited_deployment(Model),
    requires_high_risk_compliance(Model),
    red_teamed(Model).

