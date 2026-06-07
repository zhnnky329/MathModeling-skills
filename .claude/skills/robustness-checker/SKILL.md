---
name: robustness-checker
description: Design and run robustness, sensitivity, error, and baseline comparison checks.
license: MIT
---

# Purpose

Design and run robustness, sensitivity, error, and baseline comparison checks for mathematical modeling contest solutions.

This skill runs the perturbation, sensitivity, error, and baseline computations that test whether model conclusions are stable enough to support paper claims. It compares baseline and main model results, perturbs key parameters or inputs, checks error behavior, identifies fragile assumptions, and records the boundary conditions under which conclusions remain valid.

The computation is AI-owned: running perturbations, computing deltas, comparing against the baseline, and producing the ≥ 5 pass-item report are this skill's job. The **stability verdict itself — "is the model robust enough" and "how confident are we" — is NOT.** That is a modeling judgment the human makes at the gate. This skill lays out the computed evidence plus an explicit `ai_suggestion` reading of it, then emits a PENDING decision artifact and STOPS. It never renders a graded stability verdict on its own.

A key output is the per-subquestion robustness report (`robustness/Qx/qx_robustness_report.md`), which serves the paper materials chain: the report's findings are referenced by the final result analysis, incorporated into the solution package, and ultimately written into the paper's robustness section.

This skill does not choose the original modeling route, rewrite model code broadly, fabricate experiment results, or write final paper sections.

# When to use

Use this skill:

- After `code-reviewer` has confirmed that modeling code is runnable or has clear remaining risks.
- After baseline and main model outputs exist.
- After the final method has been selected (not during early experimentation rounds — basic error checks during experimentation are done by the code or experiment report).
- Before `figure-table-planner`.
- Before paper writing uses model conclusions.
- When the solution needs sensitivity analysis, baseline comparison, error analysis, or stability evidence.
- When final claims depend on parameter choices, weights, random seeds, sampling, constraints, or uncertain assumptions.

# Preconditions

The following should already exist or be provided:

- A validated candidate method pool.
- Final method explanation for the target subquestion (if the final method is locked; otherwise, basic checks only).
- Reviewed modeling code.
- Run instructions.
- Baseline outputs where applicable.
- Main model outputs.
- Cleaned data or approved non-tabular inputs.
- Data audit report and code review report if available.
- Known parameters, weights, thresholds, assumptions, constraints, and random seeds.

If model outputs do not exist, hand back to `code-reviewer`, `python-model-code-generator`, or `matlab-model-code-generator`.

If the main model has no baseline and no justified exception, hand back to `method-selector`.

# Inputs

Use or request:

- Candidate method pool files.
- Final method explanation files (if available).
- Reviewed scripts under `code/`.
- Cleaned data under `workspace/data/data_clean/`.
- Model outputs under `results/Qx/experiments/`.
- Experiment reports under `results/Qx/experiments/roundN/`.
- Figures under `results/Qx/experiments/*/figures/`.
- Code review report.
- Data audit report.
- Baseline result files.
- Main model result files.
- User-specified robustness requirements or contest scoring criteria if available.

# Workflow

1. Identify claims that need support.
   - Extract key conclusions from the final result analysis or experiment reports.
   - Identify which outputs will likely become paper claims.
   - Do not test irrelevant quantities.

2. Map checks to model type.
   - Evaluation models → weight sensitivity, normalization sensitivity, ranking stability.
   - Prediction models → error metrics, split sensitivity, residual checks, extrapolation limits.
   - Optimization models → constraint perturbation, parameter sensitivity, feasibility checks, baseline comparison.
   - Simulation models → random seed stability, trial count sensitivity, distribution summaries.
   - Mechanism models → parameter sensitivity, boundary condition checks, unit or scale consistency.

3. Compare baseline and main model.
   - Confirm that the main model improves, clarifies, or complements the baseline.
   - If the main model does not outperform the baseline, report that honestly.
   - Do not hide baseline failure or main model weakness.

4. Design robustness checks.
   - Perturb key parameters, weights, thresholds, or assumptions.
   - Perturb data where meaningful (noise injection, sample deletion, resampling, missing-value strategy comparison).
   - Test extreme but reasonable scenarios.
   - Test random seed stability when randomness exists.
   - Check feasibility under changed constraints for optimization tasks.

