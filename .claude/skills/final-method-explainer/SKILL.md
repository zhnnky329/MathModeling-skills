---
name: final-method-explainer
description: Help the modeler write a comprehensive final method explanation document that justifies the selected method, documents eliminated alternatives, defines assumptions, symbols, objectives, and solution steps for paper writing.
license: MIT
---

# Purpose

Help the modeling team member write a definitive final method explanation for a subquestion after multi-round experimentation has converged on the best method.

This skill converts the candidate method pool, iteration logs, and experiment reports into a single authoritative document that explains:
- Which method was finally chosen and why — **transcribed** from the modeler's logged `method_choice` rationale, NOT re-authored here.
- Which other candidate methods were eliminated and why — transcribed from the same decision record's `rejected_alternatives`.
- The full mathematical specification: assumptions, symbols, objective function, constraints, solution procedure. (This structural specification stays AI-drafted.)
- Evaluation metrics — with the **good-result threshold** supplied by the human decision artifact, not invented by the AI.
- Concrete paper-writing suggestions for the model construction section.

Two graded judgments in this document are NOT originated by this skill: (a) the "why this method was chosen" narrative, and (b) the assumption necessary-vs-simplifying labels, plus what counts as a "good" result. These are decided by the human at Gate G4.5 in a decision artifact; this skill drafts connective prose and a *suggested* label only, clearly marked, and transcribes the human's verdict once logged.

This skill does not select the final method (the modeler does), originate the why-this-method verdict, originate assumption-necessity labels, run experiments, write final paper sections directly, or generate code.

# When to use

Use this skill:

- After one or more rounds of experiments have been completed and the modeler has decided which method to use.
- After `result-report-generator` has produced experiment reports and the modeler has reviewed them.
- When the modeler needs to produce `methods/Qx/qx_final_method_explanation.md`.
- When the user says: "write the final method explanation for Q1", "document the final method", "explain why we chose this method", "prepare the method for paper writing".
- Before `solution-package-builder` or `paper-section-writer`.
- When the method iteration log shows convergence and the modeler confirms final selection.

# Preconditions

The following should already exist or be provided:

- The candidate method pool for this subquestion (`methods/Qx/qx_method_candidates.md` or equivalent).
- The method iteration log (`methods/Qx/qx_method_iteration_log.md` or equivalent), recording what changed across rounds.
- Experiment reports from at least one round (`results/Qx/experiments/roundN/qx_experiment_report_roundN.md`).
- The modeler's explicit confirmation of which method is the final choice — captured as a `DECIDED` `method_choice` record in `methods/Qx/qx_decision_log.md` (collected by `modeler-decision-logger`). Iteration logs alone are evidence, not the verdict.
- The problem parse and classification artifacts (for subquestion goals, constraints, and required outputs).
- The global assumptions list `planning/model_assumptions.md` (the source the per-assumption necessity verdict is decided against).

If the candidate method pool does not exist, hand back to `method-selector`.

If no experiment reports exist, hand back to `result-report-generator`.

If `methods/Qx/qx_decision_log.md` has no `DECIDED` `method_choice` record for this Qx, the why-this-method narrative has no backing — hand back to the modeler (via `method-selector` / `modeler-decision-logger`) before producing the explanation. Do not guess which method is "final", and do not author a "why we chose X" sentence yourself. Do not infer the verdict from experiment results alone.

# Inputs

Use or request:

- `methods/Qx/qx_method_candidates.md` — the original candidate method pool.
- `methods/Qx/qx_method_iteration_log.md` — the record of method changes across rounds.
- `results/Qx/experiments/roundN/qx_experiment_report_roundN.md` — experiment reports from all rounds.
- `workspace/problem/problem-parser/problem_parse.json` — for subquestion goals and constraints.
- `workspace/problem/problem-classifier/problem_classification.json` — for task type context.
- `workspace/problem/method-selector/method_plan.json` — for original method specifications.
- `methods/Qx/qx_decision_log.md` — the canonical decision log. The `method_choice` record's `modeler_rationale` is the **only** source for the why-this-method narrative; transcribe it with `<!-- from Qx-D0n -->` provenance.
- `planning/model_assumptions.md` — the global assumptions list against which necessary-vs-simplifying is decided.
- The modeler's explicit confirmation of the final method choice (as a logged decision record, not verbal).
- Any additional notes the modeler provides about why they chose this method.

