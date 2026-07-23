---
name: model-code-analyzer
description: Translate a human-approved main method and usable baseline into a minimal language-neutral implementation and experiment contract. Use after G2.5 and data readiness, before Python or MATLAB code generation.
---

# Purpose

Define exactly what code must implement and save. Do not expand the approved experiment scope or fully plan a dormant fallback.

# Preconditions

- `methods/Qx/qx_method_card.md` and probe summary exist.
- `methods/Qx/qx_decisions.jsonl` contains a human `DECIDED` method choice.
- A usable baseline is identified.
- Cleaned data and `data_profile.json` are ready when data is required.
- Implementation target and round are known.

Read legacy candidate/decision artifacts only when the new artifacts are absent.

# Workflow

1. Read the approved choice, method card, probe conditions, and experiment budget.
2. Plan only:
   - approved `main`;
   - approved `usable_baseline`;
   - shared helpers and comparison logic.
3. Record the fallback ID and trigger, but do not plan its full implementation unless the trigger is already evidenced and the human chose activation.
4. Map mathematical definitions to inputs, processing steps, intermediate evidence, outputs, and validation checks.
5. Define a directly comparable metric/output contract for main and baseline.
6. Define the round output:

```text
results/Qx/experiments/roundN/
├── figures/
├── tables/
├── metrics/
└── run_summary.json
```

Create `logs/` only for failures, warnings, or reproducibility needs.
7. Write `code/Qx/qx_code_plan.md` for Python or `code/matlab/Qx/qx_code_plan.md` for MATLAB.
8. Hand off to the matching language generator.

# Run Summary Contract

Require:

```json
{
  "schema_version": 1,
  "question": "Q1",
  "round": "round1",
  "implementation_target": "python",
  "random_seed": 2026,
  "approved_decision_id": "q1_method_choice",
  "methods": [
    {
      "method_id": "M1",
      "role": "usable_baseline",
      "script": "code/Q1/q1_baseline.py",
      "status": "success",
      "execution_time_seconds": 0,
      "input_files": [],
      "output_files": [],
      "figure_files": [],
      "metrics_summary": {},
      "warnings": [],
      "errors": []
    }
  ],
  "comparison": {},
  "fallback_trigger": {
    "fallback_id": null,
    "condition": null,
    "observed": false,
    "evidence": null
  },
  "environment": {}
}
```

# Code Plan Contents

- target language and round purpose;
- approved decision ID;
- main and baseline IDs and roles;
- input fields and units;
- per-method computation steps;
- comparable outputs and metrics;
- risk-probe conditions that implementation must monitor;
- fallback trigger evaluation;
- paths, seed, dependencies, and expected runtime;
- named review checks expected downstream.

# Rules

- Do not write executable model code.
- Do not add candidates or change model meaning.
- Do not plan a diagnostic reference as the official baseline.
- Do not implement a fallback before activation.
- Do not require success logs.
- Do not create a README when the code plan already provides the same instructions.
- Stop if a human choice, required parameter, input field, or comparable baseline output is missing.

# Verification

- Plan scope is exactly main plus usable baseline unless fallback activation is recorded.
- Outputs are directly comparable.
- Probe risks and fallback trigger are represented in `run_summary.json`.
- Paths follow the experiment contract.
- Handoff targets the correct language generator.
