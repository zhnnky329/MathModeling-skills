---
name: workflow-orchestrator
description: Manage the full mathematical modeling contest workflow and decide which skill should be used next.
license: MIT
---

# Purpose

Coordinate the full mathematical modeling contest workflow from problem intake to final QA.

This skill is a **gate-driven scheduler**, not a stage-sequential scheduler. The difference matters: a stage scheduler answers "what stage are we in, what's the next stage?" — which lets work advance even when the current stage's outputs are unreliable. A gate-driven scheduler answers "does the current stage's gate pass — and if not, what's the fallback?" — which prevents drift from propagating downstream.

This skill does not solve models, write code, generate figures, or draft paper sections directly. Its role is to inspect the current project state across ALL subquestions, track per-question progress through a defined state machine, identify missing or blocked artifacts, **evaluate each workflow gate against its enter_condition / pass_criteria / fail_fallback contract**, route to the independent audit layer (consistency-auditor + completeness-auditor + quality-assurance-auditor) before final assembly, and decide the next appropriate skill to use.

This skill is the single source of truth for "what should we do next?"

# Session-Start Environment Ping (MUST run first in any new session)

Before doing any orchestration work in a fresh session, ping the environment so downstream skills don't fail with surprises:

1. **Working tree status**: `git status --short`. If dirty (uncommitted changes, untracked files), surface the dirty files to the user before proceeding. Dirty working tree from a collaborator's in-progress work is the most common "git status looks weird" cause — flag it; do not silently work around it.
2. **Python availability**: `python --version` (or `python3 --version`). Flag if missing or wrong version.
3. **MATLAB / 北太天元 availability**: only when any Qx targets MATLAB. Check with `which matlab` or `command -v matlab`; if missing, report "MATLAB not in PATH — confirm 北太天元 will be used or switch implementation target to Python".
4. **Required scientific packages** (only when Python is the target): `python -c "import numpy, pandas, matplotlib"` — flag missing packages.
5. **Workspace skeleton**: verify `planning/`, `methods/`, `code/`, `results/`, `robustness/`, `paper/`, `workspace/data_raw/` exist (or create them with a single `mkdir -p` if the user just initialized the project).

Report the environment ping result in the very first response of a new session. **Do not start state-machine work** until the user has seen this report, since downstream skills will silently fail if the environment isn't there. A two-line summary is enough: "Env OK: Python 3.11, MATLAB found, working tree clean" or "Env WARN: MATLAB missing, working tree has 3 uncommitted files in code/Q2/".

# When to use

Use this skill:

- At the beginning of a new mathematical modeling contest task.
- After any major artifact is created, updated, or reviewed.
- When the user is unsure what to do next or asks "what's the status?"
- When the user asks specific status questions: "is Q1 ready for the writer?", "what's blocking Q3?", "which question can be handed to the paper writer?", "who should work on what?"
- Before generating code, writing paper text, assembling the final paper, or submitting results.
- When the workflow appears inconsistent, incomplete, or out of order.
- When a subquestion needs to be returned to the modeler for method revision.

# Preconditions

This skill can run with minimal context. At least one of the following should be available:

- A contest problem statement.
- A workspace directory.
- Existing workflow artifacts.
- A user-provided status update.
- A request to determine the next step.

If none of these exists, ask the user to provide the problem statement, workspace tree, or current progress summary.

# Inputs

Inspect or request the following, depending on availability:

- Problem statement or problem file location.
- Current workspace tree (all directories).
- Existing artifacts under:
  - `planning/` — global plan, problem parse, classification, symbol table, model assumptions, question dependency.
  - `methods/Q1/`, `methods/Q2/`, `methods/Q3/`, `methods/Q4/` — method candidates, iteration logs, final method explanations.
  - `code/Q1/`, `code/Q2/`, `code/Q3/`, `code/Q4/` — generated scripts.
  - `results/Q1/`, `results/Q2/`, `results/Q3/`, `results/Q4/` — experiment outputs, reports, final result analyses, solution packages.
  - `robustness/Q1/`, `robustness/Q2/`, `robustness/Q3/`, `robustness/Q4/` — robustness reports.
  - `paper/sections/` — drafted paper sections.
  - `paper/figures/` — final paper figures.
- Existing progress dashboard at `planning/progress_dashboard.md` (update if present).
- User constraints such as contest deadline, allowed tools, preferred language, or team role distribution.

# Workflow

1. Inspect the current task state ACROSS ALL SUBQUESTIONS.
   - Check each subquestion's artifacts independently — different subquestions may be at different stages.
   - Identify available files, user-provided context, and completed artifacts.
   - Do not assume that a stage is complete only because a later file exists.
   - Do not assume all subquestions are at the same stage.

2. Determine each subquestion's status using the per-question state machine (see below).

