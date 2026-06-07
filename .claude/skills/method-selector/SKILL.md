---
name: method-selector
description: Compare 2-4 candidate modeling schemes for each subproblem and recommend one execution route based on task type, data, interpretability, literature analysis, and contest constraints.
license: MIT
---

# Purpose

Generate a candidate method pool for each classified subquestion in a mathematical modeling contest.

This skill converts validated problem parse, problem classification, and related-paper analysis into a structured method candidate pool. For each subquestion, it proposes 2-4 meaningfully different candidate modeling schemes, compares them on feasibility, interpretability, data fit, and implementation risk, and recommends a first-round execution priority. It specifies what each method expects as input, what it should output, and how its results should be evaluated.

This skill focuses on generating the candidate pool — the actual method selection happens AFTER multi-round experiments, when the modeler reviews experiment reports and locks in the final method.

This skill does not generate code, clean data, run experiments, create figures, or write paper sections.

# When to use

Use this skill:

- After `problem-parser`, `problem-classifier`, and `related-paper-analyzer` have produced validated artifacts.
- Before data cleaning, code generation, robustness checks, figure planning, or paper writing.
- When the modeler needs a structured set of candidate methods to consider for each subquestion.
- When the user says: "what methods should we try for Q1?", "generate candidate methods", "build the method pool for Q2".
- When the team needs to see multiple modeling approaches before committing to one.

# Preconditions

The following should already exist or be provided:

- A validated problem parse.
- A validated problem classification artifact.
- A related paper analysis artifact at `workspace/papers/related_paper_analysis.md` or an explicit decision to proceed without one.
- Subquestion IDs and dependencies.
- Required outputs for each subquestion.
- Data inventory and known data limitations.
- Contest constraints such as time limit, allowed tools, and submission expectations if available.

If the problem parse or classification is missing, hand back to `workflow-orchestrator`, `problem-parser`, or `problem-classifier`.

# Inputs

Use or request:

- `workspace/problem/problem-parser/problem_parse.json`, if available.
- `workspace/problem/problem-classifier/problem_classification.json`, if available.
- `workspace/papers/related_paper_analysis.md`, if available.
- Parsed subquestions, required outputs, constraints, and dependencies.
- Primary and secondary problem types from `problem-classifier`.
- Transferable ideas, cautions, and comparison notes from `workspace/papers/related_paper_analysis.md`.
- Data inventory, missing data list, units, and known data risks.
- User constraints, such as preferred implementation language, team skill level, contest deadline, or required interpretability.

# Workflow

0. **Granularity alignment (前置颗粒度对齐 — first action on any open-ended request).**
   Before generating a single candidate, ask the modeler ONE most-load-bearing question. Do not produce a default pool that will need 3 revisions. Pick the question that, if answered, narrows the candidate space the most. Typical choices:
   - "This problem looks like both evaluation and classification — which output form do you want? (a ranking score, or a discrete category)?"
   - "Interpretability vs. accuracy — which do you weight more for this contest?"
   - "Do you have a baseline already in mind, or should I propose one?"
   - "Implementation target: Python, MATLAB, or 北太天元?"

   If the user has already given the answer in their request, skip this step. Do NOT ask 3 questions — pick the single most important one. Once answered, proceed to step 1.

1. Read the parsed problem, classification, and literature analysis artifacts.
   - Work subquestion by subquestion.
   - Respect dependencies between subquestions.
   - Do not collapse different subquestions into one generic method pool.

2. For each subquestion, identify the method requirements from:
   - Required output form (ranking, prediction, plan, mechanism explanation, etc.).
   - Available data and missing data.
   - Interpretability requirement.
   - Computational complexity and implementation time.
   - Literature cues (what worked in similar problems).
   - Validation and evaluation criteria.

