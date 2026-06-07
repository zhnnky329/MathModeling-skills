---
name: model-assumptions-builder
description: Extract, organize, and document unified model assumptions from the problem parse and candidate method pools, distinguishing necessary from simplifying assumptions.
license: MIT
---

# Purpose

Extract, organize, and document unified model assumptions for the entire mathematical modeling contest solution.

This skill reads the problem parse and all subquestion candidate method pools, identifies every assumption (both explicit from the problem and implicit from method choices), categorizes them by necessity and scope, checks for conflicts between subquestions, and produces a single structured assumptions document that feeds the paper's "Model Assumptions" section.

This skill does not invent assumptions, select methods, or write paper sections.

# When to use

Use this skill:

- After `problem-parser` and `problem-classifier` have produced validated artifacts.
- After `method-selector` has produced candidate method pools for all subquestions.
- Before paper writing — assumptions should be documented early and refined through the workflow.
- When the user says: "list all assumptions", "organize the model assumptions", "what are we assuming?", "build the assumptions document".

# Preconditions

The following should already exist or be provided:

- A validated problem parse.
- Candidate method pools for all subquestions (or those planned so far).
- The question dependency map (if available).

# Inputs

Use or request:

- `workspace/problem/problem-parser/problem_parse.json` — for explicit constraints and implicit assumptions from the problem.
- `methods/Qx/qx_method_candidates.md` — for method-specific assumptions.
- `planning/question_dependency.md` — for cross-subquestion context.
- Any notes the modeler has about domain knowledge or contest constraints.

# Workflow

1. Extract explicit assumptions from the problem statement.
   - Assumptions stated directly in the problem: "assume demand is independent", "assume travel time is proportional to distance".
   - Constraints that function as assumptions when simplified.

2. Extract implicit assumptions from the problem context.
   - Reasonable real-world assumptions not stated but necessary for modeling.
   - Example: "all cities are accessible", "data is accurate and complete", "future conditions follow historical patterns".

3. Extract method-induced assumptions from each subquestion's candidate pool.
   - Every modeling method introduces assumptions.
   - Example: TOPSIS assumes indicators are independent; linear programming assumes linearity; ARIMA assumes stationarity after differencing.