3. Enforce workflow gates (see "Workflow Gates" section below for the enter_condition / pass_criteria / fail_fallback contract of each gate).
   - Global gates (apply to all subquestions):
     - Do not allow method selection before problem parsing and classification.
     - Do not allow code generation before a validated method plan exists.
     - Do not allow paper claims before model results exist.
     - Do not allow final assembly before the three-auditor layer (consistency-auditor → completeness-auditor → quality-assurance-auditor) all pass.
   - Per-subquestion gates (the three critical rules):
     - Rule 1: Do not allow paper writing for Qx before `methods/Qx/qx_final_method_explanation.md` exists.
     - Rule 2: Do not allow writer handoff for Qx before `results/Qx/reports/qx_final_result_analysis.md` exists.
     - Rule 3: The paper writer should use `results/Qx/reports/qx_solution_package_for_writer.md` as primary source; if missing, Qx is NOT Ready for Writer.
   - **Gate failure propagation**: When any gate fails for Qx at stage N, mark all downstream Qx artifacts (stages > N) as DIRTY in the progress dashboard. Existing files at stages > N are not automatically valid just because they exist on disk — they may be downstream of a number that was wrong upstream.

4. Identify missing or blocked artifacts.
   - Mark missing files explicitly.
   - Mark blocked steps separately from merely incomplete steps.
   - If the blocker is user-side information, state exactly what is needed.
   - Per-subquestion blocking reasons must be specific (e.g., "Q2 needs method revision because round 2 experiment report shows M2 constraint violation").

5. Select the next skill.
   - Choose exactly one primary next skill.
   - Provide a short reason for the choice.
   - Provide concrete next actions for the user or agent.
   - If multiple subquestions need work, prioritize by dependency order (Q1 before Q2 if Q2 depends on Q1).

6. Update or produce the progress dashboard.
   - Save to `planning/progress_dashboard.md`.
   - Keep it up to date with current subquestion statuses.

7. Return a workflow state report.
   - Include the progress dashboard.
   - Include next skill recommendation.
   - Do not perform the downstream skill's work inside this skill.

# Workflow Gates (enter_condition / pass_criteria / fail_fallback)

Each gate is a hard checkpoint with three explicit parts. Do not skip a gate; do not advance on partial satisfaction. The state machine and the gates run together — the state machine says "what stage am I in", the gates say "can I leave this stage".

## Gate G1: PROBLEM_PARSED
- **enter_condition**: User provides a problem statement (file or text).
- **pass_criteria**:
  - Mechanical: `planning/parse/` exists (goals / objects / constraints / data / outputs / subquestions filled); `planning/classification/` exists with an `ai_suggested_type` per Qx.
  - Human (B-layer sentinel sweep): no surviving `[MODELER INPUT NEEDED` / `[AI-DRAFT` sentinel in the load-bearing judgment fields — per Qx the `evaluation_criteria` (the success rubric, problem-parser), the `modeler_chosen_type` + `framing_rationale` (problem-classifier), and any proposed causal/conservation `relationships`. A surviving sentinel means the human hasn't confirmed the framing → G1 not passed.
- **fail_fallback**: Mechanical gaps → `problem-parser` / `problem-classifier`. Surviving sentinels → route back to the modeler (not a skill) to supply the rubric / confirm the type. Do not advance to G2; the orchestrator never fills these fields itself.

## Gate G2: METHOD_VALIDATED  (load-bearing — most-violated boundary)
This is the method→code boundary. Most "漂亮方案到代码阶段才崩" issues happen because G2 was treated as soft.
- **enter_condition**: G1 passed; `data-auditor-cleaner` ran; `planning/symbol_table.md` and `planning/model_assumptions.md` exist.
- **pass_criteria**:
  - `methods/Qx/qx_method_candidates.md` exists with 2-4 candidates.
  - Every candidate has a runnable ≤30-line PoC script saved under `methods/Qx/poc/` AND a small-scale feasibility result (a number, a runtime, or a "fails on this data" verdict). A candidate without a PoC counts as "not yet validated".
  - Every candidate has a baseline designation or one of the candidates IS the baseline.
- **fail_fallback**: Route to `method-selector` to add the missing PoC. If PoC feasibility fails for a candidate, mark it `[REJECTED]`, move the PoC script to `workspace/archived/`, and route back to `method-selector` for an alternative.

## Gate G2.5: METHOD_CHOSEN_BY_HUMAN  (NEW — human-decision gate at the method→code boundary)
PoC proves a method is *feasible*; it does not prove it is the *right* choice. "Which method, and why, over the alternatives" is the single most graded modeling judgment — the AI must not make it. This is the pilot of the Human Decision Artifact Convention (see CLAUDE.md). It is a **two-layer gate**: the mechanical layer is G2 (above); this is its human layer.
- **enter_condition**: G2 passed — candidates carry `[CANDIDATE — PoC PASS]`, no `[CHOSEN]` yet; PoC failures already archived.
- **pass_criteria** (all checked mechanically against the decision artifact, no NLP needed):
  - `methods/Qx/decisions/method-selector_modeler_decision.md` exists with `status: DECIDED` and `decided_by: human`.
  - `choice` names a real `[CANDIDATE]` id from the pool.
  - Every `rejected_alternatives[*].reason` and the `## Modeler's rationale` body are non-empty, over the char floor, and contain no sentinel (`<<<`, `TODO`, `待补充`, `...`, empty).
  - The rationale is NOT a near-verbatim copy of `ai_suggestion` (normalized-whitespace equality / tiny edit distance; fuzzy similarity is a ledger WARN, not a gate FAIL — see CLAUDE.md).
  - The rationale references at least one concrete token from `evidence_refs` (a number, a candidate id, a symbol).
