---
name: final-method-explainer
description: Build the authoritative final method explanation for a submission-ready subquestion from the method card, human decision ledger, code plan, final results, and robustness evidence.
---

# Purpose

Explain the selected method completely without re-authoring why the human chose it.

# Preconditions

- `rigor_profile` is `submission` or writer handoff is explicitly requested.
- Human method choice and result verdicts are recorded in `qx_decisions.jsonl`.
- Approved code ran and final result/robustness evidence exists.

# Sources

Use:

- `qx_method_card.md`
- `qx_decisions.jsonl`
- `planning/model_assumptions.md`
- `planning/symbol_table.md`
- `qx_code_plan.md`
- final run summary and result analysis
- robustness summary/report

Read legacy candidate and iteration logs only for migration.

# Workflow

1. Resolve the final method and baseline from the latest non-stale human decisions.
2. Transcribe the human's selection rationale faithfully and cite its `decision_id`.
3. Explain:
   - goal and scope;
   - assumptions, including human-confirmed necessity labels;
   - symbols and units;
   - mathematical formulation;
   - inputs, outputs, objective/criteria, and constraints;
   - solution procedure;
   - baseline and why it is valid;
   - fallback trigger and whether it fired;
   - validation, robustness, limitations, and applicable range.
4. Ensure formulas match code and symbol table.
5. Save `methods/Qx/qx_final_method_explanation.md`.

# Rules

- Do not infer the chosen method from best metrics.
- Do not invent the why-this-method narrative.
- Do not create a new pending decision artifact.
- Do not restate a long iteration diary; include only material eliminated alternatives and evidence.
- Do not include unsupported numerical claims.

# Verification

- Final method and rationale trace to decision IDs.
- Assumptions, symbols, formulas, units, and code agree.
- Baseline is usable rather than merely diagnostic.
- Risks, fallback behavior, and limitations are explicit.
- The explanation is self-contained enough for the writer.
