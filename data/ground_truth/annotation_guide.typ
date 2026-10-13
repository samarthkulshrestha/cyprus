#set page(margin: 2.5cm)
#set text(size: 10pt)

= Annotation Guide — EU AI Act Compliance Labeling

== Overview

You will be given YAML files describing AI models. Each file contains metadata about one model: its use case, risk category, compute scale, capabilities, and governance data (training data quality, bias assessment status, documentation completeness, etc.).

Your task is to label each model on four binary predicates. You do not need any legal expertise --- all decisions are mechanical applications of the rules below.

== Ground Rules

+ Judge based *only* on the metadata in the YAML file.
+ Do *not* research the model externally or use prior knowledge about it.
+ Do *not* look at other annotators' labels.
+ Apply the rules below *exactly as written* --- even if the result seems wrong.
+ If you are genuinely unsure, mark confidence as "low" and explain in the notes field.
+ Record how long the full annotation takes (for the paper).

== Labels

You must assign four labels per model. Evaluate them *in the order listed*, because later labels depend on earlier ones.

=== Label 1: `prohibited` (yes / no)

Check the `use_case` field. The model is *prohibited* if and only if `use_case` is one of:

#table(
  columns: (1fr, 2fr),
  align: (left, left),
  table.header([*`use_case` value*], [*Reason*]),
  [`social_scoring`], [Article 5(1)(a): social scoring systems],
  [`cognitive_manipulation`], [Article 5(1)(b): exploitation of vulnerabilities],
  [`biometric_surveillance`], [Article 5(1)(c): real-time biometric identification],
)

If `use_case` is anything else, then *prohibited = no*.

=== Label 2: `high_risk` (yes / no)

The model is *high_risk* if *either* of these conditions is true:

+ The `risk_category` field is `high_risk`, *or*
+ The `use_case` field is one of: `healthcare`, `law_enforcement`, `critical_infrastructure`, `employment`, `education`.

If neither condition is met, then *high_risk = no*.

_Note: a model can be both prohibited and high_risk (e.g., `use_case = biometric_surveillance` with `risk_category = high_risk`). Label both independently._

=== Label 3: `systemic_risk` (yes / no)

The model has *systemic risk* if *either* of these conditions is true:

+ `compute_flops` > 10#super[25] (i.e., strictly greater than `1.0e+25`), *or*
+ The `capabilities` list has *5 or more* entries.

If neither condition is met, then *systemic_risk = no*.