3. Generate 2-4 candidate schemes per subquestion.
   - Each scheme must be meaningfully different — not cosmetic variants of the same idea.
   - Each scheme must have a clear mathematical idea (what it does, not just a name).
   - Each scheme must specify:
     - **Math idea**: The core mathematical approach in 2-3 sentences.
     - **Strengths**: Why this method fits this subquestion.
     - **Weaknesses**: Known limitations, risks, or assumptions.
     - **Expected output from programmer**: What result files, figures, and metrics the programmer should produce.
     - **Evaluation metric**: How to judge whether this method's output is good.
     - **Implementation difficulty**: easy / medium / hard.
     - **First-round priority**: high (try first) / medium (try if time) / low (backup).
     - **PoC script (REQUIRED — see step 3.5)**: path to a ≤ 30-line runnable script under `methods/Qx/poc/`.
     - **Feasibility number (REQUIRED — see step 3.5)**: a concrete result the PoC produced on small-scale data (e.g., "RMSE=2.4 on 50-sample subset", "TSP-50 solved in 0.3s", "LP infeasible — constraint conflict").

3.5. **Write and run the PoC for every candidate (Gate G2 pass criterion).**
   This is a hard requirement, not optional. A candidate without a runnable PoC + a feasibility number is NOT a validated candidate — it is a hypothesis. The orchestrator will block code generation (Gate G2) until every candidate has a PoC.

   - For each candidate, write a ≤ 30-line Python or MATLAB script that:
     - Imports nothing exotic (numpy / scipy / pandas / sklearn for Python; built-in for MATLAB).
     - Runs the candidate's core math on a **small slice of the actual cleaned data** (e.g., first 50 rows, first 5 cities, downsampled time series). Do NOT use synthetic data — the point is to test feasibility against the real distribution.
     - Outputs one number (or one verdict). Print it.
   - Save scripts to `methods/Qx/poc/<candidate_id>_poc.py` (or `.m`).
   - Run each script and record the number / verdict directly into the candidate's section in `methods/Qx/qx_method_candidates.md` under "Feasibility number".
   - If a PoC fails (crashes, takes too long, produces infeasible output), mark the candidate `[REJECTED — PoC failed: <reason>]` and move the PoC script to `workspace/archived/<Qx>/<candidate>_REJECTED_poc/`. Do NOT keep failed PoCs in the main `methods/Qx/poc/` directory.
   - Candidates that survive PoC are all tagged `[CANDIDATE — PoC PASS]`. The pool must contain ≥ 1 PoC-passing candidate. **Do not promote any of them to `[CHOSEN]` here** — that label is assigned only when the human commits a choice in the decision artifact (step 9 / Gate G2.5).

   The PoC philosophy: "30 lines that fail on real data" is worth more than "5 pages of math that look elegant". Surface infeasibility now, not at code generation.

4. Reject unsuitable methods explicitly + archive them.
   - For each subquestion, identify methods that look tempting but are unsuitable.
   - Give data-driven, time-driven, or interpretability-driven reasons for rejection.
   - For methods rejected by PoC failure, the PoC script must be moved to `workspace/archived/<Qx>/<method>_REJECTED_poc/` (per step 3.5).
   - For methods rejected by analysis only (no PoC needed), record a one-line rejection in the rejected table and in `methods/Qx/qx_method_iteration_log.md`. No script to archive.
   - This prevents the team from wasting time on obviously poor choices, and keeps the main `methods/Qx/poc/` directory containing only `[CANDIDATE]` (PoC-passed) PoCs. **Note: this skill never assigns `[CHOSEN]` — a candidate becomes the chosen method only when the human commits it in the decision artifact (step 9 / Gate G2.5). Until then, every PoC-passing candidate is `[CANDIDATE — PoC PASS]`.**

5. Define baseline requirement.
   - Every subquestion must have at least one baseline method in its candidate pool.
   - The baseline should be the simplest meaningful reference method.
   - State clearly which candidate is the baseline.

6. Suggest — do NOT decide — a first-round priority.
   - You MAY state which 1-2 methods you would try first and why, as an **AI suggestion**. Label it clearly as a suggestion (`ai_suggestion`), not a verdict.
   - State under what conditions the team should try the other candidates.
   - State what the modeler should look for in round 1 experiment reports.
   - Do NOT write "first-round priority: high" as if it were settled. The modeler decides which method to commit to in step 9. Your job is to lay out the trade-offs clearly enough that a human can choose, not to choose for them.