# Workflow

1. Confirm final method selection — from the decision log, not from your own reading.
   - Read `methods/Qx/qx_decision_log.md` for the `DECIDED` `method_choice` record. That record's `modeler_decision` is the final method; its `modeler_rationale` is the why.
   - Read the iteration log to trace the decision *path* (what was tried, failed, improved, dropped) — as supporting evidence only, not as the verdict.
   - If there is no `DECIDED` `method_choice` record, stop and hand back to the modeler. Do not promote a method from iteration-log ambiguity.
   - Do not independently decide which method is "final", and do not author the why. The human already authored it in the log; your job is to transcribe.

2. Document the selection process — by TRANSCRIBING the human's logged rationale, not re-authoring it.
   - State the final selected method clearly (from the `method_choice` record's `modeler_decision`).
   - List every candidate method that was considered and experimented.
   - For each eliminated method, transcribe the reason from the decision record's `rejected_alternatives[*].reason` (the human's words), tagged `<!-- from Qx-D0n -->`. The experiment reports supply the supporting numbers, but the *judgment* "this is why it was dropped" comes from the log.
   - The "why the final method was chosen" paragraph is **transcribed** from the `method_choice` record's `modeler_rationale`, carrying a `<!-- from Qx-D0n -->` provenance comment — NOT composed by you. You may add neutral connective phrasing around the transcribed sentence (and mark any such drafting `[AI-DRAFT — needs modeler verdict]`), but you may NOT write a "why we chose X" claim that has no backing sentence in the log. If the log's rationale is thin, that is a gap for the modeler to fill, not for you to paper over.
   - Be honest about trade-offs. If the final method has weaknesses, state them explicitly (trade-offs may be drawn from experiment reports and the logged rationale; do not invent favorable ones).

3. Define model assumptions — list and draft, but the necessary-vs-simplifying verdict is the human's (Gate G4.5).
   - List every modeling assumption the final method relies on, sourced from `planning/model_assumptions.md` plus any method-specific ones.
   - For each assumption you may **suggest** a label — "necessary" (the model breaks without it) or "simplifying" (the model works but is more approximate without it) — but mark every such suggestion `[AI-DRAFT — needs modeler verdict]`. The committed label is decided by the human in the decision artifact (`decision_point: assumption_necessity`), then transcribed back here.
   - For each assumption, state its possible impact on results (AI may draft this factual impact note).
   - Link assumptions to the problem context — why is this assumption reasonable for this specific contest problem?
   - Do not include generic assumptions that don't affect the model.
   - Do NOT present a necessary/simplifying label as settled until it carries the human's verdict from the decision log. The label is graded reasoning; this skill never originates it.

4. Define symbols and notation.
   - Create a complete symbol table covering all variables, parameters, sets, indices, functions, and outputs used in the final method.
   - Distinguish: decision variables, state variables, parameters, inputs, intermediate values, and outputs.
   - Include units where applicable.
   - Ensure notation is consistent with other subquestions (check the global symbol table if it exists).
   - Mark symbols that are shared across subquestions.

5. Write the mathematical model specification.
   - State the objective function (for optimization) or evaluation criterion (for evaluation) or prediction target (for prediction).
   - State all constraints in mathematical form.
   - State the solution procedure step by step.
   - For optimization: define decision variables, objective, constraints, and solver approach.
   - For evaluation: define indicator normalization, weighting method, aggregation formula, and ranking rule.
   - For prediction: define model form, training procedure, prediction formula, and error estimation.
   - For mechanism: define governing equations, parameters, boundary conditions, and solution method.
   - For classification/clustering: define features, model form, training/clustering procedure, and assignment rule.
   - For simulation: define stochastic elements, trial structure, output statistics, and seed management.
   - Every equation must have its variables defined. Every parameter must have a source or estimation method.

6. Define evaluation metrics — formulas are AI-drafted, the good-result threshold is the human's.
   - State how this method's output quality is measured.
   - Define each metric formula (AI-drafted).
   - State expected ranges. The **`result_good_threshold`** — i.e., what value of a metric counts as a "good" result for this method — is a graded judgment supplied by the human in the decision artifact; transcribe it, do not invent it. You may suggest a threshold marked `[AI-DRAFT — needs modeler verdict]`.
   - Link metrics to the subquestion's evaluation criteria from the problem parse.
   - Do not author a "this is a good result" interpretation that has no backing `result_good_threshold` in the decision artifact.

