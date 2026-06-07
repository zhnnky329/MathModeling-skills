---
name: consistency-auditor
description: Audit cross-media consistency of numbers, file names, symbols, and parameters across tex/code/results/data/appendix. Runs as an independent audit layer that does not trust any single skill's self-declaration of "done".
license: MIT
---

# Purpose

Independent cross-media consistency auditor. This skill exists because the rest of the pipeline cannot be trusted to police itself: every generative skill (method-selector, code-generator, result-report-generator, paper-section-writer, ...) self-declares "完成", and history shows that "完成" often hides drift — a number written into the paper is one bug-fix behind the code, a figure filename in the tex no longer exists on disk, a symbol in the method explanation has been renamed in the symbol table.

This skill compares the **same fact stated in multiple places** and reports every divergence. It does not believe any single source — it cross-checks them.

The audit covers five dimensions:
1. **Numbers** — every numerical claim in `paper/sections/*.tex` is traced back to a result artifact (`results/Qx/reports/*.md`, `results/Qx/experiments/*/metrics/*.json|csv`, `frozen_numbers.json`).
2. **File names** — every figure/table/appendix code reference in the paper must point to a file that exists on disk.
3. **Symbols** — symbols used in `paper/sections/*.tex` and `methods/Qx/qx_final_method_explanation.md` must be defined in `planning/symbol_table.md`, with the same meaning everywhere.
4. **Parameters** — parameter values written into the paper (e.g. K=30, α=0.05, seed=2026) must match the values actually used in `code/Qx/*.py` or `code/matlab/Qx/*.m`.
5. **Decision provenance** — every judgment claim in the paper ("we chose X because…", confidence, verdict) must trace to a `DECIDED` record in `methods/Qx/qx_decision_log.md` via a `decision_id` marker. This is the decision-side analogue of the numbers check; it stops the AI from re-authoring the human's reasoning.

This skill does NOT write the paper, fix the code, or regenerate results. It only reports divergences and routes them to the right repair skill.

This skill runs in parallel with `quality-assurance-auditor` and `completeness-auditor`. The three form an independent audit layer; any one of them failing blocks final assembly.

# When to use

Use this skill:

- After `paper-section-writer` has drafted paper sections for any subquestion (run per-subquestion, not only at end of project).
- After `solution-package-builder` has produced a solution package — to verify the package's numbers match the underlying results.
- Whenever a number, parameter, file name, or symbol is changed in any artifact — to detect downstream drift.
- Before `quality-assurance-auditor`. QA should see this audit's output and treat any unresolved divergence as a blocker.
- When the user asks: "are the paper numbers consistent with the code?", "did the appendix reference still match?", "is the figure filename right?", "did anything drift after that bug fix?".

Do NOT use this skill:

- To make corrections. This skill only reports.
- To approve final submission. That is `quality-assurance-auditor`'s job after this report passes.
- As a substitute for `paper-polisher`'s formula-consistency check inside a single document.

# Preconditions

This skill can run with whatever is available. It will report what it could and could not check:

- At least one of: `paper/sections/*.tex|md`, `results/Qx/reports/*.md`, `methods/Qx/qx_final_method_explanation.md`.
- Optional but strongly recommended: `frozen_numbers.json` per subquestion (see `solution-package-builder`).
- Optional: `planning/symbol_table.md`, `results/Qx/experiments/final/run_summary.json`.

If the paper drafts do not exist yet, this skill reports "no paper sections to audit" and stops without error.

# Inputs

Scan and read:

**Source-of-truth files (the "ground truth" tier)**
- `results/Qx/reports/qx_final_result_analysis.md` — programmer's final numbers.
- `results/Qx/reports/qx_solution_package_for_writer.md` — packaged numbers.
- `results/Qx/reports/frozen_numbers.json` — frozen numerical snapshot (if `solution-package-builder` ran).
- `results/Qx/experiments/final/metrics/*.json|csv` — raw metric files.
- `results/Qx/experiments/final/tables/*.csv` — raw result tables.
- `results/Qx/experiments/final/run_summary.json` — parameters actually used.
- `methods/Qx/qx_final_method_explanation.md` — declared assumptions, parameters, symbols.
- `code/Qx/*.py` and `code/matlab/Qx/*.m` — actual implementation (for parameter values, seed values).
- `planning/symbol_table.md` — symbol definitions.
- `paper/figures/` and `results/Qx/experiments/*/figures/` — actual figure files on disk.