7. Define expected artifacts per method.
   - Required input data.
   - Expected output files (results, figures, metrics).
   - Expected validation checks.
   - How to compare this method against others.

8. Produce the candidate method pool.
   - Save per-subquestion files under `methods/Qx/`.
   - Each file is `methods/Qx/qx_method_candidates.md`.
   - Also produce a global pool summary at `methods/method_pool_summary.md` (optional, useful for overview).

9. Emit the modeler decision artifact, then STOP (Gate G2.5).
   - This is the load-bearing change: which method to build, and why, is the single most graded modeling judgment. The AI must not make it.
   - Create `methods/Qx/decisions/method-selector_modeler_decision.md` following the **Human Decision Artifact Convention** in CLAUDE.md, with:
     - `status: PENDING`, `decided_by: human` (left for the human to confirm), `decision_id: qx_method_choice`.
     - `ai_suggestion`: your best single-line pick + the one reason for it. This is YOUR view, in its own field — it does not count as the decision.
     - `choice`, every `rejected_alternatives[*].reason`, and the `## Modeler's rationale` body left as `<<<HUMAN>>>` sentinels for the modeler to fill.
     - `evidence_refs`: point at the real PoC result files / experiment evidence so the human's rationale can cite a concrete number.
   - Then STOP and tell the modeler exactly what to fill in. Do NOT proceed to data cleaning or code planning. The orchestrator's Gate G2.5 keeps `code_generation_allowed_Qx = false` until this artifact's `status` is `DECIDED` with a non-empty, non-copied human rationale.
   - In **learning mode** (if `planning/session_config.json` says so): withhold `ai_suggestion` until after the human writes their rationale, to avoid anchoring. In **speed mode**: show `ai_suggestion` alongside. Either way the human rationale field, its floor, and the copy/evidence checks are identical.

# Outputs

Produce per-subquestion candidate method pool files:

- `methods/Q1/q1_method_candidates.md`
- `methods/Q2/q2_method_candidates.md`
- `methods/Q3/q3_method_candidates.md`
- `methods/Q4/q4_method_candidates.md` (if needed)
- `methods/method_pool_summary.md` (optional global overview)

Each file must include:

- Subquestion goal (from problem parse).
- Problem type (from classifier).
- Required output.
- Candidate method pool (2-4 methods).
- Rejected methods and reasons.
- Baseline designation.
- First-round priority **as an AI suggestion** (not a verdict).
- Data requirements.
- Evaluation criteria per method.

Plus, separately, the decision artifact `methods/Qx/decisions/method-selector_modeler_decision.md` (PENDING, awaiting the human) — see step 9.

# Output format

Each `methods/Qx/qx_method_candidates.md` must follow this structure:

```markdown
# Qx Method Candidate Pool

## 1. Subquestion Summary
- **Goal**: [from problem parse]
- **Problem type**: [from classifier]
- **Required output**: [what must be delivered]
- **Input data available**: [data inventory relevant to this subquestion]
- **Dependencies**: [which subquestions this one depends on]
- **Constraints**: [key constraints affecting method choice]

## 2. Candidate Method Pool

### Candidate M1: [Short Descriptive Name]  [CANDIDATE — PoC PASS | REJECTED]

- **Math idea**: [2-3 sentences explaining the core mathematical approach]
- **Why it fits this subquestion**: [1-2 sentences]
- **Strengths**:
  - [strength 1]
  - [strength 2]
- **Weaknesses**:
  - [weakness 1]
  - [weakness 2]
- **Expected programmer outputs**:
  - Result files: [list expected output files]
  - Figures: [list expected figures]
  - Metrics: [list expected metrics]
- **Evaluation criteria**: [how to judge if this method worked well]
- **Implementation difficulty**: easy / medium / hard
- **First-round priority**: high / medium / low
- **Data requirements**: [specific data fields needed]
- **Literature support**: [reference to paper analysis if applicable, or "no direct literature support"]
- **Estimated implementation time**: [rough estimate: hours]
- **PoC script**: `methods/Qx/poc/m1_poc.py` (or `.m`) — ≤ 30 lines, runs on small slice of cleaned data
- **Feasibility number**: e.g., "RMSE = 2.4 on first 50 samples, runtime 0.3s" (or "PoC failed: matrix singular when n<10" if rejected)
- **PoC verdict**: PASS (proceed to full implementation) | FAIL → [REJECTED] + archive

### Candidate M2: [Short Descriptive Name]
[Same structure]

### Candidate M3: [Short Descriptive Name]
[Same structure]

### Candidate M4: [Short Descriptive Name] (if applicable)
[Same structure]

## 3. Rejected Methods

| Method | Reason for Rejection |
|--------|---------------------|
| [method name] | [specific data-driven, time-driven, or interpretability-driven reason] |

## 4. Baseline Designation

- **Baseline**: [which candidate serves as baseline]
- **Why this baseline**: [reason — simplest, most transparent, easiest to implement]

## 5. First-Round Priority (AI suggestion — the modeler decides in the decision artifact)

- **AI would try first**: [1-2 method names] — *suggestion only, not a verdict*
- **Reason for the suggestion**: [why these look most promising to try first]
- **When to try others**: [conditions under which remaining candidates should be tested]
- **What to look for in round 1**: [what the modeler should check in the experiment report]
- **Decision pending**: the actual first-round choice is recorded by the modeler in `methods/Qx/decisions/method-selector_modeler_decision.md` (Gate G2.5). No candidate is `[CHOSEN]` until the human commits it there.

## 6. Cross-Method Comparison Matrix

| Criterion | M1 | M2 | M3 | M4 |
|-----------|---|---|---|---|
| Interpretability | [rating] | [rating] | [rating] | [rating] |
| Data requirement satisfaction | [rating] | [rating] | [rating] | [rating] |
| Implementation complexity | [rating] | [rating] | [rating] | [rating] |
| Literature support | [rating] | [rating] | [rating] | [rating] |
| Expected accuracy/fit | [rating] | [rating] | [rating] | [rating] |
| Robustness potential | [rating] | [rating] | [rating] | [rating] |

## 7. Handoff

- **Next skill**: `model-code-analyzer`
- **Required inputs for next skill**:
  - This candidate pool document
  - Cleaned data (after `data-auditor-cleaner`)
  - Implementation target (python / matlab)
```

Also produce a `methods/method_pool_summary.md` if multiple subquestions are being planned:

```markdown
# Method Pool Summary (All Subquestions)

| Subquestion | Type | # Candidates | Baseline | First-Round Priority | Rejected |
|-------------|------|-------------|----------|---------------------|----------|
| Q1 | evaluation | 3 | M1 (equal-weight) | M2, M1 | Deep learning (data insufficient) |
| Q2 | prediction | 3 | M1 (moving average) | M2, M1 | LSTM (time series too short) |
| Q3 | optimization | 2 | M1 (greedy) | M1, M2 | Genetic algorithm (overkill) |
```

# Method family guide

Use this section to select candidate method families. These are guidelines, not mandatory choices.

## Evaluation

Candidate options:
- equal-weight normalized scoring (always consider as baseline)
- entropy-weight TOPSIS
- AHP + TOPSIS (if subjective weights are justifiable)
- PCA-assisted comprehensive evaluation (if indicators are highly correlated)
- grey relational analysis
- fuzzy comprehensive evaluation
- RSR (rank sum ratio) evaluation

Use when: output is score, ranking, grade, risk level, priority, or comparison.

Check: indicator justification, positive/negative direction, normalization, weight source, ranking stability.

Avoid: arbitrary weights with no explanation, black-box scoring without labeled data, repeated indicators double-counting.

