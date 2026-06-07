---
name: problem-classifier
description: Classify each subquestion into standard mathematical modeling problem types.
license: MIT
---

# Purpose

Classify each parsed subquestion into standard mathematical modeling problem types.

This skill converts a validated problem parse into a problem-type map. It identifies the core task type of each subquestion, explains the classification reason, lists candidate method families at a high level, and flags common misclassification risks.

This skill does not select the final model, generate code, clean data, or write paper sections.

# When to use

Use this skill:

- After `problem-parser` has produced a validated problem parse.
- Before `related-paper-analyzer` and `method-selector`.
- When subquestions need to be mapped to standard mathematical modeling types.
- When a problem appears mixed and the team needs to separate evaluation, prediction, optimization, mechanism, classification, graph, simulation, or hybrid components.
- When the team is tempted to choose a model before clarifying the task type.

# Preconditions

A validated problem parse should exist and include:

- subquestions
- goals
- objects
- constraints
- data inventory
- required outputs
- preliminary variables or relationships if available
- ambiguity and risk notes

If the problem parse is missing or incomplete, hand back to `problem-parser`.

# Inputs

Use or request:

- `workspace/problem/problem-parser/problem_parse.json`, if available.
- Parsed subquestions from `problem-parser`.
- Goals, objects, constraints, data, and required outputs.
- Preliminary variables, controllable quantities, observable quantities, and relationships.
- Ambiguity and risk flags from the parsing stage.
- User notes about contest constraints or team implementation limits, if relevant.

# Workflow

1. Read the parsed subquestions.
   - Classify each subquestion separately.
   - Do not assign one coarse type to the whole problem unless the problem truly has only one task.

2. Identify the main verb and expected output.
   - Evaluation tasks often ask to evaluate, rank, compare, score, classify quality, or assess risk.
   - Prediction tasks often ask to forecast, estimate, infer future values, fill unknown trends, or quantify uncertainty.
   - Optimization tasks often ask to choose, allocate, schedule, route, maximize, minimize, or design a feasible plan.
   - Mechanism tasks often ask to explain system behavior through equations, physical rules, dynamic processes, or causal structure.
   - Classification or clustering tasks often ask to group, label, segment, identify categories, or detect abnormal samples.
   - Graph or routing tasks often involve nodes, edges, paths, networks, flows, connectivity, matching, or traversal.
   - Simulation tasks often require scenario generation, stochastic processes, agent behavior, Monte Carlo trials, or repeated process imitation.
   - Hybrid tasks combine multiple task types and should be decomposed by subquestion or modeling layer.

3. Suggest the primary type — but do not finalize the framing.
   - Emit the AI's pick as `ai_suggested_type` with an `ai_suggestion_confidence`, keeping it clearly the AI's suggestion.
   - Use the required output as the main decision criterion and explain the reasoning, so the human has something concrete to ratify.
   - Prefer the type that determines how results will be judged.
   - The primary problem-type label is load-bearing framing — it steers `method-selector`. It is the human's call, not the AI's. Leave `modeler_chosen_type` and `framing_rationale` as `[MODELER INPUT NEEDED: ...]` sentinels for the modeler to author. Do NOT pre-fill them by copying `ai_suggested_type`.

4. Determine the secondary type if needed.
   - Add a secondary type only when it materially affects method selection.
   - Do not list many secondary types just to be comprehensive.

5. Identify candidate method families.
   - List broad method families, not final models.
   - Keep candidates tied to the classified task type.
   - Mark candidate methods as tentative and subject to `method-selector`.

6. Flag unsuitable or risky directions.
   - Mark methods that appear tempting but are unsupported by data, output requirements, interpretability needs, or contest constraints.
   - Flag deep learning, black-box models, or complex heuristics when data volume, explainability, or implementation time is insufficient.

7. Produce a classification artifact.
   - Keep the output structured and concise.
   - Preserve ambiguity instead of forcing false certainty.
   - Save the paired outputs under `workspace/problem/problem-classifier/`.
   - Recommend `related-paper-analyzer` as the next skill if classification is complete.

# Outputs

Produce a problem classification artifact as paired outputs:

- `workspace/problem/problem-classifier/problem_classification.json`
- `workspace/problem/problem-classifier/problem_classification.md`