7. Provide paper-writing guidance.
   - State which parts of this explanation should go into the "Model Construction" section of the paper.
   - State which formulas are most important to show.
   - State which assumptions should be highlighted.
   - State which eliminated methods should be mentioned (for demonstrating thoroughness).
   - Suggest a logical flow: assumptions → symbols → model formulation → solution → metrics.
   - Flag any parts of the explanation that are "for internal use only" and should not appear in the paper (e.g., implementation details, debugging notes).

8. Produce the final method explanation document.
   - Save as `methods/Qx/qx_final_method_explanation.md`.
   - Keep it structured, complete, and self-contained.
   - The document should be understandable without reading the iteration logs or experiment reports (though it should reference them).
   - The structural sections (symbols, math model, solution steps) are AI-drafted as before. The two graded inserts — the why-this-method narrative and the necessary/simplifying labels + good-result threshold — must either carry a `<!-- from Qx-D0n -->` transcription provenance (already logged) or an `[AI-DRAFT — needs modeler verdict]` marker (still pending). No graded insert may appear as a settled, unsourced claim.

9. Emit the modeler decision artifact, then STOP (Gate G4.5).
   - This is the load-bearing change: the why-this-method narrative and the assumption-necessity / good-result judgments are graded reasoning. The AI must not originate them.
   - Create `methods/Qx/decisions/final-method-explainer_modeler_decision.md` following the **Human Decision Artifact Convention** in CLAUDE.md, with:
     - `status: PENDING`, `decided_by: human` (left for the human to confirm), `decision_id: qx_method_explanation`, `decision_point: assumption_necessity`.
     - `ai_suggestion`: your best-effort draft — a suggested necessity label per assumption and a suggested `result_good_threshold` — each clearly marked `[AI-DRAFT — needs modeler verdict]`. This is YOUR view, in its own field; it is not the verdict.
     - `choice`: left as a `<<<HUMAN>>>` sentinel for the modeler to fill with, per assumption, `necessity ∈ {necessary, simplifying}` + a one-line why, and the committed `result_good_threshold`.
     - The `## Modeler's rationale` body left as a `<<<HUMAN>>>` sentinel — human-authored, the AI must NOT write it.
     - `rejected_alternatives[*].reason`: left as `<<<HUMAN>>>` if not already settled in the decision log.
     - `evidence_refs`: point at `methods/Qx/qx_decision_log.md` (the `method_choice` record) and `planning/model_assumptions.md`, so the human's rationale can cite a concrete token.
   - Note the division of labor: the **why-this-method narrative is NOT decided here** — it was already decided at Gate G2.5 (`method-selector`) and lives as a `method_choice` record in the decision log; this skill only TRANSCRIBES it with provenance. This artifact's own PENDING decision is the `assumption_necessity` + `result_good_threshold` verdict.
   - Then STOP and tell the modeler exactly what to fill in. Do NOT proceed to `solution-package-builder` or `paper-section-writer`. Gate G4.5 keeps the why-this-method narrative un-blessed until the artifact's `status` is `DECIDED` with a non-empty, non-copied human rationale that cites evidence.
   - In **learning mode** (if `planning/session_config.json` says so): withhold `ai_suggestion` until after the human writes their rationale, to avoid anchoring. In **speed mode**: show `ai_suggestion` alongside. Either way the human rationale field, its floor, and the copy/evidence checks are identical.

10. Hand off to the next skill — only after the decision artifact is `DECIDED`.
   - First route the PENDING artifact to `modeler-decision-logger` so the human's `assumption_necessity` verdict folds into `methods/Qx/qx_decision_log.md`.
   - If the final result analysis also exists: hand off to `solution-package-builder`.
   - If the final result analysis does not yet exist: hand off to `result-report-generator` or `workflow-orchestrator`.

# Outputs

Produce:

- `methods/Qx/qx_final_method_explanation.md` — the structural explanation (AI-drafted), with the why-this-method narrative TRANSCRIBED from the decision log (with `<!-- from Qx-D0n -->` provenance) and graded inserts either transcribed or marked `[AI-DRAFT — needs modeler verdict]`.
- `methods/Qx/decisions/final-method-explainer_modeler_decision.md` — the PENDING decision artifact (`decision_id: qx_method_explanation`, `decision_point: assumption_necessity`), awaiting the human's per-assumption necessity labels + `result_good_threshold`. See Workflow step 9.

# Output format

The document MUST contain all of the following sections:

```markdown
# Qx Final Method Explanation

## 1. Method Selection Summary

- **Final selected method**: [method name]
- **Selection date / round**: [when this was decided]
- **Modeler**: [name or role if applicable]

### Candidate Methods Considered

| Method | Status | Reason (transcribed from decision log) |
|--------|--------|----------------------------------------|
| M1: [name] | Eliminated — Round N | [reason from `rejected_alternatives` — `<!-- from Qx-D0n -->`] |
| M2: [name] | Selected — Final | [the modeler's `method_choice` — `<!-- from Qx-D0n -->`] |
| M3: [name] | Eliminated — Round N | [reason from `rejected_alternatives` — `<!-- from Qx-D0n -->`] |

### Selection Justification (TRANSCRIBED — not authored here)

- **Why this method was chosen**: [verbatim/near-verbatim from the `method_choice` record's `modeler_rationale` — `<!-- from Qx-D0n -->`. Do NOT compose a new justification. If no such record exists, this subsection is BLOCKED, not filled.]
- **Trade-offs accepted**: [weaknesses or compromises, drawn from experiment reports + logged rationale]
- **Key differentiator**: [from the logged rationale / experiment evidence — not an AI-invented claim of superiority]

## 2. Model Assumptions

> Necessary-vs-simplifying labels are the human's verdict (decision artifact, `decision_point: assumption_necessity`).
> Until logged, each label below carries `[AI-DRAFT — needs modeler verdict]`; once decided, it carries `<!-- from Qx-D0n -->`.

### Necessary Assumptions (model breaks without them)

| # | Assumption | Label source | Justification | Impact if Violated |
|---|-----------|-------------|---------------|-------------------|
| 1 | [assumption] | `<!-- from Qx-D0n -->` or `[AI-DRAFT — needs modeler verdict]` | [why reasonable for this problem] | [what happens if not true] |

### Simplifying Assumptions (model works approximately without them)

| # | Assumption | Label source | Justification | Impact if Relaxed |
|---|-----------|-------------|---------------|------------------|
| 1 | [assumption] | `<!-- from Qx-D0n -->` or `[AI-DRAFT — needs modeler verdict]` | [why acceptable] | [effect on results] |

## 3. Symbols and Notation

### Sets and Indices

| Symbol | Meaning | Domain / Range |
|--------|---------|---------------|
| [symbol] | [description] | [domain] |

### Parameters (given or estimated)

| Symbol | Meaning | Value / Source | Unit |
|--------|---------|---------------|------|
| [symbol] | [description] | [value or how obtained] | [unit] |

### Decision Variables (controlled by the model)

| Symbol | Meaning | Domain | Unit |
|--------|---------|--------|------|
| [symbol] | [description] | [domain] | [unit] |

### State Variables (computed from decisions and parameters)

| Symbol | Meaning | Computation | Unit |
|--------|---------|------------|------|
| [symbol] | [description] | [formula or source] | [unit] |

### Outputs (delivered to the paper / downstream)

| Symbol | Meaning | Format |
|--------|---------|--------|
| [symbol] | [description] | [form] |

## 4. Mathematical Model

### 4.1 Objective Function / Evaluation Criterion
[Mathematical formulation with explanation]

### 4.2 Constraints
[Each constraint in mathematical form with explanation]

### 4.3 Solution Procedure

**Step 1**: [what is done, with formula if applicable]
**Step 2**: [what is done, with formula if applicable]
...

### 4.4 Key Formulas Summary
[The most important formulas, collected for easy reference]

## 5. Evaluation Metrics

> Formulas and expected ranges are AI-drafted. The `result_good_threshold` (what counts as a "good" result)
> is the human's verdict from the decision artifact; transcribe it (`<!-- from Qx-D0n -->`) or mark
> `[AI-DRAFT — needs modeler verdict]`. Do not assert "this is a good result" without a logged threshold.

| Metric | Formula | Expected Range | Good-result threshold (source) |
|--------|---------|---------------|--------------------------------|
| [metric] | [formula] | [range] | [threshold + `<!-- from Qx-D0n -->` or `[AI-DRAFT — needs modeler verdict]`] |

## 6. Relationship to Other Subquestions

- **Inputs from other subquestions**: [what this method receives from Q1, Q2, etc.]
- **Outputs to other subquestions**: [what this method provides to Q2, Q3, etc.]
- **Shared symbols**: [symbols also used in other subquestions]
- **Consistency notes**: [any alignment needed]

## 7. Paper Writing Guidance

### Suggested Section Flow
1. [subsection name] — [what to write]
2. [subsection name] — [what to write]
...

### Formulas to Show in Paper
- [formula reference] — [why it's important, where to show it]

### Assumptions to Highlight
- [assumption] — [why it matters to the reader]

### Eliminated Methods to Mention
- [method] — [brief reason for elimination, to show methodology was thorough]

### Internal-Use Only (do NOT put in paper)
- [item] — [why it should stay internal]

## 8. References to Supporting Documents
- Candidate methods: `methods/Qx/qx_method_candidates.md`
- Iteration log: `methods/Qx/qx_method_iteration_log.md`
- Decision log (source of the why-this-method narrative): `methods/Qx/qx_decision_log.md`
- Global assumptions: `planning/model_assumptions.md`
- This skill's decision artifact: `methods/Qx/decisions/final-method-explainer_modeler_decision.md`
- Experiment reports: `results/Qx/experiments/roundN/`
- Final result analysis: `results/Qx/reports/qx_final_result_analysis.md` (when available)
```

