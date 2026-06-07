---
name: figure-table-planner
description: Plan figures and tables that support the modeling logic, results, and paper narrative.
license: MIT
---

# Purpose

Plan figures and tables for a mathematical modeling contest solution, classifying each visual by its audience and purpose.

This skill determines which figures and tables are needed, what claim each artifact supports, which subquestion it belongs to, which data or result artifact it should use, which of four audience categories it falls into (diagnostic, comparison, paper, appendix), and where it should appear in the paper.

This skill ensures that visual materials serve the modeling logic rather than decoration, and that different audiences (modeler, method selector, paper reader) get the right visuals.

This skill does not fabricate data, generate unsupported figures, write final paper sections, or perform final QA.

**B-layer posture — the AI drafts, the modeler owns the claim.** Two spans in this plan are interpretive modeling judgments a judge grades, not mechanical bookkeeping: (a) the **figure TYPE** (1 诊断 / 2 对比 / 3 论文 / 4 附录) — what audience and purpose a figure serves — and (b) the **`core_claim`** — the single conclusion a figure is asked to defend in the paper. The AI may DRAFT both, but it must not FINALIZE either on the modeler's behalf:
- The AI proposes a type as `[AI-DRAFT — modeler must confirm: <type>]`. The human ratifies or changes it.
- For any **Type 3 (论文图)** figure — every figure that enters the paper — the AI must NOT author the claim. It writes `[MODELER INPUT NEEDED: what single claim does this figure defend?]` and stops there. A figure's claim is the sentence a judge weighs the figure against; the human authors it.
- These sentinels (`[AI-DRAFT`, `[MODELER INPUT NEEDED`) are exactly like the C-layer `<<<HUMAN>>>` sentinel: a surviving sentinel in a finalized plan is a GATE FAIL. `completeness-auditor` treats them as "not done". See Rules and Verification.

# When to use

Use this skill:

- After `robustness-checker` has produced usable robustness evidence.
- After model results, baseline comparisons, and major validation outputs exist.
- Before `paper-section-writer`.
- When the team needs a figure and table plan for the paper.
- When existing figures or tables need to be checked for narrative relevance.
- When the solution needs flowcharts, mechanism diagrams, result plots, comparison tables, or sensitivity tables.

# Preconditions

The following should already exist or be provided:

- A validated problem parse.
- Candidate method pool per subquestion.
- Data report and field mapping if data is used.
- Model result tables and figures (generated from experiments).
- Robustness or sensitivity results.
- Existing figure files if already generated.
- Expected paper structure or subquestion order if available.

If model results do not exist, hand back to `code-reviewer`, `python-model-code-generator`, `matlab-model-code-generator`, or `robustness-checker`.

If robustness evidence is required but missing, hand back to `robustness-checker`.

# Inputs

Use or request:

- `workspace/problem/problem-parser/problem_parse.json`, if available.
- Candidate method pool files under `methods/`.
- Final method explanation files under `methods/` (if available).
- `workspace/data/data_report.md`, if available.
- Model result files under `results/Qx/experiments/`.
- Robustness report and sensitivity tables under `robustness/`.
- Existing figures under `results/Qx/experiments/*/figures/`.
- Code review summary if it affects figure reliability.
- Expected paper section list if available.
- User preferences for visual style or contest formatting, if provided.

# Figure Type Classification (Four Categories)

Every planned figure MUST be classified into one of four types:

## Type 1: 诊断图 (Diagnostic Figures)

**Audience**: The modeler.
**Purpose**: Diagnose model problems, check assumptions, identify where the model is failing.
**When generated**: During experimentation rounds, before final method selection.
**Paper use**: Usually NOT included in the paper. For internal model debugging only.
**Examples**:
- Residual diagnostic plots (checking error patterns).
- QQ plots (checking distribution assumptions).
- Convergence trace plots (checking optimization convergence).
- Correlation heatmaps of indicators (checking multicollinearity).
- Intermediate computation visualizations (checking calculation correctness).
- Data distribution plots before/after transformation.