- **fail_fallback**: keep `code_generation_allowed_Qx = false`. Route back to the modeler (NOT to a skill) with the exact missing/under-floor field. **The orchestrator must never set this gate's pass itself, never auto-fill the decision artifact, and never infer the choice from `method-selector`'s `ai_suggestion`.**
- **encoding**: `code_generation_allowed_Qx = G2_mechanical_pass ∧ G2.5_human_pass`. `model-code-analyzer` and the code generators stay blocked until both are true. While blocked, the AI MAY run non-judgment prep (data cleaning, staging) — it just cannot generate the model code.

## Gate G3: CODE_REVIEWED
- **enter_condition**: G2 passed; `code/Qx/` (Python) or `code/matlab/Qx/` (MATLAB) has scripts; experiments ran.
- **pass_criteria**:
  - Code-reviewer artifact exists at `code/Qx/reviews/qx_python_review.md` or `code/matlab/Qx/reviews/qx_matlab_review.md` with ≥ 5 explicit pass items.
  - Scripts produced `results/Qx/experiments/roundN/` with `run_summary.json` and at least one figures/tables/metrics file.
- **fail_fallback**: Route to `<lang>-code-reviewer`. If the review is insufficient (< 5 pass items), route back to the same reviewer with `completeness-auditor`'s gap report attached.

## Gate G4.5: RESULTS_JUDGED_BY_HUMAN  (NEW — human-decision gate at the experiments→freeze boundary)
The result verdict (`[CHOSEN]/[REJECTED]`, "is the result good", confidence) and the stability verdict are graded modeling judgments. Freezing them makes an AI judgment permanently canonical — so the human verdict must land BEFORE the freeze, not after. This is the second human-decision gate (the second `★`); its mechanical layer is G3 + the experiment loop above.
- **enter_condition**: G3 passed; `results/Qx/experiments/roundN/` reports exist with per-method evidence; experiment-report verdict tags are `[PENDING-MODELER]` (the AI may annotate `[AI-SUGGESTED]`, visibly non-binding).
- **pass_criteria** (all checked mechanically against the decision artifacts / decision log):
  - `methods/Qx/decisions/result-report-generator_modeler_decision.md` is `DECIDED` (`decision_id: qx_result_verdict`): per-method `choice ∈ {CHOSEN,BACKUP,REJECTED}` + rationale tied to a criterion; `round_decision ∈ {proceed,iterate,return}`; `confidence` per top-line claim with a rationale that **cites a specific computed number**.
  - `methods/Qx/decisions/robustness-checker_modeler_decision.md` is `DECIDED` (`decision_id: qx_stability_verdict`): stability `confidence` + rationale **citing a number from the robustness report**.
  - `methods/Qx/decisions/final-method-explainer_modeler_decision.md` is `DECIDED` (`decision_id: qx_method_explanation`): per-assumption necessity ∈ {necessary,simplifying}; the why-this-method narrative is transcribed from the decision log, not re-authored.
  - Each artifact passes the standard human-layer checks (DECIDED + decided_by:human + over floor + no sentinel + not a near-verbatim copy of `ai_suggestion` + evidence-citation).
- **fail_fallback**: keep `freeze_allowed_Qx = false`; `solution-package-builder` refuses to emit `frozen_numbers.json`. `[REJECTED]` archival fires **only** for human-tagged rejections, never an AI label. Route back to the modeler (not a skill) with the missing/under-floor field. The orchestrator must never fill these artifacts or infer a verdict from an `ai_suggestion`.
- **encoding**: `freeze_allowed_Qx = G3_mechanical_pass ∧ G4.5_human_pass`. The freeze (G4 below) cannot fire until both are true.

## Gate G4: RESULTS_FROZEN  (load-bearing — second-most-violated boundary)
This is the results→paper boundary. Most "论文里数字与最新 results 错位" issues happen because G4 was treated as soft. **G4 now requires G4.5 to have passed** (the human verdicts must exist before the freeze) plus the package sign-off.
- **enter_condition**: G4.5 passed (`freeze_allowed_Qx = true`); `results/Qx/reports/qx_final_result_analysis.md` exists.
- **pass_criteria**:
  - `methods/Qx/decisions/solution-package-builder_modeler_decision.md` is `DECIDED` (`decision_id: qx_package_signoff`): per-flagged-claim `approve ∈ {keep,downgrade,drop}` + package confidence confirmed/overridden by the human.
  - `results/Qx/reports/frozen_numbers.json` exists with a `frozen_at` timestamp.
  - `frozen_numbers.json` is newer than the last modification time of every `code/Qx/` file it references (no stale freeze).
  - `results/Qx/reports/qx_solution_package_for_writer.md` exists; every numerical claim in it is sourced from `frozen_numbers.json`; every "why we chose X" sentence traces to a `decision_id` in `methods/Qx/qx_decision_log.md`.
- **fail_fallback**: If the package sign-off is missing/PENDING, build the human-readable package but DO NOT emit `frozen_numbers.json` — route back to the modeler for sign-off. After freeze, if `consistency-auditor` later detects drift, route to the **解冻 → 修改 → 重冻结** three-step:
  1. Modeler/programmer confirms which value is now canonical.
  2. Update the canonical source (code or analysis report).
  3. Re-run `solution-package-builder` to re-freeze. Do not edit `frozen_numbers.json` by hand.

