---
name: completeness-auditor
description: Audit whether the semantic evidence required by the active lean or submission profile exists and is current, without requiring one verbose artifact per skill or an arbitrary number of pass bullets.
---

# Purpose

Check deliverable evidence, not whether every invoked skill left a ceremonial report.

# Lean Checks

Per active Qx, require as applicable:

- manifest;
- method card;
- human decision ledger;
- risk-probe summary;
- latest run summary.

Lean completeness does not require final reports, freeze, paper, or G6 artifacts.

# Submission Checks

Per Qx require:

- final method explanation;
- current language review JSON with all required named checks passing;
- final result analysis;
- robustness report;
- solution package;
- current frozen numbers;
- paper section and referenced figures.

Globally require symbol table, assumptions, references, consistency audit, completeness audit, and QA report.

# Workflow

1. Read `rigor_profile`.
2. Resolve active Qx from manifests or artifacts.
3. Check required artifacts and semantic fields.
4. Check staleness only against materially cited evidence.
5. Accept documented legacy equivalents during migration.
6. Save `paper/audits/completeness_audit.md` only in submission/final mode.

# Status

- `PRESENT`: required evidence exists and is current.
- `MISSING`: required evidence absent.
- `INSUFFICIENT`: artifact exists but required semantic fields/checks are missing.
- `STALE`: cited material evidence changed after approval/review.
- `NOT_APPLICABLE`: justified by task/profile.

# Rules

- Do not require `≥5` prose pass items.
- Do not require a report just because a skill ran.
- Do not mark a decision stale for unrelated code, formatting, or file changes.
- Do not treat legacy artifact count as proof of semantic completeness.
- Do not repair artifacts during audit.

# Verification

- Requirements match the active profile.
- Every gap names the missing evidence and producer/owner.
- Staleness links to a material changed source.
- Final verdict is `PASSED` only when all submission requirements are satisfied.