**Targets to audit (the "claims" tier)**
- `paper/sections/*.tex|md` — paper draft text.
- `paper/main.tex` — assembled paper, if present.
- `paper/refs.bib` — bibliography (for reference-file integrity, not citation correctness — that is `reference-manager`'s job).

# Workflow

1. **Pin the source of truth.**
   For each subquestion Qx, prefer in this order:
   1. `results/Qx/reports/frozen_numbers.json` (if it exists, this is the canonical snapshot)
   2. `results/Qx/reports/qx_solution_package_for_writer.md`
   3. `results/Qx/reports/qx_final_result_analysis.md`
   4. raw metric/table files in `results/Qx/experiments/final/`

   If no source of truth exists for Qx, mark Qx as "unauditable — no canonical numbers" and skip it.

2. **Extract numerical claims from paper sections.**
   Scan each paper section for:
   - Decimal numbers (e.g., `0.92`, `12.4`)
   - Percentages (e.g., `35%`, `±10%`)
   - Integer counts and identifiers (e.g., `K=30`, `n=120`, `seed=2026`)
   - Confidence intervals, error bars
   - Ranking positions

   For each claim, record the surrounding context (claim phrasing) so a human can locate it.

3. **Trace each claim to the source of truth.**
   For each extracted claim, find the matching value in the source of truth and compare.
   - Exact-match required for integers and identifiers.
   - Decimal claims: round-tolerant comparison to the precision the paper claims (e.g., paper says `0.92` → source must be in `[0.915, 0.925)`).
   - Report any mismatch, including the file:line in both paper and source.

4. **Audit figure/table file references.**
   - Extract every `\includegraphics{...}`, `\input{...}`, image link, and table file reference from the paper.
   - For each, verify the file exists on disk under `paper/figures/` or the referenced path.
   - Report any reference whose target file does not exist.
   - Cross-check: the figure file referenced must match the file the figure-table plan assigned to that paper section.

5. **Audit appendix / code references.**
   - Extract every appendix mention of a code file (e.g., `q3_main.py`, `q3_attachment3.m`).
   - Verify each named file exists under `code/Qx/` or `code/matlab/Qx/`.
   - If the appendix embeds code snippets, verify the snippet appears verbatim in the actual source file (allowing whitespace/comment normalization).

6. **Audit symbol consistency.**
   - Extract every symbol used in `paper/sections/*.tex` and `methods/Qx/qx_final_method_explanation.md`.
   - Verify each symbol is defined in `planning/symbol_table.md` with a matching meaning.
   - Report symbols used but not defined, defined but unused (informational), or defined with conflicting meanings across files.

7. **Audit parameter consistency.**
   - Extract every named parameter value claimed in paper or method explanation (e.g., `K=30`, `α=0.05`, `learning_rate=0.001`, random seed).
   - Find the corresponding value in `code/Qx/` (search for assignments like `K = 30`, `SEED = 2026`, `alpha = 0.05`).
   - Report any parameter where paper and code disagree.

7.5. **Audit decision-narrative provenance (the rationale-laundering check).**
   This is the decision-side analogue of the numbers check: just as every paper number must trace to `frozen_numbers.json`, every *judgment claim* must trace to a human decision record. It is what stops the AI from re-authoring "why we chose X" downstream of the human's logged reason.
   - Extract every method-justification / verdict / confidence sentence from `paper/sections/*.tex`, `methods/Qx/qx_final_method_explanation.md`, and `results/Qx/reports/qx_solution_package_for_writer.md` — i.e., every "we chose X because…", "the result is reliable because…", "we are confident that…".
   - Each such sentence MUST carry a `decision_id` provenance marker (e.g., `<!-- from Q1-D03 -->`) that resolves to a `DECIDED` record in `methods/Qx/qx_decision_log.md`.
   - Report as **BLOCKING** any judgment sentence with no `decision_id`, or whose `decision_id` does not exist / is not `DECIDED` in the log → `repair_skill: modeler-decision-logger` (the human must log the decision) or `final-method-explainer` / `solution-package-builder` (must transcribe, not re-author).
   - Also flag the reverse: a `DECIDED` method-choice record whose rationale appears **nowhere** in the paper (informational — the team's reasoning isn't being used).
   - Staleness: if a decision record is marked `STALE` by `completeness-auditor` (its underlying number changed), any paper sentence citing it is suspect → WARN.

8. **Build the audit report.**
   Save to `paper/audits/cross_media_consistency_audit.md`. Structure:
   - Overall pass/fail.
   - **MUST list ≥ 5 explicit pass items** (checks that ran and found no divergence) — empty pass list is treated as "audit not run".
   - Divergence list with severity, paper location, source location, suggested repair skill.
   - Unauditable items (where source of truth was missing).

9. **Route repairs.**
   Each divergence carries a `repair_skill` field. Typical routing:
   - Paper number ≠ source number → `paper-section-writer` (paper needs update) OR `result-report-generator` (source is wrong) — pick based on which is the canonical truth.
   - Figure file missing → `math-figure-generator` (re-render) or `paper-section-writer` (remove/fix reference).
   - Symbol undefined → `symbol-table-builder` or `paper-section-writer`.
   - Parameter drift → `python-code-reviewer` / `matlab-code-reviewer` to check the code is correct, then either update code or update paper.

10. **Return control.**
    Hand audit result to `workflow-orchestrator`. Do not approve final assembly directly.

# Outputs

Produce exactly one report file:

- `paper/audits/cross_media_consistency_audit.md`

# Output format

```markdown
# Cross-Media Consistency Audit Report

> **Status**: [PASSED / FAILED]
> **Date**: [timestamp]
> **Scope**: [list of subquestions audited]
> **Source-of-truth tier used per Qx**: e.g., Q1=frozen_numbers.json, Q2=solution_package, Q3=unauditable

## Pass Items (≥ 5 required for the audit to count as "run")

1. ✅ All 14 numerical claims in `paper/sections/q1.tex` match `results/Q1/reports/frozen_numbers.json`.
2. ✅ All 6 figure references in `paper/sections/q1.tex` resolve to files on disk.
3. ✅ All 8 symbols in `paper/sections/q1.tex` are defined in `planning/symbol_table.md`.
4. ✅ Parameter `K=30` in `paper/sections/q2.tex` matches `code/Q2/q2_main.py:42`.
5. ✅ Random seed `SEED=2026` is consistent across all 4 subquestion code files.
6. ✅ ...

## Divergences

| # | Severity | Dimension | Paper Location | Source Location | Paper Value | Source Value | Repair Skill |
|---|----------|-----------|---------------|-----------------|-------------|--------------|--------------|
| 1 | BLOCKING | number | paper/sections/q3.tex:124 | results/Q3/reports/q3_final_result_analysis.md:section 2 | `Z=42` | `Z=41` | paper-section-writer |
| 2 | BLOCKING | file_ref | paper/sections/q2.tex:88 | (file missing on disk) | `q2_ranking.png` | — | math-figure-generator |
| 3 | WARNING | symbol | paper/sections/q1.tex:201 | planning/symbol_table.md | `R` used as resilience score | `R` defined as "set of regions" | symbol-table-builder |
| 4 | BLOCKING | parameter | paper/sections/q3.tex:67 | code/Q3/q3_main.py:18 | `K=12` | `K=30` | python-code-reviewer |

## Unauditable Items

| # | Reason | Affects | Suggested Resolution |
|---|--------|---------|---------------------|
| 1 | No frozen_numbers.json for Q3 | All Q3 numerical claims | Run `solution-package-builder` for Q3 to freeze numbers |

## Cross-Subquestion Checks

- Random seed consistency: ✅ all subquestions use `SEED=2026`
- Symbol table coverage: ⚠ Q4 introduces symbol `λ` but `planning/symbol_table.md` does not define it

## Verdict

- **Final assembly allowed**: [yes / no]
- **Blocking divergences**: [count]
- **Warning divergences**: [count]
- **Recommended next skill**: [workflow-orchestrator if divergences exist, otherwise completeness-auditor]
```

# Rules

- Do NOT modify any artifact. This skill only reads and reports.
- Do NOT trust paper numbers as the source of truth. The source of truth is `frozen_numbers.json` → solution package → final result analysis → raw metrics, in that order.
- Do NOT silently skip a check because the source is missing — report it as "unauditable" so the user knows the gap.
- ALWAYS list ≥ 5 explicit pass items. If fewer than 5 things were checked, the audit did not run substantively — return status `not_run` and report what was missing.
- Each divergence MUST cite both the paper location and the source location with file:line precision.
- Each divergence MUST carry a `repair_skill` field — do not leave routing implicit.
- Do not classify a divergence as WARNING when the paper number is wrong — that is BLOCKING. WARNING is reserved for ambiguity or conventions (e.g., decimal precision drift within tolerance).
- Number comparison: tolerance is the precision the paper claims. Paper says `0.92` → tolerance is `±0.005`. Paper says `92%` → tolerance is `±0.5%`. Do not silently round.
- For figure file checks, verify on disk with the filesystem, not the figure-table plan. The plan is intent; the disk is truth.
- Cross-media is the keyword: a contradiction within a single file is `paper-polisher`'s job, not ours.

# Verification

Before returning the report, verify:

- The pass list has ≥ 5 explicit items, or the status is `not_run` with reason.
- Every divergence has paper location, source location, paper value, source value, severity, and repair skill.
- Every unauditable item names the missing source.
- The verdict (final assembly allowed) is consistent with the divergence list.
- The report is saved to `paper/audits/cross_media_consistency_audit.md` (create directory if missing).

# Failure modes

Stop and report a blocker if:

- The audit would require modifying any artifact to "fix" the divergence — that is not this skill's job.
- The user asks to suppress or silence a divergence without resolving it.
- The user asks to declare "passed" while blocking divergences exist.
- All source-of-truth tiers are missing for every subquestion (then there is nothing to audit against — recommend running `solution-package-builder` or `result-report-generator` first).

# Stop conditions

This skill must stop instead of guessing when:

- A paper claim cannot be matched to any source and cannot be classified as unauditable (rare — usually it's just missing source).
- A divergence's severity depends on intent that this skill cannot determine without asking the user.
- The user requests the audit to be re-run after a "fix" but no artifact has actually changed.

When stopping, output:
- the blocker
- which subquestion / claim is affected
- what source-of-truth file is needed
- recommended next skill

# Handoff

After producing the audit report:

- If the verdict is PASSED → hand off to `completeness-auditor`, then `quality-assurance-auditor`.
- If divergences exist → hand off to `workflow-orchestrator` with the divergence list and repair routing.

Do not hand off directly to final assembly even on PASSED — `quality-assurance-auditor` is still the gatekeeper.

# Relationship to the audit layer

This skill is one of three independent auditors. They run in this order before final assembly:

1. `consistency-auditor` (this skill) — cross-media facts match.
2. `completeness-auditor` — all required `*_review.md` / `*_audit.md` files exist with ≥ 5 pass items each.
3. `quality-assurance-auditor` — workflow completeness, three critical rules, anti-fabrication, paper quality.

Each is independent; each can fail. Any failure blocks final assembly. This separation exists so that no single skill can self-declare "完成" — the system requires three orthogonal checks to converge.

# Examples

## Example 1: All consistent

Input state: Q1 paper drafted; frozen_numbers.json exists; figures exist on disk; symbols defined.

Output: 8 pass items listed; 0 divergences; verdict `PASSED`; hand off to `completeness-auditor`.

## Example 2: Number drift

Input state: paper says "RMSE = 2.3"; `frozen_numbers.json` says "rmse: 2.41".

Output:
```
| 1 | BLOCKING | number | paper/sections/q2.tex:178 | results/Q2/reports/frozen_numbers.json | 2.3 | 2.41 | paper-section-writer |
```
Verdict: FAILED. Recommended repair: `paper-section-writer` updates the paper to `2.41` (since `frozen_numbers.json` is the canonical source).

## Example 3: Figure file missing

Input state: paper references `paper/figures/q3_route_plan.png`; file does not exist on disk.

Output:
```
| 1 | BLOCKING | file_ref | paper/sections/q3.tex:88 | filesystem | q3_route_plan.png | (missing) | math-figure-generator |
```
Verdict: FAILED. Recommended repair: regenerate the figure or update the reference.

## Example 4: Parameter drift after bug fix

Input state: bug fix changed `K` from 12 to 30 in `code/Q3/q3_main.py`; paper still says `K=12`; `frozen_numbers.json` was not re-frozen.

Output:
```
| 1 | BLOCKING | parameter | paper/sections/q3.tex:67 | code/Q3/q3_main.py:18 | K=12 | K=30 | python-code-reviewer |
| 2 | WARNING | stale_freeze | results/Q3/reports/frozen_numbers.json | code/Q3/q3_main.py | (frozen 2026-05-10) | (modified 2026-05-15) | solution-package-builder |
```
Verdict: FAILED. The frozen snapshot is stale — recommend re-freezing via `solution-package-builder` AFTER the modeler confirms `K=30` is the canonical value, then update the paper.

## Example 5: Unauditable subquestion

Input state: Q4 paper drafted; no `frozen_numbers.json`, no solution package, no final result analysis for Q4.

Output:
```
## Unauditable Items
| 1 | No source of truth for Q4 | All Q4 numerical claims (14 found) | Run solution-package-builder for Q4 first |
```
Verdict: `not_run` for Q4 (but other Qx audits can still pass). Recommended next: `workflow-orchestrator` to schedule `solution-package-builder` for Q4.