## Gate G5: PAPER_SECTION_READY
- **enter_condition**: G4 passed; `paper/sections/qx.tex` exists.
- **pass_criteria**:
  - Mechanical: section meets the word-count floor (per section type); every numerical result has ≥ 3 discussion dimensions covered; every figure exists on disk and passed `math-figure-generator`'s render-check.
  - Human (B-layer): the **physical-meaning** discussion dimension is human-authored — its `[MODELER INPUT NEEDED]` sentinel has been replaced; a surviving sentinel means that dimension does NOT count toward the ≥3 floor. The three paper seeds (`key_result_claim`, `contribution_claim`, `why_this_method`) are filled (no surviving sentinel), and `why_this_method` carries a `<!-- from Qx-D0n -->` provenance marker tracing to the decision log. Every Type 3 figure's `core_claim` is human-confirmed (no surviving sentinel).
- **fail_fallback**: Missing dimensions / under floor → `paper-section-writer`. Surviving sentinel in physical-meaning or a paper seed → route back to the modeler. Figures failing render-check or with an unconfirmed `core_claim` → `math-figure-generator` (render) / `figure-table-planner` (claim).

## Gate G6: AUDIT_LAYER_PASSED  (the final gate before assembly)
This is the independent-audit gate. No single skill's "完成" claim can bypass it.
- **enter_condition**: G5 passed for all Qx; paper sections drafted; references managed.
- **pass_criteria** (all three independent audits must PASS):
  - `paper/audits/cross_media_consistency_audit.md` — verdict PASSED.
  - `paper/audits/completeness_audit.md` — verdict PASSED.
  - `paper/qa_report.md` — verdict PASSED.
- **fail_fallback**: Route to whichever auditor failed. Never approve `final_assembly_allowed=true` on partial audit. The three auditors are orthogonal — passing one does not imply the others.

## Gate dependency graph

```
G1 → G2 → G2.5★ → G3 → [experiments] → G4.5★ → G4 → G5 → G6 → final assembly
          (human)                       (human)            ↑
                                                           consistency-auditor ┐
                                                           completeness-auditor├─ all must PASS
                                                           quality-assurance-auditor ┘
```

★ = human-decision gate. Two of them sit at the two load-bearing boundaries: **G2.5** (method→code) blocks `code_generation_allowed_Qx` until the modeler commits the method choice; **G4.5** (experiments→freeze) blocks `freeze_allowed_Qx` until the modeler renders the result + stability verdicts — so the freeze never fossilizes an AI judgment. The mechanical gates (G1–G6) stay AI-owned; each human gate adds a separate file-existence-and-content check, enforced the same way as `≥5-pass-item` checks.

**The orchestrator never sets a human-gate pass itself.** It never fills a decision artifact, never infers a human verdict from an AI suggestion, and treats a missing/PENDING/under-floor decision artifact exactly like a missing mechanical artifact: the downstream `*_allowed` flag stays false.

A failure at any gate marks all downstream stages DIRTY. Re-passing a gate after repair requires re-running the gate's pass_criteria check from scratch, not trusting cached "✅" marks. After a human-gate FAIL, recovery is: the modeler edits the decision artifact → `status` flips to DECIDED → next orchestrator run re-checks the file → on pass, the human sub-flag flips true; downstream DIRTY clears only after `consistency-auditor` re-runs incrementally (Change-propagation rule P1).

# Per-Question State Machine

Each subquestion Qx moves through these states in order. The state is determined by which artifacts exist.

```
[01] Method Candidates Drafted
      → methods/Qx/qx_method_candidates.md exists
      ↓
[02] Code Implementation In Progress
      → code/Qx/ has scripts, experiment not yet run or running
      ↓
[03] Experiment Report Ready (Round N)
      → results/Qx/experiments/roundN/qx_experiment_report_roundN.md exists
      ↓  (may loop back to [01] or [02] if method revision needed)
[04] Needs Method Revision
      → experiment report indicates issues; loop back to modeler
      ↓  (after revision, return to [02] or [03])
[05] Final Method Selected
      → modeler has confirmed final method choice
      ↓
[06] Final Method Explained
      → methods/Qx/qx_final_method_explanation.md exists
      ↓
[07] Final Result Analyzed
      → results/Qx/reports/qx_final_result_analysis.md exists
      ↓
[08] Solution Package Built
      → results/Qx/reports/qx_solution_package_for_writer.md exists
      ↓
[09] Ready for Writer
      → all [06], [07], [08] exist; writer can start
      ↓
[10] Writer Draft Ready
      → paper/sections/qx.tex or equivalent exists
      ↓
[11] Reviewed by Modeler
      → modeler confirms paper's model description matches final method
      ↓
[12] Reviewed by Programmer
      → programmer confirms paper's results and figures match outputs
      ↓
[13] Finalized
      → all reviews passed; ready for final assembly
```

The orchestrator determines which state each subquestion is in by checking which files exist and reading the latest experiment report verdicts.

# Progress Dashboard

Maintain this dashboard at `planning/progress_dashboard.md`.

The dashboard MUST be a Markdown table tracking all subquestions:

