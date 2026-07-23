---
name: problem-parser
description: Parse a mathematical-modeling problem into goals, objects, data, constraints, outputs, subquestions, dependencies, variables, relationships, and human-confirmed success criteria before any method selection.
---

# Purpose

Produce a model-neutral problem contract. Do not start from favorite algorithms or infer missing attachments.

# Inputs

- complete problem statement and attachments list;
- contest rules and required deliverables;
- user clarifications;
- existing parse when revising.

# Workflow

1. Record source files and missing referenced material.
2. Extract the global objective and each Qx verbatim enough to preserve intent.
3. For each Qx identify:
   - goal;
   - objects/entities;
   - inputs and data;
   - decisions or unknowns;
   - hard and soft constraints;
   - required output and format;
   - evaluation/success criteria;
   - dependencies on other Qx;
   - uncertainty and ambiguity.
4. Separate:
   - statement facts;
   - observations from supplied data;
   - proposed relationships;
   - assumptions requiring human judgment.
5. If output form or success criteria are materially ambiguous, invoke one choice card. Do not choose the framing silently.
6. Save:
   - `planning/parse/problem_parse.json`
   - an optional concise `planning/parse/problem_parse.md` only when a human-readable view is useful.
7. Update the manifest status when present.

# JSON Contract

```json
{
  "schema_version": 1,
  "problem_source": [],
  "global_goal": "",
  "objects": [],
  "data_inventory": [],
  "global_constraints": [],
  "subquestions": [
    {
      "id": "Q1",
      "statement": "",
      "goal": "",
      "inputs": [],
      "unknowns_or_decisions": [],
      "constraints": [],
      "required_outputs": [],
      "success_criteria": [],
      "dependencies": [],
      "proposed_relationships": [],
      "ambiguities": []
    }
  ],
  "missing_material": [],
  "human_decisions_needed": []
}
```

# Rules

- Parse before classifying.
- Do not name or recommend methods.
- Do not fabricate data, fields, equations, causal relationships, or evaluation criteria.
- Preserve units, time ranges, populations, and output formats.
- A proposed relationship must be labeled as proposed until human-confirmed or evidence-supported.
- Ask only about ambiguities that change the downstream problem.

# Verification

- Every subquestion maps to a required output.
- Constraints and dependencies are explicit.
- Missing attachments and ambiguities are visible.
- Facts, proposals, assumptions, and decisions are separated.
- Human-owned success criteria are confirmed or remain a blocker.
