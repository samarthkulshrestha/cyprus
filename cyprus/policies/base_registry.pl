% --- Base Model Registry ---
% This file should be populated with facts about models.
% The core fact is `model/4`, defined as:
% model(ModelName, organization(OrgName), compute(ComputeValue), risk_score(RiskScore, confidence(Confidence))).

% Example entries:
model(gpt4, org(openai), compute(1.8e25), risk_score(0.85, confidence(0.9))).
model(cloudia, org(anthropic), compute(5e24), risk_score(0.45, confidence(0.95))).
model(customllm, org(you), compute(3e24), risk_score(0.30, confidence(0.8))).

% Additional facts can be added, for example:
% red_teamed(ModelName).
red_teamed(gpt4).
red_teamed(customllm).