The artifacts should contain:

- `classification_summary`
- `subquestion_classifications`
- `global_structure`
- `candidate_method_families`
- `unsuitable_directions`
- `classification_risks`
- `ambiguities`
- `recommended_next_skill`

# Output format

Prefer this JSON-compatible structure for `workspace/problem/problem-classifier/problem_classification.json`:

```json
{
  "classification_summary": {
    "overall_pattern": "hybrid",
    "reason": "The problem combines evaluation, prediction, and optimization across different subquestions."
  },
  "subquestion_classifications": [
    {
      "id": "Q1",
      "ai_suggested_type": "evaluation",
      "ai_suggestion_confidence": "high",
      "modeler_chosen_type": "[MODELER INPUT NEEDED: confirm or override the primary type — the AI suggests 'evaluation']",
      "framing_rationale": "[MODELER INPUT NEEDED: which type, and why this framing over the alternative — e.g. Q2 is evaluation not prediction because the graded output is a ranking, not a future value]",
      "secondary_type": "data_analysis",
      "classification_reason": "The subquestion asks for comparable scores or rankings based on multiple indicators.",
      "output_driver": [
        "ranking",
        "score",
        "comparative explanation"
      ],
      "candidate_method_families": [
        "indicator system construction",
        "weighting methods",
        "multi-criteria evaluation",
        "dimensionality reduction"
      ],
      "unsuitable_directions": [
        {
          "direction": "time series forecasting",
          "reason": "The required output is a ranking or score, not a future value."
        }
      ],
      "risk_flags": [
        "weight source must be justified",
        "positive and negative indicators must be normalized consistently"
      ]
    }
  ],
  "global_structure": {
    "is_hybrid": true,
    "dependency_pattern": [
      {
        "from": "Q1",
        "to": "Q2",
        "reason": "Q2 may use Q1 scores as explanatory variables or inputs."
      }
    ],
    "suggested_workflow_order": [
      "Q1",
      "Q2",
      "Q3"
    ]
  },
  "classification_risks": [
    "Do not force the whole problem into one type if subquestions differ."
  ],
  "ambiguities": [
    "Ambiguity inherited from the problem parse, if any."
  ],
  "recommended_next_skill": "related-paper-analyzer"
}
```

Also produce `workspace/problem/problem-classifier/problem_classification.md` with the same fields in readable Markdown form.

**B-layer human-confirmation field (load-bearing framing).** The primary problem-type label steers method selection, so the AI suggests but the human decides. For every subquestion:

- `ai_suggested_type` — the AI's pick (the old `primary_type`). The AI authors this, with `ai_suggestion_confidence` and a `classification_reason`.
- `modeler_chosen_type` — the confirmed primary type. Emit it as `[MODELER INPUT NEEDED: confirm or override the primary type — the AI suggests '<ai_suggested_type>']`. The AI must NOT fill this in.
- `framing_rationale` — emit as `[MODELER INPUT NEEDED: which type, and why this framing over the alternative — e.g. Q2 is evaluation not prediction because…]`. The AI must NOT fill this in.

A surviving `[MODELER INPUT NEEDED` (or `[AI-DRAFT`) sentinel in a finalized classification artifact is a Gate G1 FAIL — `completeness-auditor` already treats these sentinels as "not done", exactly like the C-layer `<<<HUMAN>>>` decision sentinel. The human must replace both sentinels before classification is "ready". Carry `ai_suggested_type` forward in every example below; never replace it with a finalized `primary_type`.

# Standard problem types

Use these labels consistently:

- `evaluation`
- `prediction`
- `optimization`
- `mechanism`
- `classification-clustering`
- `graph-routing`
- `simulation`
- `data-analysis`
- `hybrid`

# Classification guide

## Evaluation

Use when the main output is:

- score
- ranking
- comparison
- grade
- risk level
- comprehensive assessment
- priority order

Common cues:

- evaluate
- rank
- compare
- assess
- measure quality
- determine importance
- build an index system

Common risks:

- indicators are not justified
- positive and negative indicators are mixed incorrectly
- weights are arbitrary
- repeated indicators inflate importance
- ranking lacks sensitivity analysis

Candidate method families:

- indicator system construction
- normalization
- weighting
- multi-criteria decision analysis
- dimensionality reduction
- grey relational analysis
- fuzzy evaluation

## Prediction

Use when the main output is:

- future value
- unknown value estimate
- trend
- forecast interval
- error or uncertainty description

Common cues:

- predict
- forecast
- estimate
- infer future
- trend
- extrapolate
- fill unknown values

Common risks:

- training fit is mistaken for future generalization
- no test or validation split
- no error metric
- no explanation of failure cases
- long-term extrapolation is overclaimed

Candidate method families:

- regression
- time series analysis
- grey prediction
- machine learning regression
- ensemble prediction
- uncertainty estimation

## Optimization

Use when the main output is:

- decision plan
- allocation scheme
- schedule
- route
- maximum or minimum value
- feasible strategy under constraints

Common cues:

- choose
- allocate
- schedule
- assign
- route
- maximize
- minimize
- optimize
- design a plan

Common risks:

- decision variables are not separated from state variables
- objective function is vague
- constraints are incomplete
- feasibility is not checked
- final result gives a number but not an implementable plan

Candidate method families:

- linear programming
- integer programming
- nonlinear programming
- dynamic programming
- multi-objective optimization
- heuristic search
- network optimization

## Mechanism

Use when the main output is:

- equation-based explanation
- dynamic process model
- causal structure
- physical or biological mechanism
- interpretable system evolution

Common cues:

- explain mechanism
- describe process
- derive relationship
- simulate dynamics from rules
- model spread, motion, flow, growth, or decay

Common risks:

- assumptions are too strong
- parameters have no source
- units are inconsistent
- model is not validated against data or common sense

Candidate method families:

- differential equations
- difference equations
- compartment models
- conservation laws
- physical constraints
- system dynamics

## Classification-clustering

Use when the main output is:

- category label
- group assignment
- segment
- anomaly label
- sample type

Common cues:

- classify
- cluster
- group
- identify category
- segment
- detect abnormal samples

Common risks:

- class labels are unclear
- number of clusters is arbitrary
- feature scaling is ignored
- validation metric is missing

Candidate method families:

- supervised classification
- unsupervised clustering
- anomaly detection
- feature engineering
- dimensionality reduction

## Graph-routing

Use when the main output is:

- path
- network structure
- connectivity
- route plan
- matching
- flow allocation
- node importance

Common cues:

- network
- path
- route
- nodes
- edges
- connection
- shortest path
- flow
- matching

Common risks:

- graph abstraction loses important constraints
- edge weights are not justified
- route feasibility is not checked
- static network assumptions hide dynamic constraints

Candidate method families:

- shortest path
- minimum spanning tree
- network flow
- matching
- vehicle routing
- graph centrality
- graph search

## Simulation

Use when the main output is:

- scenario result
- stochastic outcome distribution
- repeated trial behavior
- process imitation
- policy comparison under uncertainty

Common cues:

- simulate
- scenario
- random
- probability distribution
- Monte Carlo
- dynamic process
- agent behavior

Common risks:

- random seed is not fixed
- number of trials is insufficient
- simulation assumptions are hidden
- outputs are not statistically summarized

Candidate method families:

- Monte Carlo simulation
- discrete-event simulation
- agent-based simulation
- stochastic process modeling
- scenario analysis

## Data-analysis

Use when the main output is:

- descriptive finding
- correlation pattern
- feature relationship
- distribution summary
- data insight before modeling

Common cues:

- analyze data
- describe pattern
- explore relationship
- identify influencing factors
- summarize characteristics

Common risks:

- correlation is overstated as causation
- figures are decorative rather than explanatory
- no connection to later modeling steps

Candidate method families:

- descriptive statistics
- correlation analysis
- hypothesis testing
- exploratory data analysis
- factor analysis

## Hybrid

Use when:

- different subquestions require different task types
- one stage produces inputs for another stage
- the solution combines evaluation, prediction, optimization, simulation, or mechanism modeling

Common risks:

- treating the whole problem as one type
- skipping dependencies between subquestions
- using one model to answer all tasks poorly

Candidate method families:

- staged modeling workflow
- modular pipeline
- evaluation-then-prediction
- prediction-then-optimization
- mechanism-plus-data fitting
- simulation-plus-optimization

# Rules