**Requirements**:
- Must help the modeler decide whether to revise the model.
- Should be generated early (round 1 or earlier).
- Save to `results/Qx/experiments/roundN/figures/` (not paper figures).

## Type 2: 对比图 (Comparison Figures)

**Audience**: The modeler AND the paper writer (for method selection narrative).
**Purpose**: Compare multiple candidate methods head-to-head, supporting method selection.
**When generated**: During multi-method experiment rounds.
**Paper use**: MAY be included in the paper to demonstrate thorough method selection, or may be referenced in text only.
**Examples**:
- Side-by-side ranking comparison across methods.
- Prediction error comparison across methods (bar chart of RMSE/MAE).
- Method performance radar chart.
- Baseline vs main model overlay plots.
- ROC/PR curve comparison for classification methods.

**Requirements**:
- Must clearly show which method performs better and on what criterion.
- Must support the method selection narrative in the paper.
- Save to `results/Qx/experiments/roundN/figures/`; if selected for paper, copy to `paper/figures/`.

## Type 3: 论文图 (Paper Figures)

**Audience**: The paper reader (contest judges).
**Purpose**: Support the main claims in the paper — final results, model structure, key findings.
**When generated**: After final method is locked in.
**Paper use**: MUST be included in the paper.
**Examples**:
- Final ranking bar chart.
- Final prediction vs actual plot.
- Optimal allocation map or diagram.
- Model workflow/architecture diagram.
- Mechanism schematic.
- Key sensitivity analysis result plot.
- Final result summary figure.

**Requirements**:
- Must be publication-quality: clear labels, readable fonts, proper legends, high resolution (≥300 dpi).
- Must directly support a paper claim. **The claim is the modeler's to author.** Because a Type 3 figure enters the paper, its `core_claim` is a judgment a judge grades — the AI must NOT finalize it. Write the claim cell as `[MODELER INPUT NEEDED: what single claim does this figure defend?]` and leave it for the human. (The AI may still draft the figure's *type/title/source artifact*; only the claim is off-limits to author.)
- Must have a complete, informative caption.
- Must be generated from final (not intermediate) results.
- Save to `paper/figures/` (final location).

## Type 4: 附录图 (Appendix Figures)

**Audience**: The paper reader (for supplementary reference).
**Purpose**: Provide supplementary evidence, detailed results, or additional validation.
**When generated**: After final method is locked in, when the main paper cannot fit all figures.
**Paper use**: Referenced in main text, shown in appendix.
**Examples**:
- Full set of sensitivity curves (main paper shows only key ones).
- Detailed indicator-by-indicator breakdown.
- Additional scenario results.
- Full convergence plots for optimization.
- Extended error analysis plots.

**Requirements**:
- Must be referenced from the main text ("see Appendix Figure X").
- Must not contain critical evidence that should be in the main paper.
- Save to `paper/figures/` with clear appendix labeling.

# Workflow

1. Identify paper claims and evidence needs.
   - Determine which claims require visual or tabular support.
   - Map claims to subquestions and model outputs.
   - Do not plan figures for unsupported claims.

2. Inventory available artifacts.
   - List existing result tables, robustness tables, and figure files.
   - Classify each existing figure into one of the four types.
   - Identify which artifacts are ready to use.
   - Identify which artifacts are missing but necessary.

3. Plan structural figures (typically Type 3 or Type 1).
   - Plan overall workflow diagrams (Type 3 — 论文图).
   - Plan model principle diagrams (Type 3 — 论文图).
   - Plan diagnostic structural checks (Type 1 — 诊断图).

4. Plan result figures (classify each).
   - Type 3 (论文图): Final ranking, prediction, optimization results.
   - Type 2 (对比图): Method comparison for selection narrative.
   - Type 1 (诊断图): Residual checks, diagnostic plots.
   - Type 4 (附录图): Extended sensitivity, supplementary scenarios.

