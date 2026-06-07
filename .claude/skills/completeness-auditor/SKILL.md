---
name: completeness-auditor
description: Verify every skill that claims "completed" produced a substantive audit/review artifact on disk with ≥ 5 explicit pass items. Runs as part of the independent audit layer that does not trust any single skill's self-declaration of done.
license: MIT
---

# Purpose

Independent completeness auditor. This skill exists because every reviewer / auditor / QA skill in the pipeline can declare "通过" verbally without ever writing the corresponding audit/review file to disk — and once a verbal claim of completion enters the conversation it becomes invisible. This skill makes the audit-file-on-disk a structural requirement of completion.

For every skill in the system that should produce an audit/review/check artifact, this skill verifies that:
1. The artifact file exists at its expected path.
2. The file is substantive (not a stub, placeholder, or empty template).
3. The file lists **≥ 5 explicit pass items** — concrete things that were checked and passed, not generic statements like "all good".
4. The file lists any failures, warnings, or unresolved issues — and routes each to a repair skill.

If any required audit file is missing, empty, or has fewer than 5 explicit pass items, this skill marks that skill's "completion" as **not actually complete** and blocks downstream progression.

This skill runs in parallel with `consistency-auditor` and before `quality-assurance-auditor`. Together they form the independent audit layer.

# When to use

Use this skill:

- Before `quality-assurance-auditor`. QA should treat any missing audit artifact as a blocker.
- After any reviewer / auditor / robustness-check / final-method-explainer claims completion — to verify the file actually got written.
- When the user asks: "did all the audits actually run?", "is anything missing from the QA chain?", "show me which review files don't exist".
- When the workflow has been running for a while and the user wants a sanity check on the audit chain.

Do NOT use this skill:

- To create the missing audit files. This skill only verifies; the repair routes back to the original skill.
- As a substitute for `consistency-auditor` (which checks cross-media facts) or `quality-assurance-auditor` (which checks paper quality and the three critical rules).

# The audit/review artifact registry

This is the canonical list of files that must exist for "completion" to be real. Maintain this list as the project evolves.

## Per-subquestion (Qx)

| Producer skill | Required artifact | Min pass items |
|----------------|-------------------|----------------|
| `python-code-reviewer` (when Python used) | `code/Qx/reviews/qx_python_review.md` | 5 |
| `matlab-code-reviewer` (when MATLAB used) | `code/matlab/Qx/reviews/qx_matlab_review.md` | 5 |
| `robustness-checker` | `robustness/Qx/qx_robustness_report.md` | 5 |
| `result-report-generator` (round N) | `results/Qx/experiments/roundN/qx_experiment_report_roundN.md` | 5 |
| `result-report-generator` (final) | `results/Qx/reports/qx_final_result_analysis.md` | 5 |
| `final-method-explainer` | `methods/Qx/qx_final_method_explanation.md` | (structural, not pass-item-based) |
| `solution-package-builder` | `results/Qx/reports/qx_solution_package_for_writer.md` + `results/Qx/reports/frozen_numbers.json` | (structural) |
| `figure-table-planner` | `methods/Qx/qx_figure_table_plan.md` | (structural) |
| `method-selector` | `methods/Qx/qx_method_candidates.md` + `methods/Qx/qx_method_iteration_log.md` | (structural) |
| `modeler-decision-logger` | `methods/Qx/qx_decision_log.md` | (decision-record check — see below) |

### Human decision artifacts (the enforcement arm for the human gates)

These are the files the human-decision gates (G2.5, G4.5, G4 sign-off) block on. `completeness-auditor` is what makes those gates real: a missing, PENDING, or under-floor decision artifact is a structural gap caught here, exactly like a missing review file. This is the `judgment-gate-checker` rule, folded in (no separate skill).

| Gate | Producer skill | Required decision artifact | DECIDED-check |
|------|----------------|----------------------------|---------------|
| G2.5 | `method-selector` | `methods/Qx/decisions/method-selector_modeler_decision.md` (`qx_method_choice`) | yes |
| G4.5 | `result-report-generator` | `methods/Qx/decisions/result-report-generator_modeler_decision.md` (`qx_result_verdict`) | yes |
| G4.5 | `robustness-checker` | `methods/Qx/decisions/robustness-checker_modeler_decision.md` (`qx_stability_verdict`) | yes |
| G4.5 | `final-method-explainer` | `methods/Qx/decisions/final-method-explainer_modeler_decision.md` (`qx_method_explanation`) | yes |
| G4 | `solution-package-builder` | `methods/Qx/decisions/solution-package-builder_modeler_decision.md` (`qx_package_signoff`) | yes |