4. Categorize every assumption.

   **By necessity (JUDGMENT — modeler ratifies):**
   - **Necessary (hard)**: The model breaks or becomes meaningless if violated.
   - **Simplifying (soft)**: The model still works approximately but is less accurate if violated.
   - The necessary-vs-simplifying call is a modeling judgment a judge grades, not a mechanical fact. The AI proposes a label but does NOT finalize it: write each Type cell as `[AI-DRAFT — modeler must confirm: necessary | simplifying]` (keep the AI's actual pick inside the sentinel) so the modeler must act to ratify or change it.

   **By scope (AI-owned — mechanical):**
   - **Global**: Applies to all subquestions (e.g., "data is reliable").
   - **Per-subquestion**: Applies only to specific subquestions (e.g., "indicators are independent" for Q1 TOPSIS).
   - **Method-specific**: Applies only to a specific candidate method.

5. Check for conflicting assumptions.
   - An assumption for Q1 might contradict an assumption for Q3.
   - Example: Q1 assumes indicators are independent, but Q3 uses a method that models indicator interactions — these must be reconciled.

6. Assess assumption impact (JUDGMENT — modeler ratifies).
   - For each assumption, state what happens if it is violated.
   - Weak assumptions (those whose violation changes conclusions) should be flagged.
   - The impact-if-violated framing is a modeling judgment the human owns: it is what tells a judge how exposed the model is. The AI drafts it but does NOT finalize it — write each impact cell as `[AI-DRAFT — modeler must confirm: <impact if violated>]` so the modeler must ratify or rewrite it.

7. Produce the assumptions document.
   - Save as `planning/model_assumptions.md`.
   - Keep it structured and traceable to sources.

# Outputs

Produce one document:

- `planning/model_assumptions.md`

# Output format

> **B-layer (drafts for review).** Surfacing candidate assumptions, their source, and a draft justification stays AI-owned. But two columns are modeling *judgment* the human owns and a judge grades: the **Type (necessary | simplifying)** label and the **Impact if Violated / Relaxed** framing. The AI must NOT finalize these — it drafts them inside `[AI-DRAFT — modeler must confirm: ...]` sentinels, and the modeler ratifies (keeps or rewrites). A surviving `[AI-DRAFT` sentinel in a finalized `planning/model_assumptions.md` is a GATE FAIL, exactly like a `<<<HUMAN>>>` sentinel in a C-layer decision artifact — `completeness-auditor` treats it as "not done". Every assumption still stays tied to a modeling need (problem statement or a specific method); never invent assumptions to fill the table.

```markdown
# Global Model Assumptions

> Last updated: [timestamp]
> Based on: problem statement + candidate method pools for Q1-Q4

## 1. Global Assumptions (Apply to All Subquestions)

### 1.1 Necessary Global Assumptions

> The "Necessary" placement of each row below is an AI draft; the modeler confirms or moves the row by ratifying the Type sentinel.

| # | Assumption | Source | Justification | Type | Impact if Violated |
|---|-----------|--------|---------------|------|-------------------|
| A1 | The provided data accurately reflects the true state of the system. | Problem statement | No alternative data source; contest data is taken as given. | [AI-DRAFT — modeler must confirm: necessary] | [AI-DRAFT — modeler must confirm: All quantitative results become unreliable.] |
| A2 | The system operates under steady-state conditions (no structural breaks within the analysis period). | Implicit from problem context | The problem does not describe regime changes or structural shifts. | [AI-DRAFT — modeler must confirm: necessary] | [AI-DRAFT — modeler must confirm: Predictions and rankings may be invalid for periods with structural changes.] |
| A3 | All cities/alternatives are comparable on the same set of indicators. | Implicit from problem context | The problem asks for a unified ranking/evaluation. | [AI-DRAFT — modeler must confirm: necessary] | [AI-DRAFT — modeler must confirm: Ranking becomes meaningless if cities are incommensurable.] |

### 1.2 Simplifying Global Assumptions

> The "Simplifying" placement of each row below is an AI draft; the modeler confirms or moves the row by ratifying the Type sentinel.

| # | Assumption | Source | Justification | Type | Impact if Relaxed |
|---|-----------|--------|---------------|------|-------------------|
| A4 | External factors not mentioned in the problem do not significantly affect the system. | Implicit | Contest scope limitation; model cannot account for unmentioned factors. | [AI-DRAFT — modeler must confirm: simplifying] | [AI-DRAFT — modeler must confirm: Results may not generalize to real-world scenarios with additional factors.] |
| A5 | Data measurement errors are negligible. | Implicit | No error margins provided in data. | [AI-DRAFT — modeler must confirm: simplifying] | [AI-DRAFT — modeler must confirm: Rankings and predictions would have wider confidence intervals.] |

## 2. Q1 Assumptions (Evaluation)

### 2.1 Necessary

> The "Necessary" placement of each row below is an AI draft; the modeler confirms or moves the row by ratifying the Type sentinel.

| # | Assumption | Method | Justification | Type | Impact if Violated |
|---|-----------|--------|---------------|------|-------------------|
| Q1-A1 | Indicators are sufficiently independent for entropy weighting. | M2: Entropy-TOPSIS | Entropy weights can be distorted by highly correlated indicators. | [AI-DRAFT — modeler must confirm: necessary] | [AI-DRAFT — modeler must confirm: Weights may double-count the same underlying factor. Mitigation: check correlation matrix; use PCA if correlations > 0.8.] |
| Q1-A2 | Indicator directions (positive/negative) are correctly identified. | M1, M2, M3 | Normalization direction affects scores. | [AI-DRAFT — modeler must confirm: necessary] | [AI-DRAFT — modeler must confirm: Rankings could be inverted for misclassified indicators.] |

### 2.2 Simplifying

> The "Simplifying" placement of each row below is an AI draft; the modeler confirms or moves the row by ratifying the Type sentinel.

| # | Assumption | Method | Justification | Type | Impact if Relaxed |
|---|-----------|--------|---------------|------|-------------------|
| Q1-A3 | Linear aggregation of indicators is adequate for evaluation. | M1, M2 | Simpler than nonlinear aggregation; common in contest practice. | [AI-DRAFT — modeler must confirm: simplifying] | [AI-DRAFT — modeler must confirm: Nonlinear interactions between indicators would be missed.] |

## 3. Q2 Assumptions (Prediction)

| # | Assumption | Method | Type | Justification | Impact |
|---|-----------|--------|------|---------------|--------|
| Q2-A1 | Historical patterns continue into the forecast period. | M1, M2, M3 | [AI-DRAFT — modeler must confirm: necessary] | Fundamental to all forecasting. | [AI-DRAFT — modeler must confirm: Forecasts become unreliable if structural changes occur.] |
| Q2-A2 | The time series is stationary after differencing. | M2: ARIMA | [AI-DRAFT — modeler must confirm: necessary] | Required for ARIMA model validity. | [AI-DRAFT — modeler must confirm: Non-stationary residuals indicate model misspecification.] |
| Q2-A3 | Demand in different cities is independent. | M1, M2, M3 | [AI-DRAFT — modeler must confirm: simplifying] | Avoids spatial correlation modeling complexity. | [AI-DRAFT — modeler must confirm: Cross-city spillover effects would be missed.] |

## 4. Cross-Subquestion Assumption Dependencies

| From | To | Dependency |
|------|----|-----------|
| Q1-A1 (indicator independence) | Q3-A2 (indicator use in constraints) | If indicators are correlated, Q3's constraint parameters may need adjustment. |
| Q2-A1 (historical patterns continue) | Q3-A1 (demand forecasts as input) | If Q2 forecasts are unreliable, Q3's optimal allocation is based on wrong inputs. |

## 5. Assumptions Requiring Validation

| Assumption | Validation Method | Status |
|-----------|-------------------|--------|
| Q1-A1 (indicator independence) | Compute correlation matrix of indicators | ⏳ Planned |
| Q2-A2 (stationarity after differencing) | ADF test on differenced series | ⏳ Planned |
| Q3-A1 (linearity of cost function) | Check residuals after linear fit | ⏳ Planned |

## 6. Revisions Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-14 | Initial version | From problem parse + candidate pools |
```

# Rules

- Extract assumptions from both the problem statement and the chosen methods. Surfacing candidate assumptions, their source, and a draft justification stays AI-owned.
- Categorize every assumption: necessary vs simplifying, global vs per-question vs method-specific. Keep the necessary/simplifying distinction itself, and keep every assumption tied to a modeling need.
- **The necessary-vs-simplifying label is the modeler's judgment, not the AI's.** Draft it inside `[AI-DRAFT — modeler must confirm: necessary | simplifying]`; do not finalize it on the human's behalf.
- **The impact-if-violated framing is the modeler's judgment, not the AI's.** Draft it inside `[AI-DRAFT — modeler must confirm: <impact if violated>]`; do not finalize it on the human's behalf.
- A surviving `[AI-DRAFT` sentinel in a finalized `planning/model_assumptions.md` is a GATE FAIL — `completeness-auditor` treats it exactly like an unreplaced `<<<HUMAN>>>` sentinel ("not done"). The artifact is not "ready" until every Type and Impact span has been ratified or rewritten by the human.
- Flag assumptions that require validation.
- Do not invent assumptions just to have more. Each must be traceable to the problem or a method.
- Check for conflicts between subquestions' assumptions.
- If an assumption is strong, suggest how to validate or mitigate it.
- Update the document when methods change during iteration (re-draft new Type/Impact spans as `[AI-DRAFT ...]` for the modeler to re-ratify).

# Verification

Before handing off, verify:

- Global assumptions from the problem statement are captured.
- Each subquestion's method-specific assumptions are captured.
- Every assumption is categorized (necessary/simplifying, scope).
- Impact statements are present for necessary assumptions.
- No contradictory assumptions across subquestions.
- Validation methods are suggested for key assumptions.
- The document is traceable to problem parse and method pools.

**B-layer gate (judgment-bearing spans must be human-ratified):**

- No `[AI-DRAFT` or `[MODELER INPUT NEEDED` sentinel survives anywhere in `planning/model_assumptions.md`. A surviving sentinel = NOT done; the gate FAILS exactly like a `<<<HUMAN>>>` sentinel in a C-layer decision artifact. Grep for it: `grep -n '\[AI-DRAFT\|\[MODELER INPUT NEEDED' planning/model_assumptions.md` must return nothing.
- Every assumption's **Type (necessary | simplifying)** cell has been ratified or rewritten by the modeler — the AI must not have finalized this label itself.
- Every assumption's **Impact if Violated / Relaxed** cell has been ratified or rewritten by the modeler — the AI must not have finalized this framing itself.
- If the AI hands off with sentinels still present, it must flag the artifact as DRAFT (modeler ratification pending), not "ready".

# Failure modes

Stop and report a blocker if:

- The problem parse is missing.
- No candidate method pools exist.
- An assumption conflict between subquestions cannot be resolved without changing methods.
- A necessary assumption is clearly false and would invalidate the entire approach.

# Stop conditions

This skill must stop instead of guessing when:

- Insufficient information exists to determine whether an assumption is reasonable.
- An assumption conflict requires the modeler's decision.
- The problem context is too vague to identify implicit assumptions.

When stopping, output:
- the blocker
- what assumptions are still safe to document
- what input is needed
- recommended next action

# Handoff

After producing `planning/model_assumptions.md`, hand off to:

`workflow-orchestrator`
— which will route downstream skills to use this document.

The handoff should include:
- The assumptions document path.
- Key assumptions requiring validation.
- Any unresolved conflicts needing modeler attention.

# Relationship to Paper Writing

The `paper-section-writer` should use this document as the source for the paper's "Model Assumptions" section. The assumptions should be presented in the paper as:

1. Global assumptions first.
2. Per-subquestion assumptions grouped by subquestion.
3. Necessary assumptions highlighted; simplifying assumptions noted.
4. Brief justification for each.