5. Plan tables (classify similarly).
   - Plan symbol tables, parameter tables, data summary tables, model comparison tables, result tables, and sensitivity tables as needed.
   - Avoid duplicating the same information in both a table and a figure unless each serves a distinct purpose.

6. Link figures and tables to paper sections.
   - Assign every figure or table to a section.
   - State what sentence or claim it supports.
   - Mark required captions and interpretation notes.
   - For Type 2 figures, note whether they go in the method selection narrative or are reference-only.

7. Check visual evidence quality.
   - Ensure every planned artifact uses available data, model results, or robustness results.
   - Mark artifacts that are missing source data.
   - Reject decorative visuals that do not support reasoning.

8. Produce a figure-table plan per subquestion.
   - Save as `methods/Qx/qx_figure_table_plan.md`.
   - Keep the plan concise and traceable.
   - Include the four-type classification for every figure.

# Outputs

Produce per-subquestion figure-table plans:

- `methods/Q1/q1_figure_table_plan.md`
- `methods/Q2/q2_figure_table_plan.md`
- `methods/Q3/q3_figure_table_plan.md`
- `methods/Q4/q4_figure_table_plan.md` (if needed)

Each plan includes:
- Figure inventory with four-type classification.
- Table inventory.
- Existing vs planned status.
- Paper section mapping.
- Caption requirements.
- Visual risks.

# Output format

Each `methods/Qx/qx_figure_table_plan.md` must follow this structure:

```markdown
# Qx Figure and Table Plan

## 1. Figure Inventory

### Type 3 — 论文图 (Paper Figures — MUST appear in paper)

The figure **type** is an AI draft the modeler confirms; the **Claim Supported** for every Type 3 figure is `[MODELER INPUT NEEDED: ...]` — the AI must not author it. A surviving sentinel here is a GATE FAIL.

| ID | Title | Type | Claim Supported | Source Artifact | Paper Section | Status | Caption |
|----|-------|------|----------------|-----------------|---------------|--------|---------|
| Fig.X.1 | Final Ranking Comparison | `[AI-DRAFT — modeler must confirm: bar chart / 论文图]` | `[MODELER INPUT NEEDED: what single claim does this figure defend?]` | `results/Q1/experiments/final/tables/m2_scores.csv` | Results Analysis | exists / planned | "Figure X: Final city rankings based on entropy-weight TOPSIS scores..." |

### Type 2 — 对比图 (Comparison Figures — MAY appear in paper)

| ID | Title | Type | Comparison | Source Artifact | Paper Section (if used) | Status | Caption |
|----|-------|------|-----------|-----------------|------------------------|--------|---------|
| Fig.X.2 | Method Comparison: Ranking Overlap | venn/heatmap | M1 vs M2 vs M3 | `results/Q1/experiments/round2/metrics/comparison_metrics.json` | Method Selection or Appendix | exists / planned | "Figure X: Overlap of top-5 rankings across three candidate methods..." |

### Type 1 — 诊断图 (Diagnostic Figures — Internal use, NOT for paper)

| ID | Title | Type | Diagnostic Purpose | Source Artifact | Status |
|----|-------|------|-------------------|-----------------|--------|
| Fig.X.D1 | Indicator Correlation Heatmap | heatmap | Check multicollinearity among indicators | `workspace/data/data_clean/indicator_data.csv` | exists / planned |

### Type 4 — 附录图 (Appendix Figures — Reference from main text)

| ID | Title | Type | Claim Supported | Source Artifact | Status |
|----|-------|------|----------------|-----------------|--------|
| Fig.X.A1 | Full Weight Sensitivity for All Indicators | sensitivity curves | Extended sensitivity analysis (main paper shows top-3 indicators only) | `robustness/Q1/weight_sensitivity.csv` | planned |

## 2. Table Inventory

| ID | Title | Type | Claim Supported | Source Artifact | Paper Section | Status |
|----|-------|------|----------------|-----------------|---------------|--------|
| Table X.1 | Indicator Weights (Entropy Method) | result table | "Indicator weights are objectively determined by data dispersion." | `results/Q1/experiments/final/tables/m2_weights.csv` | Model Construction | exists |
| Table X.2 | Method Comparison Metrics | comparison table | "Entropy-TOPSIS provides better differentiation than equal-weight scoring." | `results/Q1/experiments/round2/metrics/comparison_metrics.json` | Method Selection | exists |
| Table X.3 | Weight Sensitivity Results | sensitivity table | "Top-3 ranking remains stable under ±10% weight perturbation." | `robustness/Q1/weight_sensitivity.csv` | Robustness Analysis | exists |

## 3. Existing vs Planned Summary

- **Existing figures**: [count] (Type 1: [n], Type 2: [n], Type 3: [n], Type 4: [n])
- **Planned figures**: [count] (Type 1: [n], Type 2: [n], Type 3: [n], Type 4: [n])
- **Existing tables**: [count]
- **Planned tables**: [count]

## 4. Missing Artifacts

| Artifact | Type | Reason Needed | Blocking? |
|----------|------|---------------|-----------|
| `paper/figures/q1_final_ranking.png` | Type 3 | Required for Results Analysis section | Yes |
| `results/Q1/experiments/round2/figures/residual_diagnostic.png` | Type 1 | Useful for modeler to check indicator redundancy | No |

## 5. Visual Risks

- [Risk 1: e.g., "Final ranking figure does not yet have publication-quality formatting."]
- [Risk 2: e.g., "Comparison figure only covers 2 of 3 candidate methods."]

## 6. Handoff

- **Next skill**: `paper-section-writer`
- **Ready figures for paper**: [list]
- **Figures needing generation/improvement**: [list]
```