# Rules

- **The human decides at the gate; this skill never assigns the graded verdict.** It never originates the why-this-method narrative, never originates a necessary/simplifying label, never decides what counts as a "good" result, and never fills the human rationale. It lays out evidence + an `ai_suggestion`, then STOPS at the PENDING decision artifact (Gate G4.5).
- **The why-this-method narrative is TRANSCRIBED, not re-authored.** Every "why we chose X" sentence must trace to a `modeler_rationale` in `methods/Qx/qx_decision_log.md`, carried with a `<!-- from Qx-D0n -->` provenance comment. It is forbidden to write a "why we chose X" sentence that has no backing decision record — that is rationale-laundering and is prohibited.
- The structural sections (symbols, math model, solution procedure) stay AI-drafted, as before.
- Do not select the final method independently. The modeler's logged `method_choice` decision is the source.
- Every eliminated method must have a specific reason — transcribed from the decision record's `rejected_alternatives` (the human's judgment), supported by experiment report findings. Do not author the elimination judgment yourself.
- Per-assumption necessary/simplifying labels and the `result_good_threshold` are the human's verdict; this skill may only suggest them, marked `[AI-DRAFT — needs modeler verdict]`, until they are logged.
- Every assumption must be linked to a modeling need — no filler assumptions.
- Every symbol must be defined before use in formulas.
- Notation must be checked against other subquestions for consistency.
- The solution procedure must be specific enough that a programmer could re-implement it.
- The paper writing guidance should be actionable, not vague ("show the formula" not "discuss the model").
- Do not fabricate experiment results, metrics, or selection reasons.
- Do not write the actual paper section — this is a method explanation for the modeler and paper writer, not the paper itself.
- Do not claim superiority that is not supported by experiment reports.
- Trade-offs and weaknesses must be stated honestly.
- If the method has known limitations, state them clearly.

# Verification

Before handing off, verify:

- The final method is explicitly named and confirmed **from a `DECIDED` `method_choice` record** in `methods/Qx/qx_decision_log.md`, not from your own reading of the iteration log.
- The why-this-method paragraph is **transcribed** with a `<!-- from Qx-D0n -->` provenance comment; no "why we chose X" sentence lacks a backing decision record.
- Every candidate method's fate (eliminated or selected) is documented with reasons transcribed from the decision record, supported by experiment evidence.
- The PENDING decision artifact `methods/Qx/decisions/final-method-explainer_modeler_decision.md` exists with `status: PENDING`, `decided_by: human`, `decision_id: qx_method_explanation`, `decision_point: assumption_necessity`, `ai_suggestion` filled (per-assumption label suggestion + suggested `result_good_threshold`), and `choice` / `## Modeler's rationale` left as `<<<HUMAN>>>` sentinels.
- Assumptions are listed; their necessary/simplifying labels either carry `<!-- from Qx-D0n -->` (decided) or `[AI-DRAFT — needs modeler verdict]` (still pending) — none is presented as a settled, unsourced AI verdict.
- The `result_good_threshold` is transcribed from the decision artifact or marked `[AI-DRAFT — needs modeler verdict]` — never asserted as settled by this skill.
- The symbol table is complete and distinguishes variable types.
- Mathematical formulations are present and variables are defined.
- Solution procedure is step-by-step and implementable.
- Evaluation metrics are defined with formulas and interpretation.
- Paper-writing guidance is specific and actionable.
- Cross-subquestion consistency is checked (if other subquestions are available).
- The document is self-contained and understandable on its own.

# Failure modes

Stop and report a blocker if:

- `methods/Qx/qx_decision_log.md` has no `DECIDED` `method_choice` record for this Qx — the why-this-method narrative has no backing to transcribe. Hand back to the modeler; do not author the why yourself.
- The iteration log is empty or nonexistent — there is no decision path to document.
- No experiment reports exist — there is no evidence base for selection.
- The chosen method cannot be mathematically specified (missing variables, undefined parameters, unclear procedure).
- Cross-subquestion symbol conflicts exist and cannot be resolved without changes to other subquestions.
- The modeler asks for a method explanation that contradicts experiment evidence.

# Stop conditions

This skill must stop instead of guessing when:

- The final method choice is not yet a `DECIDED` `method_choice` record — do not promote a method from log ambiguity, and do not author the why.
- Key parameters have no source and no reasonable default.
- The method cannot be written in mathematical form without inventing missing pieces.
- The experiment evidence contradicts the claimed selection reason.
- The modeler asks you to author the why-this-method narrative, the necessary/simplifying labels, or the good-result threshold instead of deciding them — these are the human's at Gate G4.5; refuse and emit the PENDING artifact.
- The modeler asks to fabricate favorable justifications or hide weaknesses.

When stopping, output:

- the blocker
- why it matters
- what is missing or contradictory
- what can still be partially documented
- recommended next action (usually: return to modeler for clarification)

# Handoff

After producing `methods/Qx/qx_final_method_explanation.md` and the PENDING decision artifact, hand off first to:

`modeler-decision-logger`
— to fold the human's `assumption_necessity` verdict (once `DECIDED`) into `methods/Qx/qx_decision_log.md`. Gate G4.5 stays blocked until this is logged.

Then, only after the decision artifact is `DECIDED`:

`solution-package-builder`
— if `results/Qx/reports/qx_final_result_analysis.md` also exists.

`workflow-orchestrator`
— if the final result analysis does not yet exist and the workflow needs to determine next steps.

`result-report-generator`
— if the final method is confirmed but the final result analysis has not been generated yet.

Do not hand off directly to `paper-section-writer`. The paper writer should receive the solution package, which bundles the final method explanation with the final result analysis.

# Examples

## Example 1: Final method explanation for evaluation problem (Q1)

Input state:
- Q1 candidate methods: equal-weight scoring (M1), entropy TOPSIS (M2), AHP-TOPSIS (M3).
- Iteration log shows M3 was dropped after round 1 (AHP subjective weights hard to justify).
- Round 2 compared M1 and M2. The decision log holds a `DECIDED` `method_choice` record `Q1-D03`: modeler chose M2, kept M1 as baseline, with the modeler's own rationale.

