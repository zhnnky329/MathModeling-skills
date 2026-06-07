---
name: modeler-decision-logger
description: Collect, stamp, and freeze the human modeler's decisions into one canonical per-subquestion decision log. The decision version of frozen_numbers.json — it does NOT originate decisions, it makes the human's judgments traceable, append-only, and the single source every downstream narrative is transcribed from.
license: MIT
---

# Purpose

Maintain one canonical, append-only log of the human modeler's decisions, so that every modeling judgment a contest grades — which method and why, whether a result is good, what a number means, how confident the team is — has a single traceable home, and every downstream narrative (final method explanation, solution package, paper method-selection prose) is **transcribed from it, never re-invented**.

This is the decision-side parallel of the Frozen Numbers Convention. Just as `frozen_numbers.json` pins numbers so a bug fix can't silently shift the paper, the decision log pins judgments so the AI can't silently author what a judge grades, and so four different skills can't each re-compose the method-selection story and drift apart.

**This skill does NOT make decisions.** It never fills `modeler_decision` or `modeler_rationale`. It collects the human-authored decision artifacts that judgment-bearing skills emit (`methods/Qx/decisions/<skill>_modeler_decision.md`), validates them mechanically, stamps them, and folds them into the canonical log. It pre-fills only the mechanical fields (`decision_id`, `options_considered`, `evidence`, `ai_suggestion`).

# When to use

Use this skill:

- After a judgment-bearing skill (`method-selector`; later `result-report-generator`, `robustness-checker`, `final-method-explainer`, `solution-package-builder`) has captured a human decision in its `*_modeler_decision.md` artifact, to fold it into the canonical log.
- As a precondition check at Gates G2.5 / G4.5 / G5: "does the log contain a `DECIDED` record for the required decision point of this Qx?"
- When `final-method-explainer` / `solution-package-builder` / `paper-section-writer` need the method-selection narrative — they read it FROM this log with `decision_id` provenance, they do not re-author it.
- After the contest, to render the decision log as post-mortem review material.

Do NOT use this skill:

- To author, suggest, or auto-fill any human decision or rationale.
- To decide which method is right, what a number means, or whether a result is good.
- To overwrite a past decision (the log is append-only; a changed mind appends with `supersedes`).

# Preconditions

- At least one `methods/Qx/decisions/<skill>_modeler_decision.md` artifact exists with `status: DECIDED`.
- The Human Decision Artifact Convention in CLAUDE.md is the schema of record.