# Table types

Use these table types consistently:

| Type | Purpose | Paper Use |
|------|---------|-----------|
| `symbol_table` | Define variables, parameters, units | Always in paper (Symbols section) |
| `data_summary_table` | Describe data fields, quality, transformations | Usually in paper (Data Preprocessing) |
| `model_result_table` | Show final scores, rankings, predictions, decisions | Always in paper (Results Analysis) |
| `comparison_table` | Compare baseline vs main model, or multiple candidate methods | Often in paper (Method Selection or Results) |
| `sensitivity_table` | Show parameter perturbation effects | Always in paper (Robustness) |
| `parameter_table` | List model parameters and their values/sources | Often in paper (Model Construction) |

# Rules

- Every planned figure must be classified into one of the four types (诊断图, 对比图, 论文图, 附录图). **The type is the modeler's to confirm.** The AI may suggest a type, but it writes it as `[AI-DRAFT — modeler must confirm: <type>]`; the human ratifies or changes it. The four-type taxonomy and the "Type 1 诊断图 never in paper" rule are unchanged.
- Every planned figure or table must support a specific claim. **For every Type 3 (论文图) figure — every figure that enters the paper — the AI must NOT author the claim.** Write the claim as `[MODELER INPUT NEEDED: what single claim does this figure defend?]`. The claim is the one sentence a judge weighs the figure against; the modeler owns it. (For Type 1/2/4 the AI may draft a claim, but a Type 3 claim is load-bearing and human-authored.)
- A surviving `[AI-DRAFT` or `[MODELER INPUT NEEDED` sentinel in a finalized plan is a GATE FAIL — identical to a surviving `<<<HUMAN>>>` in a C-layer decision artifact. `completeness-auditor` treats these as "not done". Do not strip a sentinel by inventing the human's answer; only the modeler resolves it.
- Every planned figure or table must map to at least one source artifact.
- Every planned figure or table must map to a paper section (Type 1 diagnostic figures may map to "Internal Use Only").
- Prefer fewer high-value visuals over many decorative visuals.
- Type 3 论文图 must be publication-quality.
- Type 1 诊断图 should not appear in the paper (they are for modeler use).
- Type 2 对比图 should support the method selection narrative.
- Use workflow figures to explain logic, not results.
- Use result figures to support conclusions, not to decorate.
- Use tables when exact values matter.
- Use plots when patterns, trends, or comparisons matter.
- Captions must explain what the reader should learn from the artifact.
- Do not fabricate figure data or table values.
- Do not plan visuals for unsupported claims.
- Mark visual risks explicitly.

