---
name: model-assumptions-builder
description: Extract and maintain global and method-specific mathematical-model assumptions from the problem frame, active method cards, data profile, and risk probes, while leaving necessity and impact judgments to the human modeler.
---

# Inputs

- problem parse;
- active method cards;
- data profile and risk-probe summaries;
- question dependency map;
- existing assumptions and human decisions.

Read legacy candidate pools only during migration.

# Workflow

1. Extract explicit problem assumptions and method-induced assumptions.
2. Remove filler statements that do not affect model validity or interpretation.
3. For each assumption record:
   - scope and source;
   - modeling need;
   - applicable method/Qx;
   - validation evidence;
   - mitigation or fallback link.
4. Identify conflicts across Qx.
5. Present unresolved necessity/impact trade-offs in one compact choice card where possible.
6. Log human `assumption_necessity` decisions in `qx_decisions.jsonl`.
7. Save `planning/model_assumptions.md`, transcribing settled human labels and impacts with decision IDs.

# Assumption Fields

- ID;
- statement;
- scope;
- source and modeling need;
- human-confirmed type: necessary or simplifying;
- validation method/evidence;
- impact if violated;
- mitigation/fallback;
- decision ID.

# Rules

- Do not invent generic assumptions such as “data are accurate” unless they affect a real dependency.
- Do not finalize necessary/simplifying or impact judgments for the human.
- Do not leave many repeated sentinels in the final file; collect missing judgments through a choice card and stop finalization until answered.
- Revisit an assumption only when its method, evidence, or downstream use materially changes.

# Verification

- Every assumption has a modeling need and source.
- Human-owned labels trace to decisions.
- Probe/robustness evidence addresses load-bearing assumptions.
- Cross-Qx conflicts are resolved or explicit.