**DECIDED-check** (mechanical, no NLP — this is what a human gate's pass keys on):
1. File exists.
2. Front-matter `status: DECIDED` AND `decided_by: human` (`PENDING` / `ai` / `auto` ⇒ FAIL — treat like a missing artifact).
3. Every mandatory human field present, over its char floor, no surviving sentinel (`<<<`, `TODO`, `TBD`, `待补充`, `...`, empty).
4. The `## Modeler's rationale` body is NOT a near-verbatim copy of `ai_suggestion` (normalized-whitespace equality / tiny edit distance only — fuzzy similarity is a WARN written to the provenance ledger, NEVER a FAIL; formulas and `symbol_table.md` symbols are exempt).
5. The rationale cites ≥1 concrete token from `evidence_refs` (a number, a candidate id, a symbol). For `qx_stability_verdict` and `confidence` rationales this is HARD (must cite a number); elsewhere it is a WARN.
6. Staleness: if a `code/Qx/*` file is newer than the decision's `decided_at` and the decision sat behind a now-changed result, flag `STALE — modeler must re-confirm` (same mtime rule as `frozen_numbers.json`).

A decision artifact failing any of 1–3 is BLOCKING (the gate cannot pass). Item 4 failing is BLOCKING (it's a copy). Items 5–6 produce WARN unless noted HARD. Report each with the exact field, so the modeler knows precisely what to fill.

## Global (project-wide)

| Producer skill | Required artifact | Min pass items |
|----------------|-------------------|----------------|
| `data-auditor-cleaner` | `workspace/data_clean/data_report.md` | 5 |
| `symbol-table-builder` | `planning/symbol_table.md` | (structural) |
| `model-assumptions-builder` | `planning/model_assumptions.md` | (structural) |
| `consistency-auditor` | `paper/audits/cross_media_consistency_audit.md` | 5 |
| `reference-manager` | `paper/audits/reference_audit.md` | 5 |
| `paper-polisher` | `paper/audits/polish_report.md` | 5 |
| `quality-assurance-auditor` | `paper/qa_report.md` | 5 |

## Filesystem fallback paths (older conventions still supported)

If the path in the registry above does not exist, fall back to checking these legacy paths and report which convention was used:

- `workspace/code/code-review/python_review_summary.md` (legacy `python-code-reviewer` output)
- `workspace/code/code-review/matlab_review_summary.md` (legacy `matlab-code-reviewer` output)
- `workspace/data/data_report.md` (legacy data audit)

# Preconditions

This skill can run at any time. It will only audit files that should exist based on workflow state.

To know which artifacts to expect, read:

- `planning/progress_dashboard.md` (if exists) — tells you which subquestions are at which state.
- Otherwise, scan the workspace and infer which subquestions have started.

# Inputs

- `planning/progress_dashboard.md` (preferred — tells you which Qx claim what state).
- File listings under `methods/`, `code/`, `results/`, `robustness/`, `paper/`.
- The audit registry above.

# Workflow

1. **Determine scope.**
   - For each subquestion Qx, determine which state it claims to be in (from `progress_dashboard.md` or by scanning the workspace).
   - For each claimed state, look up which artifacts must exist (from the registry).
   - Also enumerate global artifacts.

2. **Verify existence.**
   For each required artifact:
   - Does the file exist?
   - If yes → proceed to substantive check.
   - If no → mark MISSING; route back to the producer skill.

3. **Verify substantive content.**
   For files that should have ≥ 5 explicit pass items:
   - Open the file.
   - Count distinct explicit pass items. An "explicit pass item" is a checkmarked or numbered statement of the form "✅/✓/[x] <specific thing> was checked and passed because <reason or evidence>".
   - Generic statements like "all checks passed" or "looks good" do NOT count as a pass item.
   - If fewer than 5 explicit pass items → mark INSUFFICIENT; route back to the producer skill.

   For files that are structural (no pass-item requirement):
   - Verify the structural sections required by that skill's output format are present and non-empty.
   - If a section is empty or contains only a placeholder ("TBD", "TODO", "待补充", "..."), mark INSUFFICIENT.

4. **Verify recency (staleness check).**
   - If `frozen_numbers.json` exists, compare its `frozen_at` timestamp to the most recent modification time of any `code/Qx/` source file.
   - If code is newer than the frozen snapshot, mark the snapshot as STALE — recommend re-freezing via `solution-package-builder`.
   - Same check applies to audit files: if a `*_review.md` is older than the code it reviewed, mark STALE.

5. **Produce the completeness report.**
   Save to `paper/audits/completeness_audit.md`.

6. **Route repairs.**
   Every MISSING / INSUFFICIENT / STALE entry carries the producer skill name in a `repair_skill` field. Hand the report to `workflow-orchestrator` for routing.

# Outputs

Produce one file:

- `paper/audits/completeness_audit.md`

# Output format

```markdown
# Completeness Audit Report

> **Status**: [PASSED / FAILED]
> **Date**: [timestamp]
> **Scope**: [Q1, Q2, Q3, Q4 + global]

## Summary

| Producer Skill | Required Artifact | Status | Pass Items | Notes |
|---------------|-------------------|--------|------------|-------|
| python-code-reviewer | code/Q1/reviews/q1_python_review.md | ✅ OK | 7 | — |
| matlab-code-reviewer | code/matlab/Q2/reviews/q2_matlab_review.md | ❌ MISSING | — | re-run matlab-code-reviewer for Q2 |
| robustness-checker | robustness/Q1/q1_robustness_report.md | ⚠ INSUFFICIENT | 2 | only 2 explicit pass items; need ≥ 5 |
| solution-package-builder | results/Q3/reports/frozen_numbers.json | ⚠ STALE | n/a | frozen 2026-05-10; code modified 2026-05-15 |
| consistency-auditor | paper/audits/cross_media_consistency_audit.md | ✅ OK | 8 | — |
| quality-assurance-auditor | paper/qa_report.md | ❌ MISSING | — | run after consistency + completeness pass |

## Pass Items (≥ 5 required for the audit to count as run)

1. ✅ `code/Q1/reviews/q1_python_review.md` exists with 7 explicit pass items.
2. ✅ `methods/Q1/q1_final_method_explanation.md` has all required structural sections filled.
3. ✅ `planning/symbol_table.md` is non-empty and contains 23 symbol definitions.
4. ✅ `results/Q1/reports/frozen_numbers.json` exists and is newer than all Q1 source files (not stale).
5. ✅ `workspace/data_clean/data_report.md` has 6 explicit pass items.
6. ✅ ...

## Missing Artifacts

| # | Skill | Expected Path | Repair Skill | Severity |
|---|-------|--------------|--------------|----------|
| 1 | matlab-code-reviewer | code/matlab/Q2/reviews/q2_matlab_review.md | matlab-code-reviewer | BLOCKING |
| 2 | quality-assurance-auditor | paper/qa_report.md | quality-assurance-auditor | BLOCKING (run last) |

## Insufficient Artifacts (fewer than required pass items)

| # | File | Pass Items Found | Required | Repair Skill |
|---|------|------------------|----------|--------------|
| 1 | robustness/Q1/q1_robustness_report.md | 2 | 5 | robustness-checker |

## Stale Artifacts

| # | File | Frozen / Reviewed At | Source Modified At | Repair Skill |
|---|------|---------------------|-------------------|--------------|
| 1 | results/Q3/reports/frozen_numbers.json | 2026-05-10 14:22 | 2026-05-15 09:11 | solution-package-builder |

## Verdict

- **Audit layer ready for QA**: [yes / no]
- **Final assembly allowed**: [no — QA has not run yet]
- **Recommended next skill**: [first missing/insufficient producer skill in repair order]

## Repair order (suggested)

1. matlab-code-reviewer → produce `code/matlab/Q2/reviews/q2_matlab_review.md`.
2. robustness-checker → expand Q1 robustness report to ≥ 5 pass items.
3. solution-package-builder → re-freeze Q3 numbers after confirming code changes.
4. quality-assurance-auditor → run after the above pass.
```

# Rules

- Do NOT create any missing audit file. Repair routes back to the producer skill.
- Do NOT count generic statements ("all good", "passed") as pass items. Only count concrete, evidence-bearing statements.
- Do NOT skip a check because the producer skill claimed completion verbally. Verbal claims do not count; only files on disk count.
- ALWAYS list ≥ 5 explicit pass items in your own report. If you cannot, status is `not_run`.
- For staleness, the rule is: a review/freeze file must be newer than every source file it reviewed. Off by one second is fine; older by an hour is stale.
- If a producer skill is not applicable (e.g., no MATLAB used, so `matlab-code-reviewer` has nothing to review), mark it `not_applicable` — do not mark it MISSING.
- The audit registry is the contract. If a new producer skill is added to the system, update the registry in this file FIRST, then run.

# Verification

Before returning the report, verify:

- The pass list has ≥ 5 explicit items.
- Every entry in the summary table has a status, producer skill name, and (if not OK) a repair skill.
- The verdict matches the entries — cannot be PASSED if any entry is BLOCKING.
- The report is saved to `paper/audits/completeness_audit.md` (create dir if missing).

# Failure modes

Stop and report a blocker if:

- The user asks to mark an artifact as "complete" by writing the audit file directly (not the producer skill's job).
- The user asks to bypass an INSUFFICIENT entry by lowering the pass-item threshold case-by-case. The threshold is structural; if a particular check legitimately has fewer than 5 items, the producer skill should justify and document that — and this auditor should still flag it.

# Stop conditions

This skill must stop instead of guessing when:

- The workspace state is so unclear that we cannot tell which Qx are in progress.
- The producer of a missing artifact cannot be determined (e.g., a file appeared on disk but doesn't match the registry — flag it as orphaned).

When stopping, output:
- the blocker
- the affected artifact
- recommended next skill

# Handoff

After producing the completeness report:

- If the verdict is PASSED → hand off to `quality-assurance-auditor`.
- If anything is MISSING / INSUFFICIENT / STALE → hand off to `workflow-orchestrator` with the repair list.

# Relationship to the audit layer

This skill is one of three independent auditors. They run in this order before final assembly:

1. `consistency-auditor` — cross-media facts match (numbers, files, symbols, parameters).
2. `completeness-auditor` (this skill) — every claimed completion has a substantive artifact on disk.
3. `quality-assurance-auditor` — workflow completeness, three critical rules, anti-fabrication, paper quality.

Each is independent; each can fail. Any failure blocks final assembly.

# Examples

## Example 1: Everything OK

Input: progress dashboard says Q1 at state 09 (Ready for Writer); all artifacts on disk; every review file has ≥ 5 pass items; nothing stale.

Output: 8 pass items listed; 0 missing; 0 insufficient; verdict PASSED → `quality-assurance-auditor`.

## Example 2: Reviewer file missing

Input: `code/Q2/q2_main.py` exists; modeler said "Python code passed review"; but `code/Q2/reviews/q2_python_review.md` does not exist on disk.

Output:
```
| 1 | python-code-reviewer | code/Q2/reviews/q2_python_review.md | python-code-reviewer | BLOCKING |
```
Verdict: FAILED. The producer skill must actually write the review file — verbal "passed" doesn't count.

## Example 3: Pass items too thin

Input: `robustness/Q1/q1_robustness_report.md` exists but only says "robustness OK".

Output:
```
| 1 | robustness/Q1/q1_robustness_report.md | 0 (only "robustness OK", not concrete) | 5 | robustness-checker |
```
Repair: `robustness-checker` must re-run and list ≥ 5 specific checks that passed (e.g., "weight ±10% — top 3 ranking unchanged", "removed indicator X — TOPSIS score shifted by 0.02 only", etc.).

## Example 4: Stale frozen snapshot

Input: `frozen_numbers.json` was created on 2026-05-10; `code/Q3/q3_main.py` was modified on 2026-05-15 after a bug fix.

Output:
```
| 1 | results/Q3/reports/frozen_numbers.json | 2026-05-10 14:22 | 2026-05-15 09:11 | solution-package-builder |
```
Repair: `solution-package-builder` must re-freeze after the modeler confirms the new numbers are canonical. Also: `consistency-auditor` will likely flag the paper as drifted — both audits should run in sequence.

## Example 5: Not applicable

Input: project uses Python only; no `.m` files anywhere.

Output:
```
| matlab-code-reviewer | n/a | not_applicable | — | no MATLAB files in project |
```
Not counted as MISSING.
