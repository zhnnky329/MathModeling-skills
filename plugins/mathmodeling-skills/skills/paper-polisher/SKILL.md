---
name: paper-polisher
description: Polish mathematical modeling paper drafts for grammar, clarity, formula consistency, hedging calibration, overclaim detection, and contest formatting compliance. Use after paper-section-writer has drafted sections.
license: MIT
---

# Purpose

Polish mathematical modeling contest paper sections for language quality, logical clarity, formula consistency, and claim calibration.

This skill operates on already-drafted paper sections. It improves wording, fixes grammar, checks formulas, calibrates hedging to match evidence strength, detects overclaims, and ensures formatting compliance. It does not invent new content, add unsupported claims, or rewrite the paper's scientific argument.

Adapted from [nature-polishing](https://github.com/Yuan1z0825/nature-skills) design principles: language serves the argument, polish should not hide weak reasoning, and claims must be proportional to evidence.

This skill does not write new paper sections, run experiments, generate figures, or perform final QA.

# When to use

Use this skill:

- After `paper-section-writer` has drafted one or more paper sections.
- Before `quality-assurance-auditor`.
- When the user says: "polish the paper", "check the English", "fix the grammar", "improve the writing", "calibrate the claims", "check for overclaims", "proofread Q1 section".
- When Chinese-to-English translation has produced rough drafts that need smoothing.
- When formulas, notation, or terminology are inconsistent across sections.

# Preconditions

The following should already exist or be provided:

- Paper section drafts under `paper/sections/`.
- Final method explanations (for formula and notation verification).
- Final result analyses (for claim verification).
- The global symbol table at `planning/symbol_table.md` (if available).
- Contest formatting requirements (if available).

If paper sections do not exist, hand back to `paper-section-writer`.

# Inputs

Use or request:

- `paper/sections/*.md` or `paper/sections/*.tex` — the drafted sections.
- `methods/Qx/qx_final_method_explanation.md` — for formula and notation verification.
- `results/Qx/reports/qx_final_result_analysis.md` — for claim verification.
- `planning/symbol_table.md` — for notation consistency.
- Contest formatting requirements.

# Workflow

1. Identify the paper type and section.
   - Mathematical modeling contest papers follow a standard structure: Abstract → Problem Restatement → Problem Analysis → Assumptions → Symbols → Model Construction (per Q) → Model Solution → Results Analysis → Robustness → Strengths & Limitations → Conclusion.
   - Each section has different polishing priorities (see section-specific rules below).

2. Run the 12-point polish checklist (see below).

3. Calibrate claims against evidence.
   - For each numerical or comparative claim, verify it is supported by the final result analysis or robustness report.
   - If a claim overstates the evidence, downgrade the language.
   - If a claim is unsupported, flag it as a blocker (do not silently remove — the writer needs to decide).

4. Check formula and notation consistency.
   - Every symbol must appear in the global symbol table or be defined locally.
   - Same concept must use the same symbol across all sections.
   - Subscripts, superscripts, and indices must be consistent.
   - Formula numbering must be sequential and match references in text.

5. Check terminology consistency.
   - Same concept must use the same term throughout.
   - Method names must match the final method explanation.
   - "Baseline", "main model", "improved model" must be used consistently.

6. Produce polished sections.
   - Show a diff or change summary.
   - Mark any claims that were downgraded and why.
   - Flag any remaining issues that need author attention.

# 12-Point Polish Checklist

## 1. Sentence Length
- Split sentences longer than 30 words.
- Vary sentence length: mix short (8-15 words) and medium (15-25 words).
- The first and last sentences of each paragraph should be the clearest.

## 2. Paragraph Structure
- Each paragraph should have one main point.
- Topic sentence first, support following, transition at end (or beginning of next).
- Paragraphs longer than 5-6 sentences should be split or tightened.

## 3. Tense Consistency
- **Problem restatement / Assumptions / Symbols**: Present tense.
- **Model construction**: Present tense for model description.
- **Model solution / Results analysis**: Past tense for what was done and found.
- **Conclusion**: Present tense for final findings, past tense for what was done.
- Do not mix tenses within a single paragraph without reason.

## 4. Hedging Calibration

Match claim strength to evidence:

| Evidence Level | Appropriate Hedging | Example |
|---------------|-------------------|---------|
| Robust, multiple checks | Strong claim, no hedge | "The entropy-TOPSIS method produces stable rankings." |
| Single check, moderate perturbation | Moderate hedge | "The rankings appear stable under moderate weight changes." |
| Limited check, narrow range | Weak hedge | "The results suggest that rankings may be stable within the tested range." |
| No check, extrapolation | No claim allowed | Flag as unsupported. Do not write. |

Hedging phrases (strongest to weakest):
- `demonstrates` / `shows` / `establishes` → strongest
- `indicates` / `suggests` / `supports` → moderate
- `may indicate` / `appears to` / `is consistent with` → weak
- `could potentially` / `might possibly` → weakest (use sparingly)

## 5. Overclaim Detection

Flag and downgrade or remove:
- Absolute claims: "always", "never", "proves", "guarantees", "optimal" (unless proven).
- Unwarranted causation: "A causes B" when only correlation is shown.
- Scope expansion: "All models benefit from..." when only one model was tested.
- Unverified "first" or "novel" claims.
- "Significantly" without statistical test or defined threshold.
- "Our model outperforms all existing methods" when only 1-2 baselines were compared.
- Numerical precision beyond data support: "The score is 0.883214" → "The score is approximately 0.88".

## 6. Formula Formatting
- Formulas in display math mode (`$$...$$` or `\begin{equation}...\end{equation}`) for important equations.
- Inline math (`$...$`) for variable references and short expressions.
- Consistent subscript/superscript style.
- Units after numerical values.
- Variable definitions immediately after first use in a formula.

## 7. Notation Consistency
- Cross-check every symbol against `planning/symbol_table.md`.
- Decision variables vs state variables vs parameters must be distinguished.
- Vector/matrix notation must be consistent (bold, arrow, or neither — pick one).

## 8. Figure and Table References
- Every `\ref{fig:...}` or "Figure X" must correspond to an actual figure file.
- Figure references must be in order (Fig.1 before Fig.2 in text).
- Every table reference must correspond to an actual table.
- Captions must include the main takeaway, not just a description.

## 9. Transition and Flow
- Between sections: one bridging sentence connecting to the next section.
- Between paragraphs: logical flow (therefore, however, in contrast, furthermore, specifically).
- Avoid "As mentioned above" / "As discussed previously" — restate briefly instead.
- Avoid "It is worth noting that..." / "It should be mentioned that..." — just state it.

## 10. Word Choice
- Prefer specific over vague: "RMSE improved by 35%" not "the error got better".
- Prefer simple over ornate: "use" not "utilize", "show" not "elucidate", "about" not "approximately" (unless precision matters).
- Remove filler: "It is important to note that", "Interestingly", "Remarkably".
- Remove redundant pairs: "various different", "basic fundamentals", "advance planning".

## 11. Voice
- Prefer active voice for clarity: "We applied TOPSIS to the indicator matrix" not "TOPSIS was applied to the indicator matrix".
- Use passive voice sparingly, mainly in Methods/Model Solution: "The weights were computed using the entropy method".
- Use "we" consistently (not "the authors", "this paper", "the research team").
- In Chinese→English translation: avoid literal translation of Chinese academic conventions.

## 12. Formatting Compliance
- Check contest-specific formatting: word count, page limit, font size, margin requirements.
- Section numbering is consistent.
- Reference format is consistent.
- Appendix materials are properly labeled.

# Section-Specific Polish Priorities

| Section | Top Priority |
|---------|-------------|
| Abstract | Claim calibration, numerical precision, word count |
| Problem Restatement | Clarity, no added requirements |
| Assumptions | Necessity check, impact statements |
| Symbols | Completeness, consistency, distinction of variable types |
| Model Construction | Formula correctness, notation consistency, assumption traceability |
| Model Solution | Procedural clarity, reproducibility |
| Results Analysis | Claim-evidence alignment, figure/table references |
| Robustness | Stable vs fragile separation, boundary conditions |
| Strengths & Limitations | Specificity, honesty |
| Conclusion | Subquestion coverage, claim calibration |

# Chinese-to-English Translation Notes

When the source text is in Chinese and needs translation to English:
- Do not translate literally. Translate the MEANING.
- Chinese academic writing often uses more hedging; keep only what the evidence supports.
- Chinese sentences tend to be longer; split into shorter English sentences.
- "本文" → "This paper" or "We" depending on context.
- "显然" / "显而易见" → avoid "obviously" unless truly obvious; use "clearly" only with strong justification.
- "一定的" → drop or replace with specific quantifier.
- "较好的效果" → must be quantified: "improved RMSE by X%" not "good results".

# Rules

- Polish language and structure; do not invent new content.
- Downgrade overclaims; do not upgrade weak claims to sound stronger.
- Flag unsupported claims as issues; do not silently remove or modify them.
- Do not change formulas without checking against the final method explanation.
- Do not add new references, experiments, figures, or numerical values.
- Do not remove limitations or uncertainty statements.
- Keep changes traceable — show what was changed and why.
- If the underlying argument is broken, flag it rather than polishing over it.

# Verification

Before handing off, verify:

- Every modified sentence is grammatically correct.
- Every formula cross-checked against the final method explanation.
- Every claim calibrated to match available evidence.
- Overclaims are flagged or downgraded.
- Notation is consistent across all sections.
- Figure/table references are in order and correspond to existing files.
- Contest formatting requirements are met.
- A change summary is produced.

# Failure modes

Stop and report a blocker if:

- A claim in the paper has no supporting evidence at all (not just weak evidence — NO evidence).
- A formula in the paper contradicts the final method explanation.
- A referenced figure or table does not exist.
- A numerical value in the paper cannot be found in any result file.
- The paper claims a result for a subquestion that has no final result analysis.

# Stop conditions

This skill must stop instead of guessing when:

- Fixing language would require changing the scientific meaning.
- The evidence for a claim is entirely absent.
- Multiple contradictory claims exist in the same section.
- A referenced artifact cannot be found.
- Continuing would hide a fundamental logical flaw under polished prose.

When stopping, output:
- the blocker
- the affected sentence or paragraph
- the missing or contradictory evidence
- recommended action

# Handoff

After polishing:
→ `quality-assurance-auditor`

With:
- polished section paths
- change summary (what was modified and why)
- flagged overclaims (downgraded or awaiting author decision)
- remaining issues needing author attention

# Examples

## Example 1: Overclaim downgrade

Original: "Our entropy-TOPSIS model demonstrates significantly better performance than all existing evaluation methods, achieving optimal ranking accuracy."

Polish: "The entropy-TOPSIS model improves score differentiation compared to the equal-weight baseline (standard deviation: 0.15 vs 0.08). Among the three candidate methods tested (equal-weight, entropy-TOPSIS, AHP-TOPSIS), entropy-TOPSIS was selected for its objective weight derivation and ranking stability under ±10% perturbation."

Changes:
- "significantly better than all existing methods" → downgraded to comparison with tested baselines only
- "optimal ranking accuracy" → removed (no ground-truth ranking exists)
- Added specific numerical evidence (std 0.15 vs 0.08)
- Added method selection context (3 candidates tested)

## Example 2: Notation fix

Original: "Let x_i be the score of city i. The weight w_j is computed by..."

Fixed: "Let $S_i$ be the composite score of city $i$. The indicator weight $\omega_j$ is computed by entropy method..."

Issue: `x_i` was used for scores in Q1 but for raw indicator values in Q2. Changed to `S_i` to match the global symbol table, and distinguished `\omega_j` (weight) from `w_j` (used elsewhere for a different variable).

## Example 3: Sentence split

Original (38 words): "After applying the entropy method to compute objective indicator weights and then using the TOPSIS method to compute the relative closeness of each city to the ideal solution, we obtained the final ranking as shown in Table 1."

Polished (two sentences, 15 + 14 words): "Entropy weighting produced objective indicator weights from data dispersion. TOPSIS then computed each city's relative closeness to the ideal solution, yielding the final ranking (Table 1)."
