---
name: decision-prompt-builder
description: At a judgment point, emit the 2-3 questions only the human modeler can answer — framed as trade-offs, not answers — and refuse to answer them. The inverse of "AI answers, human confirms": here the AI asks, the human answers, then the AI assists with the consequences.
license: MIT
---

# Purpose

At every modeling-judgment point, surface the minimal set of questions only the modeler can legitimately answer, **before** the AI shows any suggestion — and refuse to answer them. This is the reusable form of the one good pattern that already exists in `method-selector` (the "前置颗粒度对齐 — ask the ONE most load-bearing question" step): make it available at every judgment gate, not just method selection.

The posture this enforces: instead of "AI proposes a verdict → human confirms it" (which collapses into rubber-stamping), the flow becomes "AI asks the question the human owns → human answers → AI assists with what follows". The AI is allowed to lay out the trade-off; it is not allowed to pick the side.

This skill does NOT answer its own questions, pre-select a recommended option, or fill any decision artifact. It produces questions; the human's answers flow into the `modeler_decision` / `modeler_rationale` fields of the relevant decision artifact or the decision log.

# When to use

Call this skill FIRST, before the judgment-bearing skill shows its evidence/suggestion, at any gate whose verdict is a modeling judgment:

- **G1 framing** — before `problem-classifier` shows `ai_suggested_type`: what output does the team want to defend?
- **G2 / G2.5 method choice + baseline** — before `method-selector` shows its `ai_suggestion`.
- **post-experiment (G4.5)** — before `result-report-generator` / `robustness-checker` show their suggested verdicts: which result is the headline, how confident, is it robust enough?
- **G5 claim scope / figure role** — before `paper-section-writer` / `figure-table-planner` finalize: what is the contribution, what claim does this figure defend?

Any skill whose tier is `makes_modeling_judgment` (the five C-layer skills) should trigger this skill first. B-layer skills may use it for their load-bearing span (the rubric, the framing, the physical meaning).

Do NOT use this skill:

- During mechanical stages (code generation, review, freeze, render-check, the auditors) — there is no modeling judgment to ask about, and a question there is friction theatre.
- To ask a question whose answer is mechanically determinable (e.g. "should the seed be fixed?" — that is AI-owned; never ask it).

# Inputs

- The current gate / judgment point and the candidate options the downstream skill will present (so the questions are grounded in the actual trade-off).
- `planning/session_config.json` — the `mode` (`learning` | `speed`), which controls verbosity and anchor-timing only.
- The problem parse / classification for context.

# Workflow

1. Identify the single judgment the human must own at this gate (method choice / framing / result verdict / confidence / claim scope / figure claim).

2. Derive the 2-3 questions that, if answered, narrow the decision space the most. Rank them by how load-bearing they are. Each question MUST:
   - Be framed as a **trade-off**, not a leading question: "Q3 can be cast as optimization or as evaluation — optimization gives you a defensible 'optimal' claim but needs a clean objective; evaluation is safer but weaker. Which does your team want to defend?"
   - Name the consequence of each side, not the recommended side.
   - Be answerable only by a human with modeling judgment (not by computing something).

3. Emit at most 3 questions. If everything looks like a question, you have failed to prioritize — pick the 3 that matter. (Anti-fatigue: if the human is asked everything, they tune out, and the gate degrades into rubber-stamping.)

4. Hand the human's answers to the downstream skill / decision artifact. Do not author the answers. Do not mark any artifact DECIDED.

# Mode behavior (learning vs speed — scaffolding only, never gate strictness)

The `mode` in `planning/session_config.json` changes ONLY how this skill prompts — never the floors, never the copy-detection, never any gate.

| | learning mode | speed mode |
|---|---|---|
| Question count & framing | full 2-3 questions, each option's trade-off explained | one terse question, trade-off compressed to a clause |
| AI suggestion timing | **withheld** until after the human has written their answer (anti-anchoring) | shown alongside, since the expert wants a draft to react to |
| Term definitions | inline (defines TOPSIS, RMSE, etc.) | assumed known |
| Post-answer reflection | "would this convince a judge? what's the weakest part?" | omitted |

**Anchor suppression is the key learning-mode mechanic.** In learning mode, the downstream skill's `ai_suggestion` must be withheld until the human commits their own answer, then revealed for comparison ("you chose ARIMA for trend-fit; the AI also flagged seasonality you didn't mention"). This directly attacks the anchoring bias that makes a human "decision" just an echo of the AI's pick. In speed mode anchoring is an accepted trade-off for an expert who can critically evaluate a draft.

The mode is recorded per decision (`captured_in_mode`) by `modeler-decision-logger`, so a post-contest review can show which decisions were made on autopilot (speed) vs deliberated (learning).

# Outputs

A `decision_prompt` block injected at the top of the judgment skill's output (not a saved file unless the skill persists it):

```markdown
## Decision prompt — your call, not the AI's  (mode: learning)

Before you see the AI's suggestion, answer these (most load-bearing first):

1. **[output form]** Q3's answer can be a *plan* (optimization — you can claim "optimal", but you need a clean
   objective and constraints) or a *score/ranking* (evaluation — safer, but you can't claim optimality). Which
   does your team want to defend, and why?
2. **[baseline]** The simplest honest reference here is greedy allocation. Do you accept that as the baseline, or
   is there a more meaningful one for this problem?

(The AI's suggestion is withheld until you've written your answer above — so it doesn't anchor you.)
```

# Rules

- Ask, never answer. Refuse to state or pre-select the answer to your own questions, even when the human is unsure.
- Never pre-fill a `modeler_decision` / `modeler_rationale` field. Never mark an artifact DECIDED.
- At most 3 questions per gate. Fewer is better.
- Only ask genuine modeling-judgment questions — never one whose answer is mechanically determinable.
- Frame trade-offs (name both consequences); never frame a leading question that telegraphs the "right" answer.
- The mode toggle changes verbosity and anchor-timing ONLY. It NEVER relaxes a char floor, a copy-detection, or any gate. If `mode == speed`, the same human-authored decision-log records with the same floors are still required.
- Do not run during mechanical stages.

# Verification

Before handing off, verify:

- ≤ 3 questions, each a genuine human-judgment question framed as a trade-off.
- No question has a pre-selected or AI-supplied answer.
- In learning mode, the downstream `ai_suggestion` is withheld until after the human answers.
- No decision artifact field was authored or marked DECIDED by this skill.

# Failure modes

Stop and report if:

- The user asks this skill to answer its own question — refuse; narrow the trade-off instead, never resolve it.
- There is no genuine modeling judgment at this point (it's a mechanical stage) — do not invent a question.

# Handoff

- To the judgment-bearing skill (`method-selector`, `result-report-generator`, etc.): the human's answers, to flow into the decision artifact.
- To `modeler-decision-logger`: the `captured_in_mode` value for the decision record.

# Relationship to the posture shift

This skill operationalizes the "AI asks, human answers" inversion. The C-layer decision artifacts make rubber-stamping a dead end *after* the fact (empty/copied rationale fails the gate); this skill attacks the same problem *before* the fact, by making the human supply the judgment as an answer to a real question rather than as a confirmation of an AI verdict. Learning mode's anchor suppression is what makes the human's answer genuinely theirs rather than an echo.
