% --- Base Model Registry (for testing) ---
% This file contains example facts for a comprehensive AI governance model.

% --- Core Model Facts (model/8) ---
% model(ModelID, Org, Compute, RiskScore, DeploymentRegions, Alignment, Capabilities, RedTeamingStatus).
model(gpt4_turbo, org(openai), compute(2.8e25), risk_score(0.82),
      deployment_region([us, eu, uk]),
      alignment_methodology([rlhf, 'constitutional_ai']),
      capabilities([text_generation, reasoning, coding, multimodal]),
      red_teaming_status(completed)
).

model(cloudia_v2, org(anthropic), compute(6e24), risk_score(0.75),
      deployment_region([us, ca]),
      alignment_methodology([rlhf]),
      capabilities([text_generation, reasoning]),
      red_teaming_status(completed)
).