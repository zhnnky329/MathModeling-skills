---
name: python-model-code-generator
description: Generate and run minimal reproducible Python modeling code for the human-approved main method and usable baseline, saving compact experiment artifacts and a canonical run summary.
---

# Preconditions

- G2.5 human method choice is recorded in `methods/Qx/qx_decisions.jsonl`.
- `code/Qx/qx_code_plan.md` exists.
- Required cleaned data and profile exist.
- The plan targets Python.

Legacy method pools and `code/model-code-analyzer.md` may be read during migration, but they do not override the human choice.

# Workflow

1. Read the code plan, decision ledger, method card, probe conditions, and data profile.
2. Confirm scope:
   - one approved main method;
   - one usable baseline;
   - fallback only when an activation decision or evidenced trigger exists.
3. Generate clear runnable `.py` files under `code/Qx/`.
4. Use project-root-safe paths, fixed seeds, explicit inputs, and minimal justified dependencies.
5. Save:
   - tables to `results/Qx/experiments/roundN/tables/`;
   - metrics to `.../metrics/`;
   - useful diagnostic/comparison figures to `.../figures/`;
   - canonical `run_summary.json`.
6. Evaluate and record output-degeneracy and fallback-trigger metrics required by the plan.
7. Persist full logs only on failure or when a warning needs reproduction.
8. Run the code. Do not claim success from code generation alone.
9. Hand off to `code-reviewer`.

# Script Layout

Prefer the smallest clear layout:

```text
code/Qx/
├── qx_code_plan.md
├── qx_baseline.py
├── qx_main.py
└── run_all.py        # only when coordination is useful
```

Do not create one script per unapproved candidate. Do not create a README that duplicates the code plan.

# Run Summary

Follow the schema in `model-code-analyzer`. Include:

- approved decision ID;
- method IDs and roles;
- inputs and outputs;
- seed and environment;
- execution status and timing;
- compact metric summaries;
- output-degeneracy evidence;
- warnings/errors;
- fallback-trigger state.

# Rules

- Do not change the approved model or baseline.
- Do not read or overwrite raw data.
- Do not hide assumptions in code.
- Do not emit placeholder metrics, figures, or successful statuses.
- Prefer portable `.py` scripts over notebook-only workflows.
- Keep intermediate files only when needed for explanation, review, robustness, or debugging.
- Use Type 1 diagnostic figures internally; do not present them as paper figures.

# Verification

- Main and baseline both ran and are directly comparable.
- Fallback code is absent unless activated.
- Formal outputs and run summary exist.
- Seed, inputs, versions, warnings, and errors are recorded.
- Required concentration/degeneracy checks are saved.
- Next handoff is `code-reviewer`.