- Classify by subquestion, not by the entire problem title.
- Use the required output to determine the primary type.
- The primary problem-type label is load-bearing framing that steers `method-selector`. The AI suggests it (`ai_suggested_type` + confidence + reason); the human owns the final framing. Emit `modeler_chosen_type` and `framing_rationale` as `[MODELER INPUT NEEDED: ...]` sentinels and let the modeler author them.
- Do not author, pre-fill, or copy `ai_suggested_type` into `modeler_chosen_type` or `framing_rationale` on the human's behalf.
- A surviving `[MODELER INPUT NEEDED` or `[AI-DRAFT` sentinel in the finalized classification artifact is a Gate G1 FAIL — treat it exactly like the C-layer `<<<HUMAN>>>` sentinel; classification is not "ready" until the human replaces it.
- Do not select the final model.
- Do not generate code.
- Do not write paper text.
- Do not over-list candidate methods.
- Do not recommend complex or black-box methods without data and interpretability support.
- Do not hide classification uncertainty.
- Do not override ambiguities inherited from `problem-parser`.
- Do not move directly to `model-code-analyzer`.

# Verification

Before handing off, verify:

- Every parsed subquestion has an `ai_suggested_type` (the AI's suggested primary type) with a confidence and reason.
- Every parsed subquestion still carries the `[MODELER INPUT NEEDED: ...]` sentinels for `modeler_chosen_type` and `framing_rationale` — the AI must not have authored or copied them. A surviving sentinel is a Gate G1 FAIL the human must clear (it confirms the framing has not yet been ratified); the AI hands off with these sentinels intact, not pre-filled.
- Secondary types are used only when necessary.
- Classification reasons refer to task wording, required output, and data conditions.
- Candidate method families are broad, not final model choices.
- Unsuitable directions and classification risks are listed.
- Hybrid structure and dependencies are identified if present.
- The next skill is `related-paper-analyzer`.

# Failure modes

Stop and report a blocker if:

- No validated problem parse exists.
- Subquestions are missing or too vague to classify.
- Required outputs are unknown.
- A key attachment or data description is needed to determine the task type.
- The user asks for final model selection before classification is complete.

# Stop conditions

This skill must stop instead of guessing when:

- Multiple classifications would lead to materially different modeling workflows.
- The task wording is too incomplete to infer the required output.
- The classification depends on unavailable data fields or missing contest requirements.
- Continuing would require inventing the user's intent.

When stopping, output:

- the blocker
- why it matters
- the minimum information needed
- the partial classifications that are still safe
- the recommended next action

# Handoff

After producing a validated classification artifact, hand off to:

`related-paper-analyzer`

The handoff should include:

- each subquestion ID
- `ai_suggested_type` (the AI's suggested primary type) plus the `modeler_chosen_type` / `framing_rationale` status (confirmed by the human, or still a `[MODELER INPUT NEEDED]` sentinel)
- secondary type if needed
- classification reason
- candidate method families
- unsuitable directions
- risk flags
- dependency pattern

Do not hand off to `method-selector` directly unless literature analysis has already been completed or intentionally skipped.

# Examples

## Example 1: Evaluation, prediction, optimization chain

Input state:

- Q1 asks to rank cities by resilience.
- Q2 asks to forecast next-year demand.
- Q3 asks to allocate limited resources.

Output:

```json
{
  "classification_summary": {
    "overall_pattern": "hybrid",
    "reason": "The problem combines evaluation, prediction, and optimization in sequence."
  },
  "subquestion_classifications": [
    {
      "id": "Q1",
      "ai_suggested_type": "evaluation",
      "ai_suggestion_confidence": "high",
      "modeler_chosen_type": "[MODELER INPUT NEEDED: confirm or override the primary type — the AI suggests 'evaluation']",
      "framing_rationale": "[MODELER INPUT NEEDED: which type, and why this framing over the alternative — e.g. Q1 is evaluation not prediction because the graded output is a ranking, not a future value]",
      "secondary_type": "data-analysis",
      "classification_reason": "Q1 asks for city ranking based on multiple indicators.",
      "candidate_method_families": [
        "indicator system construction",
        "weighting methods",
        "multi-criteria evaluation"
      ],
      "risk_flags": [
        "indicator selection and weight source must be justified"
      ]
    },
    {
      "id": "Q2",
      "ai_suggested_type": "prediction",
      "ai_suggestion_confidence": "high",
      "modeler_chosen_type": "[MODELER INPUT NEEDED: confirm or override the primary type — the AI suggests 'prediction']",
      "framing_rationale": "[MODELER INPUT NEEDED: which type, and why this framing over the alternative — e.g. Q2 is prediction not evaluation because the graded output is a future demand value, not a ranking]",
      "secondary_type": "data-analysis",
      "classification_reason": "Q2 asks for future demand estimates.",
      "candidate_method_families": [
        "regression",
        "time series analysis",
        "ensemble prediction"
      ],
      "risk_flags": [
        "prediction error and generalization must be checked"
      ]
    },
    {
      "id": "Q3",
      "ai_suggested_type": "optimization",
      "ai_suggestion_confidence": "high",
      "modeler_chosen_type": "[MODELER INPUT NEEDED: confirm or override the primary type — the AI suggests 'optimization']",
      "framing_rationale": "[MODELER INPUT NEEDED: which type, and why this framing over the alternative — e.g. Q3 is optimization not evaluation because the graded output is an allocation plan under constraints, not a score]",
      "secondary_type": "multi-objective decision",
      "classification_reason": "Q3 asks for an allocation plan under limited resources.",
      "candidate_method_families": [
        "linear programming",
        "integer programming",
        "multi-objective optimization"
      ],
      "risk_flags": [
        "decision variables, objective function, and constraints must be explicit"
      ]
    }
  ],
  "recommended_next_skill": "related-paper-analyzer"
}
```

## Example 2: Avoid whole-problem overclassification

Input state:

- The title suggests prediction.
- Q1 asks for data cleaning and correlation analysis.
- Q2 asks for future sales prediction.
- Q3 asks for pricing optimization.

Output:

```json
{
  "classification_summary": {
    "overall_pattern": "hybrid",
    "reason": "The title is prediction-oriented, but the subquestions require data analysis, prediction, and optimization."
  },
  "subquestion_classifications": [
    {
      "id": "Q1",
      "ai_suggested_type": "data-analysis",
      "ai_suggestion_confidence": "medium",
      "modeler_chosen_type": "[MODELER INPUT NEEDED: confirm or override the primary type — the AI suggests 'data-analysis']",
      "framing_rationale": "[MODELER INPUT NEEDED: which type, and why this framing over the alternative — e.g. Q1 is data-analysis not prediction because the graded output is influencing-factor relationships, not future values]",
      "classification_reason": "Q1 asks for relationships and influencing factors rather than future values."
    },
    {
      "id": "Q2",
      "ai_suggested_type": "prediction",
      "ai_suggestion_confidence": "high",
      "modeler_chosen_type": "[MODELER INPUT NEEDED: confirm or override the primary type — the AI suggests 'prediction']",
      "framing_rationale": "[MODELER INPUT NEEDED: which type, and why this framing over the alternative — e.g. Q2 is prediction not data-analysis because the graded output is future sales values]",
      "classification_reason": "Q2 asks for future sales estimates."
    },
    {
      "id": "Q3",
      "ai_suggested_type": "optimization",
      "ai_suggestion_confidence": "high",
      "modeler_chosen_type": "[MODELER INPUT NEEDED: confirm or override the primary type — the AI suggests 'optimization']",
      "framing_rationale": "[MODELER INPUT NEEDED: which type, and why this framing over the alternative — e.g. Q3 is optimization not prediction because the graded output is a pricing decision under constraints]",
      "classification_reason": "Q3 asks for a pricing decision."
    }
  ],
  "recommended_next_skill": "related-paper-analyzer"
}
```

## Example 3: Blocked classification

Input state:

- Q2 asks to “evaluate the system.”
- The evaluation target and output form are not specified.
- No attachment fields are available.

Output:

```json
{
  "blocked_items": [
    "The evaluation target and required output form are unclear."
  ],
  "partial_classifications": [],
  "missing_information": [
    "What object is being evaluated",
    "Whether the required output is a score, ranking, grade, or recommendation",
    "Available indicator fields"
  ],
  "recommended_next_action": "Return to problem-parser or ask the user for the missing output requirements."
}
```