## Prediction

Candidate options:
- mean or last-value baseline (always consider)
- linear regression (always consider as simple baseline)
- ARIMA / SARIMA (for time series with clear temporal structure)
- exponential smoothing
- grey prediction GM(1,1) (for small-sample monotonic sequences)
- random forest regression (for tabular nonlinear data)
- gradient boosting (XGBoost/LightGBM, if justified)
- ensemble (if multiple models are justified)

Use when: output is future value, trend, forecast interval, missing value estimate, or uncertainty estimate.

Check: train-test split or validation scheme, error metrics (MAE, RMSE, MAPE), residuals, extrapolation limits, feature leakage.

Avoid: high-capacity models with tiny data, prediction without error metrics, claiming future accuracy from training fit alone, deep learning when data < 1000 samples.

## Optimization

Candidate options:
- greedy heuristic (always consider as baseline)
- linear programming (for linear objectives and constraints)
- integer programming (for discrete decisions)
- nonlinear programming (for nonlinear objectives or constraints)
- dynamic programming (for sequential decisions)
- multi-objective optimization (for trade-off problems)
- network flow / shortest path (for graph-based allocation)
- simulated annealing or genetic algorithm (for hard combinatorial cases, use only if exact methods are infeasible)

Use when: output is a decision plan, allocation, route, schedule, assignment, maximum, minimum, or feasible strategy.

Check: decision variables, state variables, parameters, objective function, constraints, feasibility, implementable final plan, sensitivity to weights or constraints.

Avoid: objective functions with vague meaning, missing constraints, final result that is only an optimal value without a plan, heuristics without baseline comparison.

## Mechanism

Candidate options:
- simplified algebraic relationship (baseline)
- differential equations (ODE/PDE)
- difference equations (discrete time)
- compartment models (SIR, SEIR, etc.)
- conservation laws
- system dynamics
- mechanism + parameter fitting (hybrid)

Use when: output must explain a process, dynamic mechanism, physical relation, biological spread, flow, motion, growth, or decay.

Check: assumptions, units, parameter sources, validation against data or common sense, boundary conditions.

Avoid: equations with undefined variables, parameters with no source, mechanism claims unsupported by validation.

## Classification / Clustering

Candidate options:
- rule-based classification (baseline)
- k-means (baseline clustering)
- decision tree
- logistic regression
- random forest
- SVM
- clustering with validation index (silhouette, Davies-Bouldin)
- anomaly detection (isolation forest, LOF)

Use when: output is class label, cluster, segment, group, or anomaly.

Check: feature scaling, class balance, validation metric, cluster number selection, interpretability.

Avoid: arbitrary cluster counts, classification without labels, accuracy-only reporting under class imbalance.

## Graph / Routing

Candidate options:
- direct distance rule (baseline)
- greedy nearest-neighbor (baseline)
- Dijkstra shortest path
- A* search
- minimum spanning tree (Prim/Kruskal)
- max flow / min cut
- Hungarian algorithm (matching)
- vehicle routing heuristics (Clarke-Wright, sweep)
- TSP/VRP exact or heuristic

Use when: problem involves nodes, edges, paths, networks, flows, routes, matching, or connectivity.

Check: graph abstraction, edge weights, node definitions, feasibility constraints, static vs dynamic assumptions.

Avoid: graph models that ignore real constraints, unjustified edge weights, routes that are mathematically valid but practically infeasible.

## Simulation

Candidate options:
- deterministic scenario comparison (baseline)
- Monte Carlo simulation
- discrete-event simulation
- agent-based simulation
- stochastic process modeling
- scenario analysis

Use when: output is a stochastic distribution, scenario result, repeated process outcome, or policy comparison under uncertainty.

Check: random seed, number of trials, parameter distributions, confidence intervals or summary statistics, scenario assumptions.

Avoid: simulation without statistical summary, hidden random assumptions, too few trials, unverifiable scenario generation.

## Data Analysis

