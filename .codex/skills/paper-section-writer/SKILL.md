---
name: paper-section-writer
description: Write mathematical modeling paper sections based only on available problem analysis, model plans, results, figures, and robustness reports.
license: MIT
---

# Purpose

Write mathematical modeling paper sections from validated workflow artifacts.

This skill turns the final method explanation, final result analysis, solution package, and figure-table plan into structured paper section drafts. It must keep every claim traceable to an artifact and must not invent data, numerical results, figures, references, or unsupported conclusions.

**CRITICAL**: This skill is gated. It MUST NOT write final paper sections for a subquestion unless all three prerequisites are met (see "Three Critical Rules" below). If prerequisites are missing, this skill must refuse and redirect to the appropriate upstream skill.

This skill does not run models, generate new results, create unsupported figures, perform final QA, or approve final submission.

# When to use

Use this skill:

- After `solution-package-builder` has produced the solution package for a subquestion.
- After `figure-table-planner` has produced the figure-table plan.
- When all three critical rule prerequisites are met for the target subquestion.
- When paper section drafts are needed.
- When existing section drafts need to be aligned with validated artifacts.
- Before `quality-assurance-auditor`.

Do NOT use this skill:
- To write final paper sections for Qx when `methods/Qx/qx_final_method_explanation.md` is missing.
- To write final paper sections for Qx when `results/Qx/reports/qx_final_result_analysis.md` is missing.
- To write final paper sections for Qx when `results/QX/reports/qx_solution_package_for_writer.md` is missing (the writer's primary source).

# Gate G5: Section Quality (NEW — load-bearing for paper external quality)

Beyond the three critical rules (which ensure the right inputs exist), every section drafted by this skill must also pass two output-quality gates before it counts as "drafted". Marketers of completion always claim "已经写完了"; this gate makes "写完" structurally checkable.

## G5.1 Word-count floor (per section type)

Different sections have different minimum substantive lengths. Below these floors, the section is "占位" not "正文":

| Section type | Floor (Chinese chars) | Floor (English words) | Rationale |
|--------------|-----------------------|------------------------|-----------|
| Abstract | 200 | 150 | Must cover problem + method + key result + robustness in 4-6 sentences |
| Problem restatement | 300 | 220 | Background + main goal + subquestions + constraints |
| Problem analysis | 400 | 280 | Decomposition reasoning + dependency map |
| Assumptions | 200 | 150 | Each necessary assumption stated with justification |
| Symbols and definitions | 150 | 100 | Variable list with units; brief |
| Data preprocessing | 300 | 220 | Sources + cleaning ops + risks |
| Model construction (per Qx) | 600 | 450 | Assumptions + symbols + math model + procedure + metrics — this is the longest per-Qx section |
| Model solution (per Qx) | 250 | 180 | Solver + pipeline + computational notes |
| Results analysis (per Qx) | 500 | 380 | Numerical results + interpretation + baseline comparison + figures referenced |
| Method selection narrative (per Qx) | 300 | 220 | Eliminated methods + why-this-method |
| Robustness and sensitivity | 350 | 250 | Stable conclusions + fragile conclusions + perturbation details |
| Strengths and limitations | 300 | 220 | At least 2 strengths + 2 limitations, each tied to evidence |
| Conclusion | 300 | 220 | Direct answer per subquestion + key numbers + limitations |

If a section is below floor, the writer must report it as `status: under_floor` and identify what is missing (which subsection lacks substance), NOT pad with filler prose. Filler prose triggers `paper-polisher` rejection later.

## G5.2 Three-Dimension Discussion Rule (per numerical result)

Every numerical result reported in the paper MUST be accompanied by at least **three discussion dimensions** out of:

1. **Sensitivity / robustness** — how does the number change under ±10% perturbation of weights / inputs / parameters? (sourced from `robustness/Qx/qx_robustness_report.md`) — **AI may draft** from the robustness report.
2. **Physical / domain meaning** — what does the number mean in the real world? Is it large or small? Plausible or surprising? — **AI MUST NOT author this.** This is a graded modeling judgment: whether a number is large/small/plausible is exactly what a judge grades and a student must learn. The AI emits the sentinel `[MODELER INPUT NEEDED: what does this number mean physically — is it large/small/plausible, what does it imply in the real world?]` in the physical-meaning slot and STOPS. A human replaces it.
3. **Baseline comparison** — how does this number compare to the baseline method's number? (sourced from comparison tables in `qx_final_result_analysis.md`) — **AI may draft** from the analysis comparison tables.
4. **Cross-subquestion consistency** — is this number consistent with related numbers from other subquestions? (e.g., total demand from Q2 should ≈ total allocated from Q3) — **AI may draft** from frozen numbers across Qx.
5. **Uncertainty / confidence interval** — what's the confidence range? Standard error? Bootstrap CI? — **AI may draft** from the analysis/robustness artifacts.

A bare claim like "RMSE = 2.4" with no discussion fails this gate. The minimum is 3 of the above 5 dimensions; pick whichever are most defensible from evidence.

**B-layer rule — physical meaning is the human's dimension.** Dimension 2 (physical / domain meaning) counts toward the ≥3 floor ONLY if its slot traces to a human-authored field, i.e. the `[MODELER INPUT NEEDED: ...]` sentinel has been replaced by human prose. A surviving `[MODELER INPUT NEEDED` (or any `[AI-DRAFT`) sentinel in the physical-meaning slot is NOT a covered dimension — it does not count, exactly as a `<<<HUMAN>>>` sentinel fails the C-layer decision gate. If removing the un-replaced physical-meaning slot drops a numerical claim below 3 covered dimensions, that claim FAILS G5.2 and the section is not "drafted". The AI draws the other dimensions (sensitivity from the robustness report, baseline from the analysis, cross-Qx, uncertainty) but never fabricates or finalizes the physical-meaning one to reach the floor.

In the output JSON summary, include a `three_dimension_check` field listing, per numerical claim, which 3+ dimensions were covered AND, for the physical-meaning slot, whether it is `human_authored: true/false` (a `false` value means that dimension does NOT count and the claim may be under the floor).

## G5.3 Three paper seeds the AI may not author (B-layer)

Three high-stakes framing claims are graded judgments — what a judge reads first and weighs most. The AI may draft surrounding prose and mechanics, but MUST NOT originate these three. Each is emitted as a `[MODELER INPUT NEEDED: ...]` sentinel (no AI draft to copy) and a human must supply it before the abstract / Qx section counts as "drafted". A surviving sentinel here is a GATE FAIL, exactly like the physical-meaning slot above.

1. **`key_result_claim` (abstract headline)** — *which* results are the headline of the paper. The AI knows every frozen number but must not decide which one(s) the abstract leads with. In the abstract draft, the headline slot is:
   `[MODELER INPUT NEEDED: which result(s) are the headline of this paper — the number(s) the abstract leads with and why they matter?]`
   The AI may surround it with the frozen numbers it has (so the human picks from real values), but must not pick the headline itself.

2. **`contribution_claim` (what the innovation is)** — what this paper's contribution / innovation actually is. This is graded contribution, not a mechanical summary. In the abstract and/or strengths section, the contribution slot is:
   `[MODELER INPUT NEEDED: what is this paper's contribution / innovation — what did we do that is new or better, in your own words?]`
   The AI must NOT generalize "we built a model and it worked" into a contribution claim.

3. **`why_this_method` (per Qx) — TRANSCRIBED, not re-authored** — the justification for the chosen method must NOT be re-authored by the AI from the method explanation. It is **transcribed verbatim** from the human's decision log at `methods/Qx/qx_decision_log.md`, with a provenance marker `<!-- from Qx-D0n -->` pointing to the specific decision entry. The method-selection narrative slot is:
   `[MODELER INPUT NEEDED: transcribe the "why this method over the rejected ones" rationale from methods/Qx/qx_decision_log.md and tag it <!-- from Qx-D0n --> with the source decision id. Do NOT re-author this from the method explanation.]`
   If `methods/Qx/qx_decision_log.md` is missing or has no entry for the method choice, the why-this-method slot stays a sentinel (gate FAIL) — route to `modeler-decision-logger`. The AI may quote/restate the *mechanics* of the method (assumptions, symbols, procedure) from the final method explanation, but the *judgment* ("why this over the alternatives") must carry the `<!-- from Qx-D0n -->` provenance marker and trace to a human decision entry. A why-this-method paragraph with no provenance marker fails this gate.

In the output JSON summary, add a `paper_seeds` field reporting, per seed, `present: true/false` and (for `why_this_method`) the `provenance_marker` transcribed. Any seed `present: false` (surviving sentinel) means the affected section is NOT "drafted".

# Three Critical Rules (Enforced as Hard Gates)

This skill MUST enforce these three rules. Violation of any rule means the skill must refuse to write final paper sections and redirect.

## Rule 1: No final paper writing without final method explanation

```
GATE CHECK: methods/Qx/qx_final_method_explanation.md MUST exist.
```

If missing: Stop. Do NOT write the paper section for Qx. The paper writer cannot write the model construction section without knowing the final method, its assumptions, symbols, and mathematical specification. Redirect to `workflow-orchestrator` with a clear blocker report.

The paper writer MAY write a partial draft for other sections that don't depend on the final method (e.g., problem restatement), but MAY NOT write the model construction or results analysis sections.

## Rule 2: No writer handoff without final result analysis

```
GATE CHECK: results/Qx/reports/qx_final_result_analysis.md MUST exist.
```

If missing: Stop. Do NOT write the results analysis section for Qx. Raw experiment outputs are not sufficient — the results must have been analyzed and interpreted by the programmer. Redirect to `workflow-orchestrator` with a clear blocker report.

## Rule 3: Writer reads primarily from the solution package

```
GATE CHECK: results/Qx/reports/qx_solution_package_for_writer.md MUST exist.
```

If missing: Stop. Do NOT write the paper section for Qx by hunting through scattered results and method notes. The solution package is the writer's curated source. If it's missing, the subquestion is NOT Ready for Writer. Redirect to `workflow-orchestrator` or `solution-package-builder`.

# Preconditions

The following must exist before writing final paper sections for a subquestion:

**REQUIRED (hard gates — verified at start)**:
1. `methods/Qx/qx_final_method_explanation.md`
2. `results/Qx/reports/qx_final_result_analysis.md`
3. `results/Qx/reports/qx_solution_package_for_writer.md`

**Also required for complete sections**:
- `methods/Qx/qx_figure_table_plan.md` (figure and table plan).
- Actual figure files referenced in the solution package (must exist on disk).
- Robustness report at `robustness/Qx/qx_robustness_report.md` (for robustness section).
- A validated problem parse (for problem restatement).
- Contest formatting requirements (if available).

**For global sections** (abstract, problem restatement, assumptions, symbols, conclusion):
- All subquestion final method explanations (for symbols and assumptions).
- All subquestion final result analyses (for abstract and conclusion).

If any hard gate is missing, this skill must refuse and report which gate failed.

# Inputs

Use or request (for Qx paper section):

**Primary sources (read first)**:
- `results/Qx/reports/qx_solution_package_for_writer.md` — THE primary source for the writer.
- `methods/Qx/qx_final_method_explanation.md` — method details.
- `results/Qx/reports/qx_final_result_analysis.md` — result details.

**Supporting sources**:
- `methods/Qx/qx_figure_table_plan.md` — figure/table assignments.
- `methods/Qx/qx_method_candidates.md` — for method selection narrative.
- `methods/Qx/qx_method_iteration_log.md` — for iteration history context.
- `robustness/Qx/qx_robustness_report.md` — for robustness section.
- Existing paper section drafts under `paper/sections/`, if any.
- Global symbol table and model assumptions (from `planning/`).
- Problem parse and classification artifacts.
- Contest paper structure or formatting notes.

# Workflow

1. **GATE CHECK: Verify prerequisites.**
   - Before anything else, check that all three hard-gate files exist for the target subquestion.
   - If any is missing, STOP immediately and report which gate failed. Do not proceed.
   - If all gates pass, proceed to step 2.

2. Read the solution package first.
   - The solution package is the writer's primary source. It summarizes everything.
   - Use it to understand the overall narrative before diving into detailed source files.
   - Follow its section mapping, claims inventory, and figure assignments.

3. Gather the detailed sources.
   - Read the final method explanation for model details.
   - Read the final result analysis for numerical claims.
   - Read the figure-table plan for visual assignments.
   - Read the robustness report for sensitivity claims.

4. Build a section map.
   - Map each subquestion to the paper sections that should answer it.
   - Map each model to its assumptions, variables, equations, results, figures, and tables.
   - Map each major claim to a supporting artifact from the solution package's claims inventory.

5. Draft standard paper sections.
   - Write only the sections requested or appropriate for the current workflow stage.
   - Keep the writing concise, technical, and evidence-based.
   - Avoid filler prose.
   - For each section, verify that every claim is traceable to an artifact.

6. Maintain artifact traceability.
   - Every numerical claim must point to a result artifact.
   - Every figure or table reference must appear in the figure-table plan or existing files.
   - Every robustness claim must point to a robustness artifact.
   - Every model description must align with the final method explanation.
   - Use the solution package's claims inventory to verify each claim.

7. Write formulas and symbols carefully.
   - Use mathematical notation only when variables are defined in the final method explanation.
   - Keep notation consistent with the global symbol table.
   - Do not introduce new variables without defining them.

8. Handle missing evidence explicitly.
   - If a result, figure, table, or robustness check is missing, mark the section as incomplete.
   - Do not fill gaps with invented values or generic claims.
   - Recommend the upstream skill needed to complete the missing evidence.

9. Produce section drafts.
   - Save drafts under `paper/sections/`.
   - Use section-oriented file names: `q1.tex` or `q1.md`, `abstract.tex`, `assumptions.tex`, etc.
   - Preserve a clear link between drafts and source artifacts.

10. Recommend final audit.
    - After section drafts are complete enough, hand off to `quality-assurance-auditor`.

# Outputs

Produce paper section drafts and a writing summary:

- `paper/sections/abstract.tex` or `.md`
- `paper/sections/problem_restatement.tex`
- `paper/sections/problem_analysis.tex`
- `paper/sections/assumptions.tex`
- `paper/sections/symbols.tex`
- `paper/sections/data_preprocessing.tex`
- `paper/sections/q1.tex`
- `paper/sections/q2.tex`
- `paper/sections/q3.tex`
- `paper/sections/q4.tex`
- `paper/sections/robustness.tex`
- `paper/sections/strengths_limitations.tex`
- `paper/sections/conclusion.tex`
- Section-to-artifact mapping.
- Incomplete claims list.
- Recommended next skill.

# Output format

Prefer this JSON-compatible summary:

```json
{
  "paper_writing_summary": {
    "status": "awaiting_modeler",
    "target_subquestion": "Q1",
    "gate_check": {
      "rule1_method_explanation_exists": true,
      "rule2_result_analysis_exists": true,
      "rule3_solution_package_exists": true,
      "all_gates_passed": true
    },
    "primary_source_used": "results/Q1/reports/q1_solution_package_for_writer.md",
    "drafted_sections": [
      "paper/sections/q1.tex"
    ],
    "incomplete_sections": [],
    "unsupported_claims": [],
    "three_dimension_check": [
      {
        "claim": "RMSE = 2.4",
        "dimensions_covered": ["sensitivity", "baseline", "physical_meaning"],
        "physical_meaning_human_authored": false,
        "note": "physical-meaning slot still a [MODELER INPUT NEEDED] sentinel — does NOT count; claim currently at 2 covered dimensions, under floor."
      }
    ],
    "paper_seeds": {
      "key_result_claim": { "present": false, "note": "[MODELER INPUT NEEDED] sentinel in abstract — human must pick the headline." },
      "contribution_claim": { "present": false, "note": "[MODELER INPUT NEEDED] sentinel in abstract — human must state the innovation." },
      "why_this_method": { "present": false, "provenance_marker": null, "note": "awaiting transcription from methods/Q1/qx_decision_log.md tagged <!-- from Q1-D0n -->." }
    },
    "surviving_sentinels": [
      "paper/sections/abstract.tex: key_result_claim, contribution_claim",
      "paper/sections/q1.tex: physical-meaning slot for RMSE; why_this_method"
    ],
    "artifact_mapping": [
      {
        "section": "q1.tex",
        "uses_artifacts": [
          "methods/Q1/q1_final_method_explanation.md",
          "methods/Q1/qx_decision_log.md",
          "results/Q1/reports/q1_final_result_analysis.md",
          "results/Q1/reports/q1_solution_package_for_writer.md",
          "results/Q1/experiments/final/figures/q1_ranking.png",
          "robustness/Q1/q1_robustness_report.md"
        ]
      }
    ],
    "recommended_next_skill": "modeler (replace [MODELER INPUT NEEDED] sentinels), then quality-assurance-auditor"
  }
}
```

If a JSON block is too rigid, use a concise Markdown report with the same fields.

# Paper section types

## Abstract
Summarize the problem, methods, key results, robustness evidence, and final conclusions. Mention only numerical results that exist. Do not invent values or claim superiority without evidence. **The AI MUST NOT author two seeds (G5.3):** the `key_result_claim` (which result is the headline) and the `contribution_claim` (what the innovation is) — emit each as a `[MODELER INPUT NEEDED: ...]` sentinel for the human to supply. The AI may draft the problem/method/robustness sentences around them.

## Problem restatement
Restate the problem in the team's own words. Include background, main goal, subquestions, required outputs, and constraints.

## Problem analysis
Explain how the problem is decomposed and why the workflow order is reasonable. Map each subquestion to its task type. Explain dependencies.

## Assumptions
State simplifying assumptions needed for modeling. Each assumption should be necessary, interpretable, and linked to a modeling need. Distinguish necessary from simplifying assumptions.

## Symbols and definitions
Define variables, parameters, sets, indices, functions, and outputs. Distinguish decision variables, state variables, parameters, inputs, and outputs. Include units where available. Keep notation consistent across sections.

## Data preprocessing
Explain data sources, field meanings, cleaning operations, and readiness. Mention missing values, outliers, units, transformations, and remaining risks.

## Model construction (per subquestion)
Present the final model: assumptions, symbols, objective function/ evaluation criterion, constraints, solution procedure. Align with the final method explanation. Include baseline before claiming improvement. Mention eliminated methods to demonstrate thoroughness.

## Model solution (per subquestion)
Explain how the model was solved or computed. Link to generated and reviewed scripts. Mention solver, algorithm, or computation pipeline.

## Results analysis (per subquestion)
Interpret model outputs. Use result tables and figures. Keep conclusions proportional to evidence. Separate result description from causal interpretation. Reference the final result analysis. **For every numerical result, the physical/domain-meaning discussion dimension (G5.2 dim 2) is the human's** — emit `[MODELER INPUT NEEDED: what does this number mean physically — is it large/small/plausible, what does it imply in the real world?]` and let the AI draft the other dimensions (sensitivity, baseline, cross-Qx, uncertainty).

## Method selection narrative (per subquestion, optional)
Describe the candidate method pool, what was tried, what was eliminated, why the final method was chosen. Supported by comparison figures (Type 2) and experiment reports. **The "why this method" judgment is the `why_this_method` seed (G5.3) and MUST be transcribed from `methods/Qx/qx_decision_log.md` with a `<!-- from Qx-D0n -->` provenance marker — the AI must NOT re-author it.** Emit `[MODELER INPUT NEEDED: transcribe the why-this-method rationale from methods/Qx/qx_decision_log.md, tagged <!-- from Qx-D0n -->]` if the decision entry is not yet available. The AI may describe the candidate pool and elimination *mechanics* freely.

## Robustness and sensitivity analysis
Show whether conclusions are stable. Use robustness-checker outputs. Separate stable and fragile conclusions. State conclusion boundaries.

## Strengths and limitations
Explain what the model does well and where it may fail. Be specific. Link limitations to assumptions, data, method, or robustness findings.

## Conclusion and recommendations
Answer the original subquestions and provide final recommendations. Every conclusion should map to a subquestion. Avoid conclusions not supported by results or QA.

## Appendix notes
Describe code, extra tables, parameter settings, or supplementary derivations. Link to scripts and outputs.

# Writing rules

- Write from validated artifacts, not memory or guesswork.
- The solution package is the primary source — use it first, then verify against detailed sources.
- **Source every number from `frozen_numbers.json`**, not from raw `qx_final_result_analysis.md` and not from the section drafts themselves. If `frozen_numbers.json` is missing, the section is NOT writable — route to `solution-package-builder`.
- Keep every major claim traceable to an artifact.
- Use concise, technical language.
- Do not write numerical claims without result artifacts.
- Do not cite figures or tables that do not exist.
- Do not invent references, experiments, or parameter values.
- Do not inflate conclusions beyond robustness evidence.
- Do not hide uncertainty.
- If evidence is missing, mark the section incomplete and name the missing artifact.
- If the solution package says a claim is "to avoid or downgrade", respect that.
- Avoid filler phrases that do not advance the argument.
- **Word-count floors are not suggestions** — a section under floor is `under_floor`, not "drafted". Do not pad with generic prose to hit the floor; identify the missing subsection instead.
- **Every numerical result needs ≥ 3 discussion dimensions** (G5.2). A bare number is not a result; it's an isolated digit.
- **The AI drafts mechanics; the human owns the graded judgments.** Three things the AI MUST NOT finalize on the human's behalf: (a) the physical/domain-meaning discussion dimension for any numerical result (G5.2 dim 2), (b) the abstract's `key_result_claim` and `contribution_claim` (G5.3), (c) the `why_this_method` per Qx, which is transcribed from `methods/Qx/qx_decision_log.md` with a `<!-- from Qx-D0n -->` provenance marker, never re-authored. Each is emitted as a `[MODELER INPUT NEEDED: ...]` sentinel. A surviving `[MODELER INPUT NEEDED` or `[AI-DRAFT` sentinel in a finalized section is a GATE FAIL — the same way a `<<<HUMAN>>>` sentinel fails the C-layer decision artifact. Do not delete a sentinel by writing the judgment yourself; that defeats the gate.

# Rules

- CRITICAL: Enforce the three gate checks before writing ANY final section for a subquestion.
- If gates fail, stop and redirect — do not write the final paper.
- CRITICAL (B-layer): The AI does NOT finalize graded judgments on the human's behalf. For every numerical result, leave the physical/domain-meaning dimension as `[MODELER INPUT NEEDED: ...]` (G5.2 dim 2). In the abstract, leave `key_result_claim` and `contribution_claim` as `[MODELER INPUT NEEDED: ...]` (G5.3). For each Qx, the why-this-method judgment is transcribed from `methods/Qx/qx_decision_log.md` with a `<!-- from Qx-D0n -->` marker, never re-authored. A section with a surviving `[MODELER INPUT NEEDED` / `[AI-DRAFT` sentinel is NOT "drafted" — it is `awaiting_modeler`, and the gate fails (completeness-auditor treats these sentinels as not-done).
- Partial drafts may be written for non-gated sections (problem restatement, data preprocessing) but must be marked as "DRAFT — awaiting [missing prerequisite]".
- Do not run code, clean data, change models, or fabricate data/results/references/figures/tables.
- Do not perform final QA or approve final submission.
- Do not overwrite validated artifacts without permission.
- Do not introduce notation that conflicts with the global symbol table or final method explanation.
- Mark unsupported claims explicitly.
- Keep section drafts modular and reviewable.

# Verification

Before handing off, verify:

- Gate check passed for the target subquestion (all three rules satisfied).
- **Gate G5 passed**: each drafted section is at or above its word-count floor (or marked `under_floor` with identified gap).
- **Three-dimension discussion check**: each numerical claim has ≥ 3 of {sensitivity, physical meaning, baseline, cross-Qx, uncertainty} discussion dimensions — and the physical-meaning dimension counts toward the 3 ONLY if its `[MODELER INPUT NEEDED: ...]` sentinel has been replaced by human prose. Removing un-replaced physical-meaning slots, no numerical claim is left under 3 covered dimensions.
- **B-layer sentinel sweep**: no `[MODELER INPUT NEEDED` and no `[AI-DRAFT` sentinel survives in any section claimed "drafted". The three seeds (G5.3) — `key_result_claim`, `contribution_claim`, `why_this_method` per Qx — are present and human-supplied. Each `why_this_method` paragraph carries a `<!-- from Qx-D0n -->` provenance marker tracing to `methods/Qx/qx_decision_log.md`. A surviving sentinel = gate FAIL; mark the section `awaiting_modeler`, not "drafted".
- The solution package was used as the primary source.
- Every drafted section uses only available artifacts.
- **Every numerical claim is sourced from `frozen_numbers.json`** (not raw results, not previous drafts).
- Every figure or table reference maps to the figure-table plan or existing file.
- Every figure referenced has passed `math-figure-generator`'s `render_check_and_log` (verify by checking `paper/figures/render_check.log`).
- Every robustness claim maps to a robustness artifact.
- Every subquestion has a corresponding draft section or is marked incomplete.
- Assumptions are connected to modeling needs.
- Variables and notation are defined before use.
- Limitations are not hidden.
- Unsupported claims are listed.
- The next skill is `paper-polisher`, then `consistency-auditor` / `completeness-auditor` / `quality-assurance-auditor` (audit layer).

# Failure modes

Stop and report a blocker if:

- **GATE FAILURE (Rule 1)**: `methods/Qx/qx_final_method_explanation.md` is missing. → Redirect to `workflow-orchestrator` or `final-method-explainer`.
- **GATE FAILURE (Rule 2)**: `results/Qx/reports/qx_final_result_analysis.md` is missing. → Redirect to `workflow-orchestrator` or `result-report-generator`.
- **GATE FAILURE (Rule 3)**: `results/Qx/reports/qx_solution_package_for_writer.md` is missing. → Redirect to `workflow-orchestrator` or `solution-package-builder`.
- Model results are missing for a section that requires them.
- Figure-table plan is missing.
- Robustness results are missing for a robustness claim.
- A requested section would require invented numerical values.
- A claim cannot be traced to any artifact.
- The user asks for final paper assembly before QA.
- The user asks to hide uncertainty or unsupported limitations.

# Stop conditions

This skill must stop instead of guessing when:

- Any of the three hard-gate files is missing (see above).
- Drafting would require inventing data, results, figures, tables, references, parameters, or experiments.
- A section depends on a missing upstream artifact.
- The available artifacts contradict each other.
- A conclusion would exceed the evidence.
- A figure or table reference cannot be traced.
- Continuing would overwrite reviewed section drafts without permission.

When stopping, output:
- the blocker
- which gate failed (if applicable)
- why it matters
- affected section
- missing artifact or evidence needed
- safe partial draft if any
- recommended next action

# Handoff

After producing paper section drafts with all gates passed, hand off to:

`quality-assurance-auditor`

The handoff should include:
- drafted section paths
- gate check results
- artifact mapping
- figure and table references
- unsupported or incomplete claims
- missing artifacts
- known writing risks
- sections requiring human review

If missing model results block writing, hand back to the appropriate code generator or `code-reviewer`.

If missing robustness evidence blocks writing, hand back to `robustness-checker`.

If missing visual planning blocks writing, hand back to `figure-table-planner`.

If gates failed, hand back to `workflow-orchestrator` with the specific gate failure report.

# Examples

## Example 1: All gates pass — draft Q1 section, but seeds await the modeler (B-layer)

Input state:
- `methods/Q1/q1_final_method_explanation.md` exists.
- `results/Q1/reports/q1_final_result_analysis.md` exists.
- `results/Q1/reports/q1_solution_package_for_writer.md` exists.
- Figure-table plan exists.
- User asks: "write the Q1 paper section."

The AI drafts the mechanics (model construction, solution, baseline/sensitivity discussion) but leaves the graded judgments as sentinels: the physical-meaning slot per number, and the abstract's `key_result_claim` / `contribution_claim`, and the `why_this_method` paragraph (which must be transcribed from the decision log). Status is `awaiting_modeler`, not "drafted", until those sentinels are replaced by the human.

Output:
```json
{
  "paper_writing_summary": {
    "status": "awaiting_modeler",
    "target_subquestion": "Q1",
    "gate_check": {
      "rule1_method_explanation_exists": true,
      "rule2_result_analysis_exists": true,
      "rule3_solution_package_exists": true,
      "all_gates_passed": true
    },
    "drafted_sections": [
      "paper/sections/q1.tex (mechanics drafted; physical-meaning + why_this_method sentinels pending)"
    ],
    "paper_seeds": {
      "key_result_claim": { "present": false },
      "contribution_claim": { "present": false },
      "why_this_method": { "present": false, "provenance_marker": null }
    },
    "surviving_sentinels": [
      "paper/sections/abstract.tex: key_result_claim, contribution_claim",
      "paper/sections/q1.tex: physical-meaning slot per number; why_this_method"
    ],
    "primary_source_used": "results/Q1/reports/q1_solution_package_for_writer.md",
    "recommended_next_skill": "modeler (replace sentinels; transcribe why_this_method from methods/Q1/qx_decision_log.md), then quality-assurance-auditor"
  }
}
```

## Example 2: Gate failure — Rule 1 violation

Input state:
- User asks: "write the Q2 paper section."
- `methods/Q2/q2_final_method_explanation.md` does NOT exist (modeler hasn't confirmed final method).
- `results/Q2/reports/q2_final_result_analysis.md` exists.
- `results/Q2/reports/q2_solution_package_for_writer.md` does NOT exist (blocked by Rule 1).

Output:
```json
{
  "blocked_items": [
    "GATE FAILURE (Rule 1): Cannot write Q2 paper section. The final method explanation is missing at methods/Q2/q2_final_method_explanation.md."
  ],
  "gate_check": {
    "rule1_method_explanation_exists": false,
    "rule2_result_analysis_exists": true,
    "rule3_solution_package_exists": false,
    "all_gates_passed": false
  },
  "what_can_be_written": [
    "Problem restatement section (does not depend on final method).",
    "Data preprocessing section (if data report exists)."
  ],
  "recommended_next_skill": "workflow-orchestrator",
  "recommended_next_action": "The modeler must confirm the final method for Q2 and run final-method-explainer. Then solution-package-builder must produce the solution package. Only then can the paper writer proceed."
}
```

## Example 3: Gate failure — Rule 2 violation

Input state:
- Q3 has final method explanation.
- Q3 has raw experiment outputs but no final result analysis.
- User says: "Q3 is done, write it up."

Output:
```json
{
  "blocked_items": [
    "GATE FAILURE (Rule 2): Cannot write Q3 paper section. The final result analysis is missing at results/Q3/reports/q3_final_result_analysis.md. Raw experiment outputs are not sufficient — the programmer must analyze and interpret the results first."
  ],
  "gate_check": {
    "rule1_method_explanation_exists": true,
    "rule2_result_analysis_exists": false,
    "rule3_solution_package_exists": false,
    "all_gates_passed": false
  },
  "recommended_next_skill": "result-report-generator",
  "recommended_next_action": "Run result-report-generator in final mode to produce the final result analysis for Q3. Then run solution-package-builder."
}
```

## Example 4: Gate failure — Rule 3 violation

Input state:
- Q4 has final method explanation and final result analysis.
- But no solution package has been built.
- User says: "write Q4 paper section."

Output:
```json
{
  "blocked_items": [
    "GATE FAILURE (Rule 3): Cannot write Q4 paper section. The solution package is missing at results/Q4/reports/q4_solution_package_for_writer.md. The paper writer should use the solution package as primary source, not scatter through method and result files."
  ],
  "gate_check": {
    "rule1_method_explanation_exists": true,
    "rule2_result_analysis_exists": true,
    "rule3_solution_package_exists": false,
    "all_gates_passed": false
  },
  "recommended_next_skill": "solution-package-builder",
  "recommended_next_action": "Run solution-package-builder for Q4 to produce the writer-facing package. Then the paper writer can proceed."
}
```

## Example 5: Write only non-gated sections

Input state:
- Q2 gates fail (Rule 1).
- But the user needs to write problem restatement and data preprocessing sections (which don't depend on Q2's final method).

Output:
```json
{
  "paper_writing_summary": {
    "status": "partial_draft_only",
    "target_subquestion": "Q2",
    "gate_check": {
      "rule1_method_explanation_exists": false,
      "rule2_result_analysis_exists": true,
      "rule3_solution_package_exists": false,
      "all_gates_passed": false
    },
    "drafted_sections": [
      "paper/sections/problem_restatement.md (DRAFT — not Q2-dependent)",
      "paper/sections/data_preprocessing.md (DRAFT — not Q2-dependent)"
    ],
    "blocked_sections": [
      "paper/sections/q2.tex (BLOCKED — awaiting final method explanation and solution package)"
    ],
    "recommended_next_skill": "workflow-orchestrator"
  }
}
```