_Tip: count the items under `capabilities:` in the YAML. For compute, look for numbers like `1.0e+26` (which is 10#super[26], greater than 10#super[25]) vs. `1.0e+19` (which is 10#super[19], far below the threshold)._

=== Label 4: `can_deploy` (yes / no)

This is the most complex label. Follow this decision tree in order:

*Step 1:* If `prohibited = yes` then *can_deploy = no*. Stop here.

*Step 2:* If `high_risk = no` then *can_deploy = yes*. Stop here.

*Step 3:* If `high_risk = yes`, check all of the following requirements. If *any* requirement fails, `can_deploy = no`.

#table(
  columns: (auto, 1.5fr, 2fr, 1.5fr),
  align: (center, left, left, left),
  table.header([*\#*], [*Requirement*], [*Field to check*], [*Pass condition*]),
  [1], [Red teaming completed], [`red_teaming_status`], [Equals `completed`],
  [2], [Risk score not suspiciously low], [`risk_score`], [>= 0.10],
  [3], [Training data quality sufficient], [`governance.training_data.quality_score`], [>= 0.85],
  [4], [Training data documented], [`governance.training_data.documentation_status`], [Equals `complete`],
  [5], [Training data source documented], [`governance.training_data.source`], [Not `undocumented`],
  [6], [Bias assessment started], [`governance.bias_assessment.status`], [Not `not_started`],
)

If all requirements pass, then *can_deploy = yes*.

#pagebreak()

== Worked Examples

=== Example A: A high-risk model that fails deployment

```yaml
model_id: workday_hiring_ai
organization: workday
compute_flops: 1.0e+19
risk_score: 0.68
risk_category: high_risk
use_case: employment
red_teaming_status: not_started
capabilities:
- resume_screening
- candidate_ranking
governance:
  training_data:
    quality_score: 0.55
    documentation_status: incomplete
  bias_assessment:
    status: not_started
```

*Reasoning:*

+ *prohibited?* `use_case = employment` --- not in the prohibited list --- *no*
+ *high_risk?* `risk_category = high_risk` --- *yes* \
  (also, `use_case = employment` independently triggers high_risk)
+ *systemic_risk?* `compute_flops = 1.0e+19` (< 10#super[25]), 2 capabilities (< 5) --- *no*
+ *can_deploy?* Not prohibited. High-risk, so check requirements:
  - Red teaming: `not_started` --- *fail*
  - Training data quality: 0.55 < 0.85 --- *fail*
  - Documentation: `incomplete` --- *fail*
  - Bias assessment: `not_started` --- *fail*
  - Result: *can_deploy = no*

*Labels:* `prohibited=no, high_risk=yes, systemic_risk=no, can_deploy=no`

=== Example B: A high-risk model that passes deployment

```yaml
model_id: paige_ai_prostate
organization: paige_ai
compute_flops: 1.0e+19
risk_score: 0.55
risk_category: high_risk
use_case: healthcare
red_teaming_status: completed
capabilities:
- medical_imaging
- pathology
governance:
  training_data:
    source: clinical_datasets
    quality_score: 0.9
    documentation_status: complete
  bias_assessment:
    status: completed
```

*Reasoning:*

+ *prohibited?* `use_case = healthcare` --- not prohibited --- *no*
+ *high_risk?* `risk_category = high_risk` --- *yes*
+ *systemic_risk?* `1.0e+19` < 10#super[25], 2 capabilities < 5 --- *no*
+ *can_deploy?* Not prohibited. High-risk, so check requirements:
  - Red teaming: `completed` --- pass
  - Risk score: 0.55 >= 0.10 --- pass
  - Training data quality: 0.9 >= 0.85 --- pass
  - Documentation: `complete` --- pass
  - Source: `clinical_datasets` (not `undocumented`) --- pass
  - Bias assessment: `completed` (not `not_started`) --- pass
  - Result: *can_deploy = yes*

*Labels:* `prohibited=no, high_risk=yes, systemic_risk=no, can_deploy=yes`

#pagebreak()

=== Example C: A prohibited model

```yaml
model_id: clearview_ai_facial_recognition
use_case: biometric_surveillance
risk_category: unacceptable_risk
compute_flops: 1.0e+20
capabilities:
- facial_recognition
- biometric_identification
- image_search
```

*Reasoning:*

+ *prohibited?* `use_case = biometric_surveillance` --- *yes*
+ *high_risk?* `risk_category = unacceptable_risk` (not `high_risk`), and `biometric_surveillance` is not in the high-risk use case list --- *no*
+ *systemic_risk?* `1.0e+20` < 10#super[25], 3 capabilities < 5 --- *no*
+ *can_deploy?* `prohibited = yes` --- *no* (stop immediately)

*Labels:* `prohibited=yes, high_risk=no, systemic_risk=no, can_deploy=no`

=== Example D: A minimal-risk model (simple case)

```yaml
model_id: google_bert_bert_base_uncased
risk_category: minimal_risk
use_case: general_purpose
compute_flops: 1.45e+18
capabilities:
- general
```

*Reasoning:*

+ *prohibited?* `use_case = general_purpose` --- *no*
+ *high_risk?* `risk_category = minimal_risk`, `use_case = general_purpose` --- *no*
+ *systemic_risk?* `1.45e+18` < 10#super[25], 1 capability < 5 --- *no*
+ *can_deploy?* Not prohibited, not high-risk --- *yes* (no further checks needed)

*Labels:* `prohibited=no, high_risk=no, systemic_risk=no, can_deploy=yes`

#pagebreak()

== Decision Flowchart

#let yes_color = rgb("#2d7d46")
#let no_color = rgb("#444444")

#align(center)[
  #block(width: 85%)[
    #set text(size: 9pt)
    #table(
      columns: (auto, 1fr),
      align: (center, left),
      stroke: none,
      table.header([*Step*], [*Decision*]),
      table.hline(),
      [1], [Is `use_case` in \{`social_scoring`, `cognitive_manipulation`, `biometric_surveillance`\}? \
            #text(fill: yes_color)[Yes] → `prohibited = yes` #h(2em) #text(fill: no_color)[No] → `prohibited = no`],
      table.hline(stroke: 0.5pt + luma(200)),
      [2], [Is `risk_category = high_risk`, or `use_case` in \{`healthcare`, `law_enforcement`, `critical_infrastructure`, `employment`, `education`\}? \
            #text(fill: yes_color)[Yes] → `high_risk = yes` #h(2em) #text(fill: no_color)[No] → `high_risk = no`],
      table.hline(stroke: 0.5pt + luma(200)),
      [3], [Is `compute_flops` > `1.0e+25`, or `len(capabilities)` >= 5? \
            #text(fill: yes_color)[Yes] → `systemic_risk = yes` #h(2em) #text(fill: no_color)[No] → `systemic_risk = no`],
      table.hline(stroke: 0.5pt + luma(200)),
      [4], [`can_deploy`: \
            If `prohibited = yes` → *no* \
            Else if `high_risk = no` → *yes* \
            Else if `high_risk = yes` → check all 6 requirements (see table above) \
            #h(2em) All pass → *yes* #h(2em) Any fail → *no*],
    )
  ]
]

== Annotation Template

For each model, record your labels in this format:

```yaml
model_id_here:
  prohibited: false
  high_risk: false
  systemic_risk: false
  can_deploy: true
  confidence: high       # high, medium, or low
  notes: ""              # explain any uncertainty
```

== Common Pitfalls

+ *Don't confuse `risk_category` with `use_case`.* A model with `risk_category: unacceptable_risk` is not automatically prohibited --- only the three specific `use_case` values trigger prohibition.

+ *`can_deploy` requirements only apply to high-risk models.* If a model is not high-risk (and not prohibited), it can deploy regardless of governance data quality.

+ *Count capabilities carefully.* The YAML list may have varying indentation. Count the actual `- item` entries under `capabilities:`.

+ *Scientific notation.* `1.0e+25` = 10#super[25] exactly. This is *not* greater than 10#super[25]. The threshold is strictly greater than, so `1.0e+25` → `systemic_risk = no`. But `1.1e+25` → `systemic_risk = yes`.