```markdown
# Project Progress Dashboard

> Last updated: [timestamp]

## Overall Status

| Stage | Q1 | Q2 | Q3 | Q4 |
|-------|----|----|----|-----|
| Method Candidates Drafted | ✅ | ✅ | ✅ | ❌ |
| Experiment Report Ready | ✅ (R2) | ✅ (R1) | ❌ | ❌ |
| Final Method Selected | ✅ | ❌ | ❌ | ❌ |
| Final Method Explained | ✅ | ❌ | ❌ | ❌ |
| Final Result Analyzed | ✅ | ❌ | ❌ | ❌ |
| Solution Package Built | ⏳ | ❌ | ❌ | ❌ |
| Ready for Writer | ⏳ | ❌ | ❌ | ❌ |
| Writer Draft Ready | ❌ | ❌ | ❌ | ❌ |
| Reviewed by Modeler | ❌ | ❌ | ❌ | ❌ |
| Reviewed by Programmer | ❌ | ❌ | ❌ | ❌ |
| **Finalized** | ❌ | ❌ | ❌ | ❌ |

## Current Status Summary

| Subquestion | Status | Blocked By | Next Action |
|-------------|--------|------------|-------------|
| Q1 | Solution Package in Progress | — | Run solution-package-builder |
| Q2 | Needs Method Revision | M2 constraint violation in R1 | Modeler to fix constraints, then re-run |
| Q3 | Not Started | Waiting on Q1 results (input dependency) | — |
| Q4 | Not Started | Global planning incomplete | Run problem-parser and classifier first |

## Blockers

| Blocker | Affects | Severity | Resolution |
|---------|---------|----------|------------|
| Q2 M2 infeasible | Q2 finalization | High | Modeler revises constraint formulation |
| Q4 not parsed | Q4 start | High | Run problem-parser for all subquestions |

## Global Artifact Status

| Artifact | Status | Path |
|----------|--------|------|
| Problem Parse | ✅ | planning/parse/ |
| Problem Classification | ✅ | planning/classification/ |
| Global Symbol Table | ✅ | planning/symbol_table.md |
| Model Assumptions (Global) | ⏳ | planning/model_assumptions.md |
| Question Dependency Map | ✅ | planning/question_dependency.md |
| Related Paper Analysis | ✅ | workspace/papers/related_paper_analysis.md |
| Data Report | ✅ | workspace/data/data_report.md |

## Three Critical Rules Check

| Rule | Q1 | Q2 | Q3 | Q4 |
|------|----|----|----|-----|
| 1: Final method explanation exists before paper writing | ✅ | ❌ | ❌ | ❌ |
| 2: Final result analysis exists before writer handoff | ✅ | ❌ | ❌ | ❌ |
| 3: Solution package exists as writer's primary source | ⏳ | ❌ | ❌ | ❌ |

## Recommended Next Skill

- **Skill**: `solution-package-builder` for Q1
- **Reason**: Q1 has both final method explanation and final result analysis; solution package is the next prerequisite for writer handoff.
- **Runners-up** (if Q1 is already assigned):
  - `method-selector` for Q2 revision (after modeler fixes M2)
  - `problem-parser` for Q4
```

# Expanded Workflow Stages (Global)

The full global workflow now includes per-subquestion iteration loops:

```
【0】全题启动阶段 (Global Setup)
problem-parser → problem-classifier → related-paper-analyzer
    → global symbol table → global model assumptions → question dependency map
    ↓
【1】候选方法池阶段 (Per-Question Start)
method-selector → methods/Qx/qx_method_candidates.md
    ↓
【2】编程实验阶段 (Per-Question, Multi-Round)
model-code-analyzer → python/matlab-model-code-generator → code-reviewer
    → results/Qx/experiments/roundN/
    ↓
【3】实验报告阶段 (Per-Question, Per-Round)
result-report-generator → results/Qx/experiments/roundN/qx_experiment_report_roundN.md
    ↓
【4】方法迭代循环 (Per-Question Loop)
    ← modeler reviews report → revises methods → back to 【2】
    OR → proceed to 【5】
    ↓
【5】最终方法锁定
final-method-explainer → methods/Qx/qx_final_method_explanation.md
    ↓
【6】最终结果分析
result-report-generator (final mode) → results/Qx/reports/qx_final_result_analysis.md
    ↓
【7】稳健性分析
robustness-checker → robustness/Qx/qx_robustness_report.md
    ↓
【8】论文材料包
solution-package-builder → results/Qx/reports/qx_solution_package_for_writer.md
    ↓
【9】图表规划
figure-table-planner → paper/figures/ planning
    ↓
【10】论文写作 (Per-Question)
paper-section-writer → paper/sections/qx.tex
    ↓
【11】建模手审核 → 【12】编程手审核
    ↓
【13】独立审计层 (NEW — three orthogonal audits, all must PASS to advance)
  ├─ consistency-auditor   → paper/audits/cross_media_consistency_audit.md
  ├─ completeness-auditor  → paper/audits/completeness_audit.md
  └─ quality-assurance-auditor → paper/qa_report.md
    ↓ (only if all three PASS — Gate G6)
【14】终稿组装
Final assembly of main.tex + sections + figures → paper/final.pdf

If any of the three audits FAIL:
  → route to the failed auditor's recommended repair skill
  → re-run the failed audit after repair
  → never advance to 【14】 on partial audit
```

# The Three Critical Rules (Enforced Here)

These rules are the orchestrator's primary enforcement responsibility:

