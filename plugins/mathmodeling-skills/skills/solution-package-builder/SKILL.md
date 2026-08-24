---
name: solution-package-builder
description: Assemble a submission-ready writer package from final method, result, robustness, figure, and human-decision artifacts, then freeze approved numerical claims with provenance.
---

# Purpose

Create the writer's single source package and immutable numerical snapshot. Do not manufacture missing judgments or freeze unapproved claims.

# Preconditions

- `rigor_profile` is `submission`.
- Final method explanation, final result analysis, robustness report, and figure plan exist.
- Human method, result, stability, and claim-scope decisions exist in `qx_decisions.jsonl`.
- Canonical sources are current.

# Workflow

1. Collect final method structure, result claims, limitations, figures, tables, and decision provenance.
2. Draft `results/Qx/reports/qx_solution_package_for_writer.md`.
3. Flag every proposed top-line claim with:
   - value and unit;
   - canonical source path and location;
   - robustness support;
   - decision ID for claim scope or rationale;
   - confidence/limitation.
4. Invoke one final choice card when package sign-off is missing:
   - keep;
   - downgrade;
   - drop.
5. Route the human answer to `modeler-decision-logger` as `package_signoff`.
6. Only after sign-off, generate `results/Qx/reports/frozen_numbers.json`.
7. Verify every numerical package claim resolves to the freeze and every judgment claim resolves to a human decision ID.

# Frozen Number Contract

Each entry contains:

```json
{
  "claim_id": "q1_main_rmse",
  "value": 2.4,
  "unit": "units",
  "source_file": "results/Q1/experiments/final/metrics/main.json",
  "source_locator": "$.rmse",
  "frozen_at": "ISO-8601",
  "frozen_by_skill": "solution-package-builder",
  "decision_id": "q1_package_signoff"
}
```

Use a source line only for stable text files; use a JSON path, table key, or row/column identifier for structured data.

# Rules

- Do not create `solution-package-builder_modeler_decision.md`.
- Do not emit `frozen_numbers.json` before human package sign-off.
- Never edit an existing freeze by hand.
- Transcribe human rationales; do not re-compose them as stronger claims.
- The package may cite the compact method-card history but must not depend on a separate iteration log.
- Do not copy raw exploratory outputs into the package without final validation.

# Change and Re-freeze

When a canonical source changes after freeze:

1. append the reason to `freeze_change_log.md`;
2. update and rerun the canonical source;
3. obtain renewed human judgment when the evidence changed materially;
4. regenerate the freeze;
5. run scoped consistency for Qx.

# Verification

- All prerequisites are final and current.
- Package sign-off exists in the JSONL ledger.
- Every frozen value has a real canonical source and stable locator.
- Every package number matches the freeze.
- Every modeling judgment traces to a human decision.
- Writer can use the package without searching scattered results.