Candidate options:
- descriptive statistics (baseline)
- correlation analysis
- hypothesis testing
- factor analysis
- principal component analysis
- regression explanation
- exploratory visualization

Use when: output is pattern discovery, factor identification, descriptive insight, or relationship analysis.

Check: correlation vs causation, data quality, unit consistency, figure relevance, connection to later modeling steps.

Avoid: decorative figures without modeling purpose, causal claims from correlation alone, analysis not feeding any subquestion.

# Rules

- Generate 2-4 candidate methods per subquestion. If only 1 is feasible, explain why and flag the risk.
- Each candidate must have a distinct mathematical idea — not just a different library or parameter.
- Every subquestion must have a baseline candidate designated.
- Every candidate must specify what the programmer should output and how to evaluate it.
- **PoC is mandatory** — every candidate must have a runnable ≤ 30-line PoC + a feasibility number. A candidate without a PoC is not a candidate; it's a hypothesis. Gate G2 blocks code generation on PoC absence.
- **Before generating the pool, ask one most-load-bearing question** to align granularity with the modeler (Workflow step 0). Do not default-produce 3 versions and get them all rejected.
- **PoC failures must be archived**, not buried. Move failed PoC scripts to `workspace/archived/<Qx>/<candidate>_REJECTED_poc/` and mark the candidate `[REJECTED]` with a one-line reason. The main `methods/Qx/poc/` directory contains only `[CANDIDATE]` (PoC-passed) PoCs.
- Unsuitable methods must be explicitly rejected with reasons.
- First-round priority is stated **only as an AI suggestion** — never as a decided verdict, never `[CHOSEN]`.
- **Do not select ANY method — not the final one, not the first-round one.** This skill emits PoC-passed candidates + a suggestion + a PENDING decision artifact. The human commits the choice at Gate G2.5; only then does a candidate become `[CHOSEN]`. Do not infer the choice from your own suggestion, and do not fill the human rationale field.
- Do not generate code.
- Do not clean data.
- Do not write paper text.
- Do not fabricate data, metrics, or results.
- Mark high-risk methods as high-risk.
- Preserve uncertainty inherited from previous stages.

# Verification

Before handing off, verify:

- Every subquestion has 2-4 candidate methods or an explicit justification for fewer.
- Every subquestion has a baseline designated.
- Every candidate has: math idea, strengths, weaknesses, expected outputs, evaluation criteria, difficulty, priority, **PoC script path, feasibility number, PoC verdict**.
- At least one candidate passed its PoC and is marked `[CANDIDATE — PoC PASS]` per subquestion. (No `[CHOSEN]` here — that is the human's call at G2.5.)
- All `[REJECTED]` PoCs have been moved to `workspace/archived/`.
- Unsuitable methods are explicitly listed and rejected with reasons.
- First-round priority is presented as an AI suggestion, clearly not a verdict.
- Cross-method comparison matrix is filled for all criteria.
- **The decision artifact `methods/Qx/decisions/method-selector_modeler_decision.md` exists with `status: PENDING`**, `ai_suggestion` filled, and `choice` / rationale left as `<<<HUMAN>>>` for the modeler.
- The next skill is `data-auditor-cleaner` for data prep, but **Gate G2.5 blocks code generation** until the modeler fills the decision artifact (`status: DECIDED`). Hand back to the modeler, not forward to code planning.

# Failure modes

Stop and report a blocker if:

- No validated problem classification exists.
- Required outputs are unknown.
- Data availability is too unclear to select feasible methods.
- The only plausible methods require data that is unavailable or forbidden by contest rules.
- A subquestion's output requirements are so vague that no method can be meaningfully proposed.

# Stop conditions

This skill must stop instead of guessing when:

- Selecting a method would require inventing data fields, labels, constraints, or evaluation metrics.
- A subquestion cannot be linked to a required output.
- A method choice depends on an unavailable attachment.
- The user asks for final numerical results, code, or paper text before the candidate pool is complete.

When stopping, output:

- the blocker
- why it matters
- safe partial candidate pools if any
- missing information needed
- recommended next action

# Handoff

After producing the candidate method pool, hand off to:

`data-auditor-cleaner`
— to prepare data for the methods in the pool.

The handoff should include:

- Candidate method pool files (per subquestion).
- Required data fields per method.
- Baseline designations.
- First-round execution recommendations.
- Implementation difficulty notes.

If no external or tabular data is needed, the workflow owner may route next to `model-code-analyzer`.

# Examples

## Example 1: Evaluation problem candidate pool

Input state:
- Q1: evaluate and rank cities by resilience.
- Problem type: evaluation.
- Data: multiple indicators with mixed units.
- Literature: TOPSIS and entropy weighting commonly used in similar evaluation problems.

Output (`methods/Q1/q1_method_candidates.md`):

```markdown
# Q1 Method Candidate Pool

## 2. Candidate Method Pool

### Candidate M1: Equal-Weight Normalized Scoring

- **Math idea**: Normalize all indicators to [0,1] range (with direction handling), then compute a weighted sum with equal weights. Rank cities by total score descending.
- **Why it fits**: Simplest possible multi-indicator evaluation; transparent and easy to explain.
- **Strengths**:
  - No weight justification needed (all indicators treated equally)
  - Trivial to implement and verify
  - Serves as baseline for all other methods
- **Weaknesses**:
  - Cannot distinguish indicator importance
  - May overweight redundant indicators
- **Expected programmer outputs**:
  - Result files: `equal_weight_scores.csv`, `equal_weight_ranking.csv`
  - Figures: `indicator_distribution.png`, `score_bar_chart.png`
  - Metrics: score variance, ranking list
- **Evaluation criteria**: Ranking interpretability, score differentiation
- **Implementation difficulty**: easy
- **First-round priority**: high (baseline — always implement first)
- **Data requirements**: indicator matrix (all columns)
- **Estimated implementation time**: 0.5 hours

### Candidate M2: Entropy-Weight TOPSIS

- **Math idea**: Use information entropy of each indicator to compute objective weights (higher dispersion → higher weight). Then apply TOPSIS: find ideal best/worst virtual alternatives, compute each city's relative closeness to the ideal best, rank by closeness.
- **Why it fits**: Entropy provides objective data-driven weights (no subjective input needed). TOPSIS produces clear comparable scores. Widely used in mathematical modeling contests.
- **Strengths**:
  - Objective weights (no subjective bias)
  - Well-established in contest literature
  - Produces differentiable scores
- **Weaknesses**:
  - Entropy may overweight high-variance indicators that are not practically important
  - Sensitive to normalization method choice
- **Expected programmer outputs**:
  - Result files: `entropy_weights.csv`, `topsis_scores.csv`, `topsis_ranking.csv`
  - Figures: `weight_bar_chart.png`, `score_distribution.png`, `ranking_comparison.png` (vs baseline)
  - Metrics: weight values, relative closeness scores, ranking stability
- **Evaluation criteria**: Weight interpretability, ranking differentiation vs baseline, top-K stability
- **Implementation difficulty**: medium
- **First-round priority**: high (recommended main method)
- **Data requirements**: indicator matrix (all columns), indicator direction (positive/negative)
- **Estimated implementation time**: 2 hours

### Candidate M3: PCA-Assisted Evaluation

- **Math idea**: Apply PCA to reduce correlated indicators to independent principal components. Use component scores (weighted by explained variance) as composite evaluation scores.
- **Why it fits**: Handles indicator correlation automatically. Reduces dimensionality if many indicators exist.
- **Strengths**:
  - Handles multicollinearity well
  - Automatic dimensionality reduction
- **Weaknesses**:
  - Reduced interpretability (principal components are linear combinations)
  - May lose information from small-variance components that are practically important
  - Harder to explain to readers
- **Expected programmer outputs**:
  - Result files: `pca_loadings.csv`, `pca_scores.csv`, `pca_ranking.csv`
  - Figures: `scree_plot.png`, `biplot.png`, `pca_score_plot.png`
  - Metrics: explained variance ratio, component loadings, ranking vs TOPSIS comparison
- **Evaluation criteria**: Information retention (explained variance), consistency with M2 ranking
- **Implementation difficulty**: medium
- **First-round priority**: medium (try if M1/M2 results need validation)
- **Data requirements**: indicator matrix (all numeric columns)
- **Estimated implementation time**: 1.5 hours

## 3. Rejected Methods

| Method | Reason for Rejection |
|--------|---------------------|
| AHP + TOPSIS | Requires subjective pairwise comparison matrix; cannot be objectively justified without domain expert input |
| Deep neural network scoring | Insufficient labeled data; no ground-truth scores for training; weak interpretability |
| Fuzzy comprehensive evaluation | Membership function design is arbitrary without domain knowledge; similar to weighted scoring with extra complexity |

## 4. Baseline Designation

- **Baseline**: M1 (Equal-Weight Normalized Scoring)
- **Why**: Simplest transparent reference; any improvement over equal weights must be demonstrated

## 5. First-Round Execution Recommendation

- **Implement first**: M1 and M2
- **Reason**: M1 establishes the baseline; M2 is the recommended main method. M3 is a validation backup.
- **When to try M3**: If M2 ranking is suspicious (dominated by one or two high-variance indicators) or if indicators are highly correlated
- **What to look for in round 1**: Does M2 produce meaningfully different weights? Does the ranking differ from M1? Is the ranking stable?

## 6. Cross-Method Comparison Matrix

| Criterion | M1 Equal-Weight | M2 Entropy-TOPSIS | M3 PCA |
|-----------|---|---|---|
| Interpretability | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Data requirement satisfaction | ★★★★★ | ★★★★★ | ★★★★★ |
| Implementation complexity | ★★★★★ | ★★★☆☆ | ★★★☆☆ |
| Literature support | ★★★☆☆ | ★★★★★ | ★★★☆☆ |
| Expected differentiation | ★★☆☆☆ | ★★★★☆ | ★★★★☆ |
| Robustness potential | ★★★★★ | ★★★★☆ | ★★★☆☆ |
```

## Example 2: Prediction problem candidate pool

Input state:
- Q2: predict future demand.
- Problem type: prediction.
- Data: historical time series, 36 months.
- Literature: ARIMA and grey prediction common for short series.

Output (summary):
```markdown
### Candidate M1: Moving Average Baseline
- Math idea: Forecast = average of last K observations.
- Baseline: Yes.
- First-round priority: high.

### Candidate M2: ARIMA
- Math idea: Model time series as autoregressive integrated moving average process; fit order via AIC; forecast with confidence intervals.
- First-round priority: high.

### Candidate M3: Grey Prediction GM(1,1)
- Math idea: Accumulate data to reduce noise, fit first-order differential equation, inverse-accumulate to get predictions.
- First-round priority: medium (especially useful if data is short and monotonic).

### Rejected:
| LSTM | Data length (36 points) is insufficient for deep learning; high implementation risk |

### Baseline: M1 (Moving Average)
```

## Example 3: Optimization problem candidate pool

Input state:
- Q3: allocate limited resources to demand points.
- Problem type: optimization.
- Data: demand estimates, resource capacity, cost parameters.

Output (summary):
```markdown
### Candidate M1: Greedy Allocation (Baseline)
- Math idea: Sort demand points by priority, allocate resources greedily from highest to lowest until capacity exhausted.
- Baseline: Yes.

### Candidate M2: Integer Linear Programming
- Math idea: Define binary allocation variables, minimize total cost subject to capacity and demand constraints, solve with branch-and-bound.

### Candidate M3: Multi-Objective Optimization
- Math idea: Extend M2 with additional objectives (fairness, coverage) using weighted sum or epsilon-constraint method.

### Rejected:
| Genetic Algorithm | Overkill; problem size is manageable with exact methods; GA adds randomness and reduces reproducibility |

### Baseline: M1 (Greedy Allocation)
```
