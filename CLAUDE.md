# Mathematical Modeling Workflow

`AGENTS.md` is the single source of truth for workflow policy, gates, artifacts, human decisions, risk probes, freezing, and audits. Read and follow it before invoking a modeling skill.

`.claude/skills/` is a complete standalone skill tree, not an adapter to `.codex/skills/`. When maintaining a shared skill, keep the full counterpart in both trees and validate both; do not replace either copy with wrappers or symlinks.

The native distribution package lives under `plugins/mathmodeling-skills/`. After updating both standalone trees, run `scripts/sync-plugin.sh` and validate both platform manifests before release.

# Claude-Specific Operating Rules

- Do not duplicate the full workflow contract in individual responses or generated artifacts.
- Load only the skill needed for the current gate and only the referenced material needed for the current task.
- Pass paths plus a compact evidence digest between skills; do not paste entire upstream reports when paths are available.
- Treat `planning/manifests/Qx.json` as the state source. Derive status views instead of maintaining duplicate dashboards.
- Use `planning/session_config.json` with independent `interaction_mode` and `rigor_profile` controls. Read legacy `mode` only for compatibility.
- In `lean`, create only the lean artifact set defined in `AGENTS.md`.
- In `submission`, add final explanations, reviews, reports, frozen numbers, paper sections, and the three final audits.
- Capture human judgments in `methods/Qx/qx_decisions.jsonl`. Do not create new per-skill `*_modeler_decision.md` files.
- Never originate a human-owned modeling choice, rationale, confidence verdict, physical interpretation, or submission authorization.
- Replace universal PoCs with the method-specific risk probe defined in `AGENTS.md`; do not use source-line count as evidence quality.
- Fully implement only the approved main method and usable baseline. Activate a fallback only when its recorded trigger fires.
- Persist full logs only for failures or reproducibility needs.
- Run scoped consistency checks only for `CANONICAL` or `FROZEN` changes. Run all three auditors before final assembly.
- Never edit `frozen_numbers.json` manually.

# Compatibility

During migration, skills may read these legacy artifacts:

- `planning/progress_dashboard.md`
- `methods/Qx/qx_method_candidates.md`
- `methods/Qx/qx_method_iteration_log.md`
- `methods/Qx/qx_decision_log.md`
- `methods/Qx/decisions/*_modeler_decision.md`
- `code/Qx/reviews/qx_<lang>_review.md`

Do not require or emit them for new work when the new manifest, method card, JSONL decision ledger, probe summary, and JSON review exist.