## Rule 1: No final paper writing without final method explanation

`paper-section-writer` MUST NOT write final paper sections for Qx based only on `qx_method_candidates.md` or early method plans. The orchestrator checks that `methods/Qx/qx_final_method_explanation.md` exists before routing Qx to the paper writer.

If a user asks to write Qx paper but this file is missing, the orchestrator blocks and routes to `final-method-explainer` instead.

## Rule 2: No writer handoff without final result analysis

Program execution outputs alone are NOT sufficient for writer handoff. The orchestrator checks that `results/Qx/reports/qx_final_result_analysis.md` exists before marking Qx as Ready for Writer.

If a user says "Qx is done, write the paper" but only raw results exist (no analysis report), the orchestrator blocks and routes to `result-report-generator` instead.

## Rule 3: Writer reads from the solution package, not scattered results

The paper writer's primary source for Qx is `results/Qx/reports/qx_solution_package_for_writer.md`. The orchestrator checks that this file exists before routing Qx to the paper writer.

If it is missing, the orchestrator blocks and routes to `solution-package-builder`.

# Status Query Responses

The orchestrator should be able to answer these questions precisely:

- **"Q1 现在卡在哪？"** → State the exact status (e.g., "Q1 is at state [08] Solution Package Built — waiting for solution-package-builder. It needs: nothing. It is blocked by: nothing.")
- **"哪个小问可以交给论文手？"** → List subquestions at state [09] Ready for Writer (e.g., "None yet. Q1 is closest at [08] — one step away.")
- **"哪个小问缺最终方法详解？"** → List subquestions at state [05] or earlier (e.g., "Q2, Q3, Q4 are missing final method explanations. Q2 is at [04] Needs Method Revision.")
- **"哪个小问只有结果没有解释？"** → List subquestions with results but no analysis report (e.g., "Q3 has raw results in results/Q3/experiments/round1/ but no analysis report.")
- **"哪个小问需要退回建模手？"** → List subquestions at state [04] Needs Method Revision (e.g., "Q2 needs method revision — M2 constraint violation.")

# Outputs

Produce a workflow state report containing:

- `current_global_stage`
- `progress_dashboard` (link to or contents of `planning/progress_dashboard.md`)
- `per_question_status` (state machine state for each Qx)
- `completed_artifacts`
- `missing_artifacts`
- `blocked_items` (global and per-question)
- `workflow_gates` (global and per-question)
- `three_critical_rules_check`
- `next_skill`
- `next_actions`
- `handoff_context`
- `runners_up` (alternative next skills if the primary is already in progress)

# Output format

Prefer this JSON-compatible structure:

```json
{
  "current_global_stage": "per_question_iteration",
  "progress_dashboard_path": "planning/progress_dashboard.md",
  "per_question_status": {
    "Q1": {
      "state": "08_solution_package_built",
      "state_label": "Solution Package Built",
      "ready_for_writer": false,
      "blocked": false,
      "blocked_reason": null,
      "missing_for_next_state": [
        "paper/sections/q1.tex"
      ]
    },
    "Q2": {
      "state": "04_needs_method_revision",
      "state_label": "Needs Method Revision",
      "ready_for_writer": false,
      "blocked": true,
      "blocked_reason": "Round 1 experiment shows M2 constraint violation. Modeler must revise constraint formulation.",
      "missing_for_next_state": [
        "Revised method from modeler"
      ]
    },
    "Q4": {
      "state": "00_not_started",
      "state_label": "Not Started",
      "ready_for_writer": false,
      "blocked": false,
      "blocked_reason": null,
      "missing_for_next_state": [
        "Problem parse (all subquestions)",
        "Problem classification (all subquestions)",
        "methods/Q4/q4_method_candidates.md"
      ]
    }
  },
  "global_completed_artifacts": {
    "problem_parse": true,
    "problem_classification": true,
    "related_paper_analysis": true,
    "global_symbol_table": true,
    "global_model_assumptions": false,
    "question_dependency_map": true,
    "data_report": true,
    "cleaned_data": true
  },
  "per_question_completed_artifacts": {
    "Q1": {
      "method_candidates": true,
      "method_iteration_log": true,
      "experiment_report_round1": true,
      "experiment_report_round2": true,
      "final_method_explanation": true,
      "final_result_analysis": true,
      "solution_package": true,
      "robustness_report": true,
      "paper_draft": false,
      "figure_table_plan": true
    }
  },
  "blocked_items": [
    {
      "scope": "Q2",
      "item": "final_method_explanation",
      "reason": "Modeler has not confirmed final method. Round 1 experiment showed M2 constraint violation.",
      "resolution": "Modeler revises constraint formulation, then re-run code for M2."
    }
  ],
  "three_critical_rules_check": {
    "Q1": {
      "rule1_method_explanation_exists": true,
      "rule2_result_analysis_exists": true,
      "rule3_solution_package_exists": true,
      "ready_for_writer": true
    },
    "Q2": {
      "rule1_method_explanation_exists": false,
      "rule2_result_analysis_exists": false,
      "rule3_solution_package_exists": false,
      "ready_for_writer": false
    }
  },
  "workflow_gates": {
    "global": {
      "method_selection_allowed": true,
      "code_generation_allowed_Q1": true,
      "code_generation_allowed_Q2": true,
      "paper_writing_allowed_Q1": true,
      "paper_writing_allowed_Q2": false,
      "final_assembly_allowed": false
    }
  },
  "next_skill": "paper-section-writer",
  "next_actions": [
    "Write paper/sections/q1.tex using results/Q1/reports/q1_solution_package_for_writer.md as primary source.",
    "Reference figures from results/Q1/experiments/final/figures/."
  ],
  "runners_up": [
    {
      "skill": "workflow-orchestrator",
      "action": "Return Q2 to modeler for constraint revision."
    }
  ],
  "handoff_context": {
    "reason": "Q1 is Ready for Writer (all three critical rules satisfied).",
    "required_inputs_for_next_skill": [
      "results/Q1/reports/q1_solution_package_for_writer.md",
      "results/Q1/experiments/final/figures/",
      "robustness/Q1/q1_robustness_report.md"
    ]
  }
}
```