If a decision artifact is still `PENDING` (the human hasn't decided yet), do not log it — report it as "decision pending" and let the gate stay blocked.

# Inputs

- `methods/Qx/decisions/*_modeler_decision.md` — the per-skill human decision artifacts.
- The candidate pool / experiment reports the decision references (for `evidence` provenance).
- The existing `methods/Qx/qx_decision_log.md`, if any (to append to).
- `planning/session_config.json` (for `mode`, recorded per record).

# Workflow

1. Locate decided artifacts.
   - For the target Qx, find every `methods/Qx/decisions/<skill>_modeler_decision.md` with `status: DECIDED`.
   - Skip `PENDING` ones; report them as still-blocking.

2. Validate each decided artifact mechanically (do NOT re-judge the content).
   - `decided_by: human`; no sentinel survives in mandatory fields; over char floor.
   - Rationale is not a near-verbatim copy of `ai_suggestion` (normalized-whitespace / tiny edit distance only — fuzzy similarity is a ledger WARN, not a reject; formulas and `symbol_table.md` symbols are exempt).
   - Rationale references at least one concrete token from `evidence_refs`.
   - If validation fails, do NOT log it — return it to the gate as a FAIL with the exact reason.

3. Append to the canonical log.
   - Write one decision record per validated artifact into `methods/Qx/qx_decision_log.md`.
   - Stamp `decision_id` (monotonic `Qx-D01`, `Qx-D02`, …), `decision_point` (from the fixed taxonomy below), `timestamp`, and `captured_in_mode`.
   - **Append-only.** If this decision revises an earlier one, set `supersedes: <prior decision_id>` and append a new record; never edit the prior record.

4. Update the global index.
   - Maintain `planning/decision_log_index.md`: one row per decision across all Qx (id, Qx, decision_point, choice, confidence, supersedes).

5. Provide the narrative source for downstream skills.
   - When asked for the method-selection narrative, return the relevant `modeler_rationale` fields verbatim/near-verbatim, each tagged with its `decision_id`, so the consuming skill can cite provenance (`<!-- from Q1-D03 -->`).
   - The AI consuming this is forbidden from writing a method-justification sentence that has no backing decision record.

6. Staleness check (mirrors frozen_numbers).
   - If a `code/Qx/*` change shifted a result that a `result_verdict` record was based on, mark that record `STALE — modeler must re-confirm verdict against new result`. Do not silently keep a verdict the human signed against now-changed numbers.

# Decision-point taxonomy (fixed)

A record's `decision_point` is exactly one of:
`framing` · `method_choice` · `assumption_necessity` · `baseline` · `hyperparameter` · `result_verdict` · `confidence` · `claim_scope` · `figure_role`

The four a judge actually grades are **mandatory** before "Ready for Writer": `method_choice`, `result_verdict`, `confidence`, `assumption_necessity`. The rest are optional. `completeness-auditor` checks the mandatory four exist per Qx.

# Outputs

- `methods/Qx/qx_decision_log.md` — the canonical append-only log for Qx.
- `planning/decision_log_index.md` — global roll-up across all Qx.

# Output format

`methods/Qx/qx_decision_log.md`:

```markdown
# Qx Decision Log

> Canonical, append-only record of the modeler's decisions for Qx.
> Downstream narratives transcribe from here with `decision_id` provenance. Never edited in place.

---

### Q2-D01 · method_choice · 2026-06-06T14:20+08:00 · mode: learning
- **options_considered**: M1 moving-average (baseline) / M2 ARIMA / M3 grey GM(1,1)   <!-- AI-filled, neutral -->
- **evidence**: PoC feasibility — M2 RMSE 2.4 on first 50 months (methods/Q2/poc/m2_poc_result.txt) <!-- AI-filled -->
- **ai_suggestion**: M2 ARIMA — best PoC fit   <!-- AI-filled, not a verdict -->
- **modeler_decision**: M2 (CHOSEN)            <!-- HUMAN -->
- **modeler_rationale**: <human's ≥-floor words, cites a number from evidence>   <!-- HUMAN -->
- **confidence**: medium
- **supersedes**: —

### Q2-D02 · result_verdict · 2026-06-07T09:10+08:00 · mode: speed
...
```

`planning/decision_log_index.md`:

```markdown
# Decision Log Index (all subquestions)

| id | Qx | decision_point | choice | confidence | supersedes |
|----|----|----------------|--------|------------|------------|
| Q2-D01 | Q2 | method_choice | M2 | medium | — |
| Q2-D02 | Q2 | result_verdict | M2 CHOSEN | high | — |
```

# Post-contest review

Because every record carries `options_considered`, `evidence`, the human's `modeler_decision` + `modeler_rationale`, and a `supersedes` chain, the index is a decision diary. After the contest it renders, per record: "At Q2-D01 you chose M2 over M3 because <your words>; the evidence then was <metrics>." The `supersedes` chains show where the team's thinking changed — the most useful thing for a student to revisit. This is the learning payoff: the artifact that gated the contest is the study guide afterward, with zero extra authoring.

# Rules

- Never author, suggest, or auto-fill `modeler_decision` or `modeler_rationale`. Pre-fill only `decision_id` / `options_considered` / `evidence` / `ai_suggestion`.
- Never decide which method is right, what a number means, or whether a result is good.
- Append-only. Never edit or delete a past record. A changed mind is a new record with `supersedes`.
- Do not log a `PENDING` artifact. Do not log an artifact that fails mechanical validation — return it to the gate.
- Validation is mechanical only (existence / floor / sentinel / near-verbatim-copy / evidence-citation). Do not grade the modeling content.
- A downstream narrative sentence claiming "why we chose X" must trace to a `modeler_rationale` in this log. If the human hasn't logged the why, the paper may not assert the why.
- Keep the mandatory decision-point set minimal (the four graded ones) to avoid authoring burden; the rest are opt-in.

# Verification

Before handing off, verify:

- Every `DECIDED` artifact for this Qx is reflected as exactly one record.
- No `PENDING` artifact was logged.
- The mandatory decision points (`method_choice`, `result_verdict`, `confidence`, `assumption_necessity`) exist for any Qx marked Ready-for-Writer.
- The global index matches the per-Qx logs.
- No record was edited in place; revisions used `supersedes`.
- No human field was authored by this skill.

# Failure modes

Stop and report a blocker if:

- A required decision artifact is `PENDING` (the human hasn't decided) — the gate stays blocked; this is not an error, it's the design.
- A decision artifact fails mechanical validation (empty / sentinel / near-verbatim copy / no evidence citation) — return it to the modeler with the exact field.
- A downstream skill asks this logger to author a rationale — refuse.
- A `result_verdict` record is stale (its underlying number changed) — flag for re-confirmation, do not silently keep it.

# Handoff

- To `final-method-explainer` / `solution-package-builder` / `paper-section-writer`: provide the `modeler_rationale` fields with `decision_id` tags as the narrative source.
- To `workflow-orchestrator`: report which mandatory decision points are present vs missing per Qx (gate input).
- To `consistency-auditor`: the log is a cross-media source — every "why we chose X" sentence in the paper must trace to a `decision_id` here.

# Relationship to the conventions

This skill operationalizes the **Human Decision Artifact Convention** (CLAUDE.md) by giving the scattered per-skill decision artifacts one canonical, append-only home, with the same immutability discipline as the **Frozen Numbers Convention**: append-with-`supersedes` is the decision-side analogue of `解冻 → 修改 → 重冻结`.