# Verification

Before handing off, verify:

- Every planned figure has a type (1-4), source artifact, target section, and supported claim.
- Every planned table has a type, source artifact, target section, and supported claim.
- **B-layer sentinel check (gate-blocking):** no `[AI-DRAFT` and no `[MODELER INPUT NEEDED` sentinel survives in a plan that is being handed off as "ready". A surviving sentinel means the modeler has not yet confirmed the figure type or authored the Type 3 claim — the plan is NOT ready, exactly as a surviving `<<<HUMAN>>>` blocks a C-layer artifact. Grep each `methods/Qx/qx_figure_table_plan.md` for `[AI-DRAFT` and `[MODELER INPUT NEEDED` before claiming done.
- **Every Type 3 (论文图) figure has a human-authored `core_claim`** — not an AI sentence, not a copy of the AI's caption. If the claim cell still reads `[MODELER INPUT NEEDED: ...]`, hand the plan back to the modeler; do not author the claim to make the gate pass.
- Type classification is correct: diagnostic figures are not marked as paper figures, and vice versa.
- Existing artifacts and missing artifacts are separated.
- No figure or table relies on fabricated data.
- Robustness visuals correspond to completed or explicitly planned checks.
- Important model claims have at least one Type 3 figure or a justification for text-only.
- Captions or caption requirements are specified.
- The next skill is `paper-section-writer` or `workflow-orchestrator`.

# Failure modes

Stop and report a blocker if:

- Model results are missing for planned paper figures.
- Robustness results are missing but required for key claims.
- A requested paper figure has no source artifact.
- A requested table would require invented values.
- The paper structure is too unclear to map visuals to sections.
- Existing figures contradict model results or cannot be traced.

# Stop conditions

This skill must stop instead of guessing when:

- A planned artifact requires unavailable numerical results.
- A figure or table would imply a claim not supported by existing outputs.
- The source data for a visual cannot be identified.
- The user asks to create evidence for a conclusion that has not been validated.
- Continuing would require inventing data, captions, values, or experimental findings.

When stopping, output:
- the blocker
- why it matters
- affected figure or table
- missing artifact or source needed
- safe partial plan if any
- recommended next action

# Handoff

After producing per-subquestion figure-table plans, hand off to:

`paper-section-writer`

The handoff should include:
- Per-subquestion figure-table plans.
- Type 3 (论文图) inventory — these are the paper writer's required figures.
- Type 2 (对比图) inventory — these may be used for method selection narrative.
- Table inventory.
- Source artifacts.
- Section mapping.
- Caption requirements.
- Visual risks.
- Missing artifacts.

If missing visuals require additional robustness results, hand back to `robustness-checker`.

If missing visuals require model outputs, hand back to `code-reviewer` or a language-specific model-code-generator.

# Examples

## Example 1: Evaluation model figure plan (Q1)

Input state:
- Q1 final method: entropy-TOPSIS.
- Results exist: scores, weights, ranking.
- Robustness exists: weight sensitivity.
- Baseline comparison exists.

Output (`methods/Q1/q1_figure_table_plan.md` excerpt):

