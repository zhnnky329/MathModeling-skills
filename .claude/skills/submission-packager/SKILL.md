---
name: submission-packager
description: Package a G6-approved mathematical-modeling paper and its exact supporting code, data, results, and figures without changing their behavior or the workspace.
---

# Purpose

Create one paper Markdown and one `支撑材料/` directory after the submission audits. Preserve selected code, inputs, and outputs under their workspace-relative paths. The packaged code must retain its module imports, CSV parsing, and normal working-directory paths. A packaging manifest stays outside the package at `planning/submission_packaging_manifest.json`.

# Preconditions

- `planning/session_config.json` selects `rigor_profile: submission`.
- Every `planning/manifests/Qx.json` is at G6 and allows final assembly.
- `paper/audits/cross_media_consistency_audit.md`, `paper/audits/completeness_audit.md`, and `paper/qa_report.md` each contain an explicit `Verdict: PASSED` line. Ask the relevant auditor to record the verdict when an older report omits it; do not infer passage from file existence.
- The paper and freezes have not changed after those audits. Renew affected audits when they have.
- Each Qx has a current `frozen_numbers.json`. Its source files identify one successful experiment round; that round's `run_summary.json` lists `scripts`, `inputs`, and `outputs` as workspace-relative paths. Update canonical run evidence through the normal workflow when a field is missing. Never select a round by its number alone.
- A final `paper/main.md` exists, or supply another Markdown with `--paper`.

If the human explicitly authorizes packaging before G6, record their choice and rationale as a `DECIDED` human `packaging_waiver` in a decision ledger. Pass its `decision_id` with `--allow-unaudited`. The package manifest records this waiver and every failed gate or audit; never label it G6-approved.

# Workflow

1. Run `python <skill-dir>/scripts/package_submission.py --workspace <ws>` with Python 3.9 or newer. This is a dry run and prints every copied source, its destination, blocked items, and a SHA-256 plan digest. Check the actual contest's submission format and present the full inclusion list to the human.
2. After the human confirms that exact list, run the same command with `--confirm <plan digest>`. A changed source or plan blocks packaging. `--out` selects another output directory. `--force` replaces only a previous, unchanged package recorded in the external manifest.
3. The script copies selected source files into a staging directory, preserves their workspace-relative paths, rewrites only the packaged Markdown's image paths, checks Python syntax, then moves the verified stage into place. It rejects output paths containing the workspace or selected sources. The original workspace and the frozen sources stay untouched.
4. When a safe reproduction command is available, pass `--verify-command 'python code/Q1/run_all.py'` (repeat per required command). Commands execute from the packaged `支撑材料/` directory after copied frozen outputs are removed, so they must recreate those outputs. Numerical JSON claims with a `$.path` locator are checked against frozen values using `--atol` and `--rtol`. Review command side effects before running. A missing command or unsupported locator is reported as `UNVERIFIED`, never as a runtime pass. MATLAB execution requires a compatible local runtime and an explicit command.
5. Review the external manifest, package file hashes, runtime status, and actual Markdown image links. Only describe the package as runnable when the required reproduction checks passed.

# Selection and limits

- Code comes from `run_summary.json` and its local Python/MATLAB dependencies. Inputs come from the summary and literal data paths in selected code. Outputs come from the summary and frozen sources. Paper images come from references in the delivered Markdown.
- Preserve filenames and directories. Do not consolidate modules, prune comments, convert CSV files, rename data, or copy exploratory rounds, decision ledgers, audit files, or logs into `支撑材料/`.
- The paper is the only Markdown at the package root. Local paper images are copied beneath `支撑材料/` and their references in the packaged paper are updated. Unresolved image paths block packaging.
- The manifest records evidence hashes, exact source-to-destination mapping, gate and audit evidence, selected frozen rounds, the confirmation digest, package hashes, and runtime status.