5. Run or specify checks.
   - Run checks when code and data are available.
   - If execution is not possible, produce an executable robustness plan and mark it as not yet run.
   - Do not invent numerical robustness results.

6. Summarize the computed evidence (facts), and offer a reading (suggestion) — do NOT render a verdict.
   - The computed numbers stay AI-owned facts: perturbation deltas, baseline comparison values, error metrics, ranking changes, variance under seeds.
   - You MAY group findings into a *suggested* stable/fragile split and state which conclusions you read as supported vs. requiring caution — but label this as your **`ai_suggestion`**, not a graded verdict.
   - State the boundary conditions under which conclusions appear valid, as evidence the human will weigh.
   - Do NOT auto-render an overall `Status: passed / needs_caution`. The overall stability verdict and the confidence level are decided by the human in step 8.5, not here.

7. Determine figure placement.
   - For each robustness figure, recommend: main paper (Type 3 论文图) or appendix (Type 4 附录图).
   - Criteria: if the result materially affects the main conclusion → main paper. If supplementary detail → appendix.

8. Produce per-subquestion robustness report.
   - Save to `robustness/Qx/qx_robustness_report.md`.
   - Keep the report self-contained and citable from the final result analysis and solution package.

8.5. Emit the modeler decision artifact, then STOP (Gate G4.5).
   - This is the load-bearing change: whether the model is "robust enough" — and how confident we are in its stability — is a graded modeling judgment. The AI must not make it. You ran the perturbations and computed the deltas; the human reads them and commits the verdict.
   - Create `methods/Qx/decisions/robustness-checker_modeler_decision.md` following the **Human Decision Artifact Convention** in CLAUDE.md, with:
     - `schema_version`, `skill: robustness-checker`, `scope: Qx`, `decision_id: qx_stability_verdict`, `decision_point: confidence`.
     - `status: PENDING`, `decided_by: human` (left for the human to confirm), `decided_at` left blank.
     - `ai_suggestion`: your reading of the perturbation / sensitivity / baseline results — your single best stability verdict (`high` / `medium` / `needs_caution`) plus the one number that drives it. This is YOUR view, in its own field — it does not count as the decision. The computed numbers themselves (perturbation deltas, baseline comparison) stay AI-owned facts in the report, not in this field.
     - `choice` (the human's `confidence` ∈ {`high`, `medium`, `needs_caution`}), every `rejected_alternatives[*].reason`, and the `## Modeler's rationale` body left as `<<<HUMAN>>>` sentinels for the modeler to fill. The human rationale MUST cite at least one specific number from the robustness report (e.g. a perturbation delta, a baseline improvement, an error metric) — you cannot trust stability without naming the perturbation result that justifies it. This evidence-citation is the strong lever.
     - `evidence_refs`: point at the real computed numbers under `robustness/Qx/` — the report, the perturbation/sensitivity/baseline CSVs and figures — so the human's rationale resolves to concrete numbers.
   - Then STOP and tell the modeler exactly what to fill in. Do NOT proceed to `figure-table-planner` or hand the verdict downstream. Gate G4.5 (part of the results→freeze human layer) keeps the stability verdict from flowing into the solution package / freeze until this artifact's `status` is `DECIDED` with a non-empty, non-copied human rationale that cites a report number.
   - In **learning mode** (if `planning/session_config.json` says so): withhold `ai_suggestion` until after the human writes their rationale, to avoid anchoring. In **speed mode**: show `ai_suggestion` alongside. Either way the human rationale field, its char floor, and the copy/evidence checks are identical.
   - `modeler-decision-logger` collects this artifact into `methods/Qx/qx_decision_log.md` (append-only).

9. Recommend next step.
   - If robustness evidence is sufficient AND the human has committed the stability verdict (decision artifact `status: DECIDED`), hand off to `figure-table-planner`.
   - If model or code issues are discovered, hand back to the relevant upstream skill.

# Outputs

Produce per-subquestion robustness artifacts:

- `robustness/Q1/q1_robustness_report.md`
- `robustness/Q2/q2_robustness_report.md`
- `robustness/Q3/q3_robustness_report.md`
- `robustness/Q4/q4_robustness_report.md`
- Sensitivity data files: `robustness/Qx/weight_sensitivity.csv`, `robustness/Qx/error_metrics.csv`, `robustness/Qx/constraint_sensitivity.csv`, etc.
- Robustness figures: `robustness/Qx/figures/weight_sensitivity.png`, `robustness/Qx/figures/residual_plot.png`, `robustness/Qx/figures/baseline_comparison.png`, etc.

# Output format

Each `robustness/Qx/qx_robustness_report.md` must follow this structure:

```markdown
# Qx Robustness and Sensitivity Report

## 1. Summary

- **Computed evidence (AI-owned facts)**: [one-sentence factual summary of what the perturbations / baseline comparison produced — the numbers, not a verdict]
- **AI-suggested stability reading** (`ai_suggestion`, NOT a verdict): high / medium / needs_caution — [the one number that drives this reading]
- **Verdict status**: PENDING — decided by the human in `methods/Qx/decisions/robustness-checker_modeler_decision.md` (Gate G4.5). This skill does NOT render the stability verdict.
- **Recommended next skill** (after the human decides): `figure-table-planner`

## 2. Claims Under Test

| # | Claim | Source | Importance |
|---|-------|--------|------------|
| 1 | [claim from final result analysis or experiment report] | [source artifact] | high / medium |

## 3. Baseline Comparison

### 3.1 Comparison Setup
- **Baseline**: [method name]
- **Main model**: [method name]
- **Comparison metric**: [metric name and formula]

### 3.2 Comparison Results

| Metric | Baseline | Main Model | Improvement | Meaningful? |
|--------|----------|------------|-------------|-------------|
| [metric] | [value] | [value] | [delta] | yes / no / marginal |

### 3.3 Baseline Comparison Reading (`ai_suggestion`, NOT a verdict)
- The comparison **numbers** above (baseline value, main-model value, delta) are AI-owned facts.
- Whether the improvement is "meaningful enough" is the AI's *suggested reading* — label it as such. The human commits whether this counts as a meaningful improvement in the decision artifact.
- [If the AI reads the main model as not improving, honest factual statement of the gap]

## 4. Robustness Checks

### 4.1 [Check Type: e.g., Weight Sensitivity]

- **Description**: [what was perturbed, how, and by how much]
- **Perturbation range**: [e.g., ±5%, ±10%, ±20%]
- **Status**: completed / planned / not applicable
- **Artifact**: `robustness/Qx/weight_sensitivity.csv`
- **Figure**: `robustness/Qx/figures/weight_sensitivity.png`
- **Finding**: [specific finding]
- **Conclusion stability**: stable under this perturbation / fragile / breaks
- **Figure recommendation**: main paper / appendix / not needed

### 4.2 [Next Check Type]
[same structure]

## 5. Supported Conclusions

These conclusions are supported by robustness evidence:

| # | Conclusion | Supporting Check | Confidence |
|---|-----------|-----------------|------------|
| 1 | [conclusion] | [check name + artifact] | high / medium |

## 6. Fragile Conclusions

These conclusions require caution or qualification:

| # | Conclusion | Why Fragile | Boundary Condition | Recommended Qualification |
|---|-----------|-------------|-------------------|--------------------------|
| 1 | [conclusion] | [which check revealed fragility] | [under what conditions it holds] | [how to qualify in the paper] |

## 7. Conclusion Boundaries

For each major conclusion, state the conditions under which it remains valid:

| Conclusion | Valid When | May Fail When | Paper Guidance |
|-----------|------------|--------------|----------------|
| [conclusion] | [conditions] | [conditions] | [how to frame in paper] |

## 8. Figure Placement Recommendations

| Figure | Content | Recommended Placement | Reason |
|--------|---------|----------------------|--------|
| `robustness/Qx/figures/weight_sensitivity.png` | Weight perturbation effect on ranking | Main paper (Type 3) | Directly supports key claim about ranking stability |
| `robustness/Qx/figures/full_sensitivity_curves.png` | All indicators, full perturbation | Appendix (Type 4) | Supplementary detail |

## 9. Remaining Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| [risk not covered by current checks] | [potential impact on conclusions] | [how to address or acknowledge in paper] |

## 10. Generated Artifacts

- `robustness/Qx/qx_robustness_report.md`
- `robustness/Qx/weight_sensitivity.csv`
- `robustness/Qx/figures/weight_sensitivity.png`
- `methods/Qx/decisions/robustness-checker_modeler_decision.md` (PENDING — the human commits the stability verdict here at Gate G4.5)

## 11. Handoff

- **Stability verdict**: PENDING — awaiting the human in `methods/Qx/decisions/robustness-checker_modeler_decision.md` (Gate G4.5).
- **Next skill** (after the human decides): `figure-table-planner`
- **AI-suggested supported conclusions** (`ai_suggestion`, for the human to weigh): [list]
- **AI-suggested fragile conclusions** (`ai_suggestion`, for the human to weigh): [list]
```

Plus, separately, the decision artifact `methods/Qx/decisions/robustness-checker_modeler_decision.md` (PENDING, awaiting the human) — see workflow step 8.5.

# Robustness check types

## Baseline comparison
Use when: a baseline and main model both exist; a paper claim says the main model is better.

Check:
- Whether outputs differ materially.
- Whether improvement is meaningful.
- Whether the main model adds interpretability, accuracy, feasibility, or stability.
- Whether the baseline already solves the task sufficiently.

## Parameter sensitivity
Use when: results depend on parameters, thresholds, coefficients, decay rates, penalties, or hyperparameters.

Check:
- Small perturbations (±5%, ±10%, ±20%).
- Monotonicity of output changes.
- Tipping points where conclusions change.
- Parameters that dominate results.

## Weight sensitivity
Use when: evaluation, multi-objective optimization, or weighted scoring is used.

Check:
- Weight perturbation.
- Alternative weighting schemes.
- Ranking stability (do top-K alternatives stay the same?).
- Score stability.

## Data perturbation
Use when: results may depend on noisy, incomplete, or uncertain data.

Check:
- Noise injection.
- Missing-value strategy comparison.
- Sample deletion.
- Bootstrap or resampling if appropriate.
- Effect of outliers.

## Error analysis
Use when: prediction, fitting, classification, or estimation is used.

Check:
- MAE, RMSE, MAPE, accuracy, F1, residuals, confusion matrix.
- Train-test split or cross-validation.
- Error distribution.
- Failure cases.
- Extrapolation limits.

## Constraint perturbation
Use when: optimization constraints affect feasibility or final decisions.

Check:
- Resource limits.
- Budget/capacity limits.
- Fairness or safety bounds.
- Feasibility under relaxed and tightened constraints.

## Randomness stability
Use when: stochastic algorithms, simulations, random sampling, or train-test splits are used.

Check:
- Fixed random seeds.
- Multiple seeds.
- Result variance.
- Trial count sensitivity.
- Confidence intervals or summary statistics.

## Extreme scenario testing
Use when: the model may face boundary cases or policy scenarios.

Check:
- High-demand case.
- Low-resource case.
- Worst-case cost.
- Best-case or optimistic case.
- Edge conditions allowed by the problem context.

## Conclusion boundary (always required)
Check for ALL models:
- What conditions must hold for the conclusion to remain valid.
- Where the conclusion should not be generalized.
- Which assumptions are most important.
- What data limitations constrain the interpretation.

# Rules

- **The human decides the stability verdict at the gate — this skill never assigns it.** Run the perturbations, compute the deltas, compare against baseline, and produce the ≥ 5 pass-item report (all AI-owned). But do NOT auto-render an overall `Status: passed / needs_caution`, and do NOT declare the model "robust enough" or split conclusions into a graded stable/fragile verdict on your own. Emit a PENDING decision artifact (`decision_id: qx_stability_verdict`) and STOP. The human commits `confidence ∈ {high, medium, needs_caution}` at Gate G4.5.
- **Never fill the human rationale field.** Leave `choice`, `rejected_alternatives[*].reason`, and the `## Modeler's rationale` body as `<<<HUMAN>>>` sentinels. Your reading goes ONLY in the `ai_suggestion` field. The human's rationale must cite at least one specific number from the robustness report — do not pre-write or copy it.
- Robustness checks must target claims, not random variables.
- Every major paper claim should have at least one supporting check or a stated limitation.
- Do not invent robustness results.
- Do not report a check as completed unless actually run or derived from existing artifacts.
- If a check is only planned, mark it as planned.
- Prefer simple, explainable checks over elaborate but fragile tests.
- Use baseline comparison whenever a main model claims improvement.
- For evaluation models, check ranking stability.
- For prediction models, report error metrics and residual or failure behavior.
- For optimization models, check feasibility and constraint sensitivity.
- For simulation models, check random seed and trial count stability.
- For mechanism models, check parameter and boundary-condition sensitivity.
- Always include a conclusion boundary section.
- Do not choose a new main model.
- Do not silently change the validated method plan.
- Do not fabricate numerical results or hide unstable findings.
- Do not write final paper text or perform final QA.
- Mark incomplete checks and fragile conclusions explicitly.
- Output per-subquestion reports (not one global report).

# Verification

Before handing off, verify:

- **The stability verdict was NOT originated by this skill.** No auto-rendered overall `Status` verdict; the report's overall stability reading is labeled `ai_suggestion`, not a graded verdict.
- **The decision artifact `methods/Qx/decisions/robustness-checker_modeler_decision.md` exists** with `status: PENDING`, `decision_id: qx_stability_verdict`, `decided_by: human`, `ai_suggestion` filled (in its own field), and `choice` / `rejected_alternatives[*].reason` / `## Modeler's rationale` left as `<<<HUMAN>>>` for the modeler.
- **`evidence_refs` resolve to real computed files under `robustness/Qx/`** so the human's rationale can cite a concrete number.
- **The human rationale field was left for the human** — this skill did not write or copy it; the AI's reading lives only in `ai_suggestion`.
- Gate G4.5 is respected: the stability verdict does not flow into the solution package / freeze until the human sets `status: DECIDED`.
- Per-subquestion robustness report exists for every subquestion that has a final method.
- Baseline comparison exists where applicable.
- Major conclusions have supporting checks or stated limitations.
- Robustness checks match the model type.
- Completed checks have artifacts or clear derivations.
- Planned checks are not mislabeled as completed.
- Generated tables and figures are saved under correct `robustness/Qx/` directories.
- Stable and fragile findings are separated.
- Conclusion boundaries are stated.
- Figure placement recommendations (main paper vs appendix) are provided.
- Remaining risks are listed.
- The next skill is `figure-table-planner` — but only after the human commits the stability verdict (decision artifact `status: DECIDED`).

# Failure modes

Stop and report a blocker if:

- Model outputs do not exist.
- Baseline outputs are missing without justification.
- Reviewed code is unavailable or not runnable.
- Required data is missing.
- The method plan does not define the output being tested.
- Robustness checks would require fabricating data or results.
- Results cannot be traced to scripts, data, or method-plan items.
- The user asks for paper conclusions before robustness evidence exists.

# Stop conditions

This skill must stop instead of guessing when:

- A robustness result cannot be computed from available artifacts.
- The metric or claim to be tested is undefined.
- A required baseline is missing.
- A robustness failure reveals that the method plan is invalid.
- The code cannot be run safely or lacks required inputs.
- Continuing would require inventing numerical findings.

When stopping, output:
- the blocker
- why it matters
- affected subquestion or claim
- checks that can still be performed
- missing information or artifact needed
- recommended next action

# Handoff

If robustness evidence is usable:
→ `figure-table-planner`
— with the per-subquestion robustness report, sensitivity tables, generated figures, supported conclusions, fragile conclusions, figure placement recommendations, and remaining risks.

If robustness checks expose code issues:
→ `code-reviewer`

If robustness checks expose method-plan issues:
→ `method-selector`

If robustness checks expose data issues:
→ `data-auditor-cleaner`

Do not hand off directly to `paper-section-writer` unless figure and table planning has already been completed.

# Relationship to the Paper Materials Chain

The robustness report is a link in the paper materials chain:

```
robustness/Qx/qx_robustness_report.md
    ↓ (referenced by)
results/Qx/reports/qx_final_result_analysis.md
    ↓ (incorporated into)
results/Qx/reports/qx_solution_package_for_writer.md
    ↓ (written into)
paper/sections/robustness.tex
```

The solution-package-builder should reference this report. The final result analysis should cite its findings. The paper robustness section should be based on it.

# Examples

## Example 1: Evaluation robustness (Q1)

Input state:
- Q1 final method: entropy-TOPSIS (M2).
- Equal-weight baseline (M1) exists.
- Ranking results exist.

Output (`robustness/Q1/q1_robustness_report.md` excerpt):

```markdown
# Q1 Robustness and Sensitivity Report

## 1. Summary
- **Computed evidence (AI-owned facts)**: Top-3 ranking unchanged under ±10% weight perturbation; ranks 4-7 swap in 3 of 20 perturbation runs.
- **AI-suggested stability reading** (`ai_suggestion`, NOT a verdict): medium — driven by the rank-4-7 instability (3/20 runs) against a fully stable top-3.
- **Verdict status**: PENDING — decided by the human in `methods/Q1/decisions/robustness-checker_modeler_decision.md` (Gate G4.5). This skill does NOT render the stability verdict.
- **Recommended next skill** (after the human decides): `figure-table-planner`

## 3. Baseline Comparison

| Metric | M1 Equal-Weight | M2 Entropy-TOPSIS | Improvement | Meaningful? (AI reading) |
|--------|----------------|-------------------|-------------|--------------------------|
| Top-3 consistency | N/A (reference) | Same top 3 as M1 | — | M2 confirms M1's top picks |
| Score differentiation (std) | 0.08 | 0.15 | +88% | AI reads as meaningful — human decides |

### 3.3 Baseline Comparison Reading (`ai_suggestion`, NOT a verdict)
The numbers above are AI-owned facts: M2 raises score-differentiation std from 0.08 to 0.15 (+88%) while holding the same top-3. The AI *reads* this as a meaningful improvement that adds discrimination for middle ranks; whether it counts as meaningful enough is committed by the human in the decision artifact.

## 6. Fragile Conclusions

| Conclusion | Why Fragile | Boundary Condition | Recommended Qualification |
|-----------|-------------|-------------------|--------------------------|
| "City D ranks 5th" | Rank changes under ±15% weight perturbation | Stable within ±10% perturbation | "City D ranks 5th under current weights; this position is moderately sensitive to weight assumptions." |

## 8. Figure Placement Recommendations

| Figure | Recommended Placement | Reason |
|--------|----------------------|--------|
| `weight_sensitivity.png` | Main paper (Type 3) | Supports key stability claim |
| `full_sensitivity_curves.png` | Appendix (Type 4) | Supplementary detail |
```

## Example 2: Prediction robustness (Q2)

```markdown
## 1. Summary
- **Computed evidence (AI-owned facts)**: ARIMA cuts 1-3 month RMSE by 35% vs. moving-average baseline; 12-month forecast error grows ~4x over the 3-month error.
- **AI-suggested stability reading** (`ai_suggestion`, NOT a verdict): needs_caution — driven by the ~4x long-horizon error growth, despite the strong 35% short-term gain.
- **Verdict status**: PENDING — decided by the human in `methods/Q2/decisions/robustness-checker_modeler_decision.md` (Gate G4.5). This skill does NOT render the stability verdict.

## 5. AI-Suggested Supported Conclusions (`ai_suggestion`, for the human to weigh)
| Conclusion | Supporting Check | AI confidence reading |
|-----------|-----------------|-----------------------|
| "ARIMA improves short-term RMSE by 35% over moving average baseline." | Error analysis (1-3 month horizon) | High |

## 6. Fragile Conclusions
| Conclusion | Why Fragile | Recommended Qualification |
|-----------|-------------|--------------------------|
| "Future demand will be X in month 12." | Long-term forecast error grows exponentially | "The model projects X for month 12, but uncertainty increases substantially beyond a 3-month horizon." |
```

## Example 3: Blocked by missing baseline

```json
{
  "blocked_items": [
    "Baseline output is missing for Q3. The main optimization result cannot be compared against a reference plan."
  ],
  "affected_subquestion": "Q3",
  "recommended_next_skill": "python-model-code-generator or matlab-model-code-generator",
  "recommended_next_action": "Generate and review the planned baseline output before robustness comparison."
}
```