```markdown
# Q1 Figure and Table Plan

## 1. Figure Inventory

### Type 3 — 论文图 (Paper Figures)

Type cells carry the AI's confirmable draft; every Claim Supported cell is left for the modeler. (Sentinels shown unresolved here on purpose — a finalized plan must have all of these replaced by the human, or the gate fails.)

| ID | Title | Type | Claim Supported | Paper Section | Status |
|----|-------|------|----------------|---------------|--------|
| Fig.1.1 | Overall Evaluation Workflow | `[AI-DRAFT — modeler must confirm: flowchart / 论文图]` | `[MODELER INPUT NEEDED: what single claim does this figure defend?]` | Model Construction | planned |
| Fig.1.2 | Indicator Weight Distribution | `[AI-DRAFT — modeler must confirm: bar chart / 论文图]` | `[MODELER INPUT NEEDED: what single claim does this figure defend?]` | Model Construction | exists |
| Fig.1.3 | Final City Ranking | `[AI-DRAFT — modeler must confirm: horizontal bar chart / 论文图]` | `[MODELER INPUT NEEDED: what single claim does this figure defend?]` | Results Analysis | exists |

### Type 2 — 对比图 (Comparison Figures)

| ID | Title | Type | Comparison | Paper Section | Status |
|----|-------|------|-----------|---------------|--------|
| Fig.1.4 | Ranking Comparison: Equal-Weight vs Entropy-TOPSIS | scatter/dumbbell | M1 (baseline) vs M2 (final) | Method Selection | exists |
| Fig.1.5 | Method Comparison Radar Chart | radar | M1 vs M2 vs M3 on 5 criteria | Method Selection (optional) | planned |

### Type 1 — 诊断图 (Internal Use)

| ID | Title | Type | Diagnostic Purpose | Status |
|----|-------|------|-------------------|--------|
| Fig.1.D1 | Indicator Correlation Matrix | heatmap | Check for redundant indicators before entropy weighting | exists |
| Fig.1.D2 | Score Distribution by Method | histogram | Check if scores are overly concentrated | exists |

### Type 4 — 附录图 (Appendix)

| ID | Title | Type | Claim Supported | Status |
|----|-------|------|----------------|--------|
| Fig.1.A1 | Full Weight Sensitivity (±20%) | sensitivity lines | Extended robustness (main paper shows ±10% only) | planned |
```

## Example 2: Prediction model figure plan (Q2)

```markdown
### Type 3 — 论文图

(Claim cells stay `[MODELER INPUT NEEDED]` until the modeler authors them; the type is the AI's confirmable draft.)

| ID | Title | Type | Claim Supported | Status |
|----|-------|------|----------------|--------|
| Fig.2.1 | Prediction vs Actual (Test Set) | `[AI-DRAFT — modeler must confirm: scatter + line / 论文图]` | `[MODELER INPUT NEEDED: what single claim does this figure defend?]` | exists |
| Fig.2.2 | Forecast with Confidence Intervals | `[AI-DRAFT — modeler must confirm: line + ribbon / 论文图]` | `[MODELER INPUT NEEDED: what single claim does this figure defend?]` | exists |

### Type 2 — 对比图

| ID | Title | Comparison | Status |
|----|-------|-----------|--------|
| Fig.2.3 | Method Error Comparison (RMSE) | Moving Average vs ARIMA vs Grey Prediction | exists |
| Fig.2.4 | Residual Comparison | M1 vs M2 vs M3 | planned |

### Type 1 — 诊断图

| ID | Title | Diagnostic Purpose | Status |
|----|-------|-------------------|--------|
| Fig.2.D1 | ACF/PACF Plot | Identify ARIMA order (p, d, q) | exists |
| Fig.2.D2 | Residual ACF | Check if residuals are white noise | exists |

### Type 4 — 附录图

| ID | Title | Claim Supported | Status |
|----|-------|----------------|--------|
| Fig.2.A1 | Rolling-Origin Forecast Evaluation | Extended validation | planned |
```