Output (note: the "why M2" prose is transcribed from `Q1-D03`, not authored here; necessity labels remain `[AI-DRAFT]` until the PENDING `qx_method_explanation` artifact is decided):
```markdown
# Q1 Final Method Explanation

## 1. Method Selection Summary

### Candidate Methods Considered

| Method | Status | Reason (transcribed from decision log) |
|--------|--------|----------------------------------------|
| M1: Equal-Weight Normalized Scoring | Retained as baseline | Provides transparent reference; no weight justification needed <!-- from Q1-D03 --> |
| M2: Entropy-Weight TOPSIS | **Selected — Final** | Modeler's choice <!-- from Q1-D03 --> |
| M3: AHP-TOPSIS | Eliminated — Round 1 | Requires subjective pairwise comparison matrix; cannot be objectively justified without domain expert input <!-- from Q1-D03 rejected_alternatives --> |

### Selection Justification (TRANSCRIBED — not authored here)

- **Why M2 was chosen**: <!-- from Q1-D03 --> [verbatim/near-verbatim from the modeler's `modeler_rationale` — e.g., the modeler's words that M2's objective weights and ±10% perturbation stability were what decided it. NOT a fresh paragraph composed by this skill. If `Q1-D03` did not exist, this subsection would be BLOCKED.]
- **Trade-offs accepted**: Entropy weighting can overweight high-variance indicators that may not be practically important (drawn from round 2 experiment report + the logged rationale).
- **Key differentiator**: <!-- from Q1-D03 --> [the differentiator the modeler actually logged, not an AI-invented superiority claim].

## 3. Symbols and Notation

### Sets and Indices

| Symbol | Meaning | Domain / Range |
|--------|---------|---------------|
| i | City index | i = 1, 2, ..., m |
| j | Indicator index | j = 1, 2, ..., n |

### Parameters

| Symbol | Meaning | Value / Source | Unit |
|--------|---------|---------------|------|
| x_{ij} | Raw value of indicator j for city i | From cleaned indicator matrix | varies by indicator |

## 4. Mathematical Model

### 4.3 Solution Procedure

**Step 1 — Normalization**: Apply min-max normalization with direction handling.
[formula]

**Step 2 — Entropy weight calculation**: Compute entropy e_j for each indicator.
[formula]

**Step 3 — TOPSIS scoring**: Compute ideal best/worst and relative closeness.
[formula]

**Step 4 — Ranking**: Sort cities by C_i descending.
```

## Example 2: Blocked — no DECIDED method_choice record to transcribe

Input state:
- Experiment reports exist for Q2, round 2.
- Iteration log shows three methods tested.
- `methods/Q2/qx_decision_log.md` has NO `DECIDED` `method_choice` record (M2 and M4 both performed well; the human has not committed).

Output:
```json
{
  "blocked_items": [
    "No DECIDED method_choice record exists for Q2. The why-this-method narrative has no logged rationale to transcribe, and this skill never authors it. The iteration log shows M2 and M4 both performed well in round 2."
  ],
  "safe_partial_work": [
    "Structural sections (symbol table, math model skeleton) can be drafted for both M2 and M4.",
    "The PENDING decision artifact methods/Q2/decisions/final-method-explainer_modeler_decision.md can be emitted with ai_suggestion-level assumption-necessity drafts marked [AI-DRAFT — needs modeler verdict]."
  ],
  "recommended_next_action": "Route the human's method choice through method-selector's decision artifact + modeler-decision-logger so a DECIDED method_choice record exists; only then can the why-this-method narrative be transcribed."
}
```

## Example 3: PENDING decision artifact emitted (assumption_necessity)

Input state:
- Q1 has a `DECIDED` `method_choice` record `Q1-D03` (M2 entropy-TOPSIS).
- The structural explanation is drafted; the why-M2 prose is transcribed from `Q1-D03`.
- The necessary/simplifying labels and good-result threshold are not yet decided.

Output (`methods/Q1/decisions/final-method-explainer_modeler_decision.md`, abbreviated):
```markdown
---
schema_version: 1
skill: final-method-explainer
scope: Q1
decision_id: qx_method_explanation
decision_point: assumption_necessity
status: PENDING
decided_by: human
decided_at:
ai_suggestion: "[AI-DRAFT — needs modeler verdict] A1 (indicators independent) → simplifying; A2 (data complete after cleaning) → necessary; result_good_threshold: top-3 ranking stable under ±10% weight perturbation"
choice: <<<HUMAN>>>
rejected_alternatives: []
confidence:
evidence_refs:
  - methods/Q1/qx_decision_log.md
  - planning/model_assumptions.md
---

## Modeler's rationale
<<<HUMAN>>>
```
Then STOP. Tell the modeler: fill each assumption's necessity label + one-line why, set `result_good_threshold`, write the rationale citing a token from `evidence_refs`, set `status: DECIDED`. Do not proceed to `solution-package-builder` until then.