If a JSON block is too rigid for the situation, use a concise Markdown report with the same fields.

# Rules

- Do not solve the mathematical model.
- Do not select specific algorithms unless the next step is only to route to `method-selector`.
- Do not write code.
- Do not draft paper sections.
- Do not fabricate missing artifacts.
- Do not infer completion without evidence.
- Do not skip workflow gates for speed.
- Do not approve final delivery without the full audit layer passing (Gate G6 — consistency + completeness + QA all green).
- Do not treat any one auditor's "✅" as sufficient for assembly — the three are orthogonal.
- Run the session-start environment ping in every new session before doing anything else.
- **Never set a human-decision gate's pass yourself** (G2.5 is the first such gate). Never fill, edit, or auto-populate a `*_modeler_decision.md` artifact; never infer a human's method choice from the AI's `ai_suggestion`. A PENDING or under-floor decision artifact blocks the downstream `*_allowed` flag exactly like a missing mechanical artifact.
- Enforce the three critical rules at every handoff.
- Track per-question status separately — different subquestions are at different stages.
- Update the progress dashboard whenever the state changes.
- Keep recommendations tied to traceable artifacts.
- Prefer one clear next step over many speculative branches.
- If a subquestion is blocked, state exactly what needs to happen to unblock it.
- If the modeler or programmer needs to act, be specific about what they need to do.

# Verification

Before handing off, verify:

- The chosen `next_skill` matches the earliest incomplete required stage for the highest-priority subquestion.
- No workflow gate is bypassed (global or per-question).
- The three critical rules are checked for the target subquestion.
- Missing artifacts are explicitly listed.
- Blocked items are separated from ordinary incomplete items.
- The next actions are concrete enough to execute.
- The handoff context includes the minimum inputs needed by the next skill.
- The progress dashboard reflects the current state (update if needed).

# Failure modes

Stop and report a blocker if:

