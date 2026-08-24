---
name: problem-classifier
description: Classify each parsed mathematical-modeling subquestion by required output and structure, surface ambiguous framing trade-offs for human choice, and record primary/secondary task types without selecting algorithms.
---

# Preconditions

- `planning/parse/problem_parse.json` exists and maps every Qx to an output.
- Material framing ambiguities are visible.

Read legacy parse paths only during migration.

# Task Types

- evaluation/ranking;
- prediction/estimation;
- optimization/decision;
- mechanism/dynamics;
- classification/clustering;
- graph/routing/network;
- simulation/scenario;
- descriptive/inference;
- mixed.

Detailed cues are in `references/task-type-guide.md`.

# Workflow

1. Classify from the required output, decision structure, constraints, and relationships—not keywords alone.
2. Assign:
   - primary type;
   - optional secondary type;
   - confidence;
   - evidence from the parse;
   - consequences for validation and deliverables.
3. Identify mixed or ambiguous framings that would change what the team can claim.
4. For a load-bearing ambiguity, invoke one choice card explaining consequences. Do not silently settle it.
5. Save `planning/classification/problem_classification.json`.
6. Record the human framing decision in `methods/Qx/qx_decisions.jsonl`, or in `planning/framing_decisions.jsonl` when the Qx method directory does not yet exist.

# Output Contract

```json
{
  "schema_version": 1,
  "subquestions": [
    {
      "id": "Q1",
      "primary_type": "evaluation",
      "secondary_type": null,
      "confidence": "high",
      "evidence": [],
      "required_validation": [],
      "framing_decision_id": null,
      "risks": []
    }
  ]
}
```

# Rules

- Do not propose or choose methods.
- Do not classify only from nouns such as “forecast” or “optimal”; verify the required output.
- A subquestion may be mixed, but avoid listing many types without prioritization.
- Human framing is required when alternative classifications lead to materially different outputs or claims.
- Do not create a long taxonomy report when the JSON record is sufficient.

# Verification

- Every Qx has one primary type.
- Mixed/secondary types are justified.
- Classification evidence resolves to the parse.
- Ambiguous framing is human-confirmed or remains a blocker.
- No algorithm selection leaked into classification.

# Reference

- `references/task-type-guide.md`