- The problem statement is missing.
- The user asks to generate code but no method plan exists.
- The user asks to write numerical conclusions but no model results exist.
- The user asks to assemble or submit the final paper before QA passes.
- The user asks to write Qx paper but `qx_final_method_explanation.md` is missing (Rule 1).
- The user asks to hand Qx to writer but `qx_final_result_analysis.md` is missing (Rule 2).
- The user asks to write Qx paper but `qx_solution_package_for_writer.md` is missing and the package cannot be assembled from available artifacts (Rule 3).
- The workspace state is inconsistent, such as paper claims existing without corresponding results.
- Multiple incompatible interpretations of the current task exist and the choice affects workflow order.
- A subquestion dependency is violated (e.g., Q2 code references Q1 results that don't exist).

# Stop conditions

This skill must stop instead of guessing when:

- Required artifacts cannot be located.
- The current stage cannot be determined from available context.
- A downstream skill would need fabricated data, fabricated results, or unsupported assumptions.
- The user request conflicts with the workflow gates or the three critical rules.
- The per-question state cannot be determined because artifacts are missing and the user cannot clarify.

When stopping, output:

- the blocker
- why it matters
- the minimum information or artifact needed to continue
- which subquestion is affected
- the recommended next skill once the blocker is resolved

# Handoff

Typical handoff order (global, then per-question):

1. `problem-parser`
2. `problem-classifier`
3. `related-paper-analyzer`
4. **Create global symbol table, model assumptions, dependency map** (planning stage)
5. `method-selector` (per Qx — can run in parallel for independent subquestions)
6. `model-code-analyzer`
7. `python-model-code-generator` or `matlab-model-code-generator`
8. `code-reviewer`
9. `result-report-generator` (round N experiment report)
10. **Loop back to 5 or 6** if method revision needed
11. `result-report-generator` (final result analysis, when method is locked)
12. `final-method-explainer`
13. `robustness-checker`
14. `figure-table-planner`
15. `solution-package-builder`
16. `paper-section-writer`
17. **Modeler review → Programmer review**
18. `reference-manager` (verify citations are real)
19. `paper-polisher` (style / hedging / formula consistency within paper)
20. **Independent audit layer (Gate G6 — three orthogonal audits, all must PASS):**
    - `consistency-auditor` (cross-media numbers / files / symbols / parameters)
    - `completeness-auditor` (every claimed completion has a substantive artifact on disk)
    - `quality-assurance-auditor` (workflow completeness + three critical rules + anti-fabrication + paper quality)
21. Back to `workflow-orchestrator` for final assembly (only when Gate G6 passes)

If the workflow is complete and **all three audits pass**, hand off to final assembly or user review. A single auditor "✅" is NOT sufficient — the three are orthogonal and must converge.

# Examples

## Example 1: New contest problem

Input state:
- Problem PDF exists.
- No parsed problem exists.

Output:
```json
{
  "current_global_stage": "global_setup",
  "next_skill": "problem-parser",
  "next_actions": [
    "Extract goals, objects, constraints, data, outputs, and subquestions.",
    "Save parsed result under planning/parse/."
  ]
}
```

## Example 2: User asks to generate code too early

Input state:
- Problem has been parsed.
- Problem has not been classified.
- Method plan does not exist.
- User asks for modeling code.

Output:
```json
{
  "current_global_stage": "global_setup",
  "blocked_items": [
    "Code generation is blocked because no validated method plan exists."
  ],
  "next_skill": "problem-classifier",
  "next_actions": [
    "Classify each subquestion before literature analysis and method selection.",
    "Then hand off to related-paper-analyzer, then method-selector."
  ]
}
```

## Example 3: Q1 is Ready for Writer

Input state:
- Q1: `methods/Q1/q1_final_method_explanation.md` exists.
- Q1: `results/Q1/reports/q1_final_result_analysis.md` exists.
- Q1: `results/Q1/reports/q1_solution_package_for_writer.md` exists.
- User asks "what's next?"

Output:
```json
{
  "per_question_status": {
    "Q1": {
      "state": "09_ready_for_writer",
      "state_label": "Ready for Writer",
      "ready_for_writer": true
    }
  },
  "three_critical_rules_check": {
    "Q1": {
      "rule1_method_explanation_exists": true,
      "rule2_result_analysis_exists": true,
      "rule3_solution_package_exists": true,
      "ready_for_writer": true
    }
  },
  "next_skill": "paper-section-writer",
  "next_actions": [
    "Write paper/sections/q1.tex using results/Q1/reports/q1_solution_package_for_writer.md as primary source."
  ],
  "handoff_context": {
    "reason": "Q1 satisfies all three critical rules. Writer can proceed with the solution package.",
    "required_inputs_for_next_skill": [
      "results/Q1/reports/q1_solution_package_for_writer.md"
    ]
  }
}
```

## Example 4: Q2 needs method revision (Rule 1 violation)

Input state:
- Q2 has experiment report round 1.
- Experiment report says M2 produces infeasible output.
- User says "let's just write the Q2 paper anyway."

Output:
```json
{
  "blocked_items": [
    "CRITICAL RULE 1 VIOLATION: Q2 paper writing is blocked because methods/Q2/q2_final_method_explanation.md does not exist. The experiment report indicates M2 is infeasible — the modeler must revise the method before a final method can be explained."
  ],
  "per_question_status": {
    "Q2": {
      "state": "04_needs_method_revision",
      "state_label": "Needs Method Revision",
      "ready_for_writer": false,
      "blocked_reason": "M2 constraint violation in round 1. Modeler must fix constraint formulation or select a different candidate method."
    }
  },
  "next_skill": "method-selector",
  "next_actions": [
    "Modeler: revise Q2 constraint formulation for M2, or select a different candidate method from the pool.",
    "After revision: regenerate code and run round 2 experiments.",
    "Do NOT start paper writing until final method is confirmed and explained."
  ]
}
```

## Example 5: User asks "which question can be handed to the paper writer?"

Input state:
- Q1: Solution package exists. Not yet drafted.
- Q2: Final method explanation exists but no final result analysis.
- Q3: Only method candidates drafted.
- Q4: Not started.

Output:
```json
{
  "query_response": "Q1 is ready for the paper writer. Q2, Q3, Q4 are not ready.",
  "ready_for_writer": ["Q1"],
  "almost_ready": [],
  "not_ready": {
    "Q2": "Missing final result analysis (Rule 2). Programmer must run final experiments and produce results/Q2/reports/q2_final_result_analysis.md.",
    "Q3": "Only at candidate method stage. Need experiments, method selection, method explanation, result analysis, and solution package.",
    "Q4": "Not started — needs problem parsing and classification first."
  },
  "next_skill": "paper-section-writer",
  "next_actions": [
    "Write paper/sections/q1.tex for Q1 (only subquestion Ready for Writer).",
    "Meanwhile: Q2 programmer should produce final result analysis."
  ]
}
```

## Example 6: User asks to assemble final paper before QA

Input state:
- Paper sections exist for all subquestions.
- QA report does not exist.

Output:
```json
{
  "current_global_stage": "quality_assurance",
  "blocked_items": [
    "Final assembly is blocked because QA has not passed."
  ],
  "next_skill": "quality-assurance-auditor",
  "next_actions": [
    "Audit problem coverage, model-result consistency, figure references, robustness checks, unsupported claims, and workflow completeness."
  ]
}
```

## Example 7: Progress dashboard update

Input state:
- After completing Q1 solution package, the orchestrator is invoked.

Output:
- Updated `planning/progress_dashboard.md` with:
  - Q1 state changed to [08] Solution Package Built.
  - Next recommended skill: `paper-section-writer` for Q1.
  - Three critical rules check updated for Q1 (all three ✅).
  - Q2, Q3, Q4 statuses unchanged.
