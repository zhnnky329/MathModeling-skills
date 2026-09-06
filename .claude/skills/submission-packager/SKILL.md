---
name: submission-packager
description: Assemble the final contest deliverable after Gate G6 — one paper Markdown plus a flat per-question supporting folder (q1..qn) holding at most two runnable consolidated scripts (model + figures), paper-cited figures, and per-question consolidated workbooks for result tables and required data — using evidence-driven selection, a human-confirmed inclusion list, and a reproducible packaging manifest kept outside the package.
---

# Purpose

Turn the deep workspace tree into the two things a contest actually accepts: one paper Markdown and one clean supporting-materials folder. Each question's code is consolidated into at most two runnable scripts; everything else is selected from recorded evidence, never hand-picked. Packaging never modifies the workspace tree — consolidated files are written only into the package.

# Preconditions

- `rigor_profile` is `submission` and G6 has passed, or the human explicitly authorizes packaging before audits complete.
- The subquestions are identifiable from `planning/manifests/Q*.json` (fall back to `results/Q*` directories).
- A final paper Markdown exists (`paper/main.md` by default) or the human supplies its path.
- Each question has a final experiment round with a complete `run_summary.json`.

# How to Run

All selection, consolidation, comment pruning, read rewriting, and checks are performed by the deterministic consolidator: the bundled script `scripts/package_submission.py` (stdlib only, Python 3.8+). Do not reimplement them by hand — hand-built packages cannot reproduce the manifest.

1. **Dry run.** `python <skill-dir>/scripts/package_submission.py --workspace <ws> --dry-run` prints the per-qN inclusion list (files, kinds, sources), planned consolidations and workbook merges, warnings, and problems. Present that output as the inclusion list for Human Confirmation.
2. **Package.** After the human confirms, rerun the same command without `--dry-run`. Problems block writing; the manifest is written last.

Flags: `--paper`, `--out`, `--paper-name`, `--support-dir-name` for non-default paths; `--zip` also archives the package; `--force` rebuilds an existing output dir; `--no-merge-code` / `--no-merge-data` / `--no-merge-tables` disable individual consolidation steps.

# Package Structure

```text
submission/
├── <paper>.md
└── 支撑材料/
    ├── q1/    # flat: q1_model.py [+ q1_figures.py] + figures + workbooks; no subfolders
    ├── q2/
    └── ...
```

`qN` is the submission-facing name of `Qx`, ordered by question number. Every file sits directly inside its `qN` folder.

# Selection Rules

Derive the inclusion list from evidence. Do not hand-pick files.

1. **Question order.** Read `question_id` from `planning/manifests/Q*.json`; map `Q1→q1`, `Q2→q2`. Fall back to naturally sorted `results/Q*` directories.
2. **Final round.** For each Qx, use the highest-numbered `results/Qx/experiments/roundN/` containing a complete `run_summary.json`. Never take files from earlier rounds.
3. **Code.** Take scripts recorded in that `run_summary.json` (fall back to `code/Qx/` when it lists none). Then resolve local imports transitively: any sibling `.py`/`.m` file a selected script imports or calls is also selected. Selection ends here; packaging then consolidates the selected Python into at most two runnable files per question (see Code Consolidation). MATLAB files are copied unchanged.
4. **Paper figures.** Parse `paper/sections/qx.tex` for `\includegraphics{...}` and resolve each path against `paper/`, `paper/figures/`, or by unique basename. A figure belongs to every qN whose section references it; a figure referenced only by non-question sections (e.g., an appendix) is copied into every qN and flagged. Unreferenced figures are excluded — this is what keeps Type 1 diagnostics out of the package.
5. **Result tables.** Take `tables/` and `metrics/` files from the final round only.
6. **Data.** Take input files listed in `run_summary.json` plus data files referenced by the selected code (search `workspace/data_clean/` first, then `workspace/data_raw/` only if no cleaned copy exists).

# Naming

- Consolidated code is named `qN_model.py` / `qN_figures.py`; data files keep their original names (the code reads them by name). Consolidation never renames what the code itself references.
- Figures and tables gain a `qN_` prefix (`q1_rmse_by_model.png`) for cross-referencing with the paper.
- On a name collision inside one qN, keep the first file, rename later ones with a `_2` suffix, and log the conflict. Never overwrite silently.

# Code Consolidation

Selected Python is merged into at most two runnable files per question — prefer one. `qN_model.py` receives every non-figure entry plus helpers (inlined in dependency order, local import statements dropped, top-level imports hoisted and deduped). Only when figure entries exist alongside model entries does a second `qN_figures.py` receive them. Each file carries a one-line `# 整合自 …` provenance header and must pass a `compile()` check before writing.

- Comments are pruned by rule, not judgment: decision-log / TODO / debug / history / backup notes and commented-out code lines are removed; units, formulas, parameter meanings, and docstrings stay.
- Data reads are rewritten so the package stays runnable: a CSV whose content moved into a workbook sheet must be read only via `read_csv("<literal>")` string literals; those calls become `read_excel("qN_data.xlsx", sheet_name="…")` (or `qN_results.xlsx`), and unquoteable path literals of files kept loose are shortened to bare filenames. A CSV referenced in any other way (`open()`, `loadtxt`, variables, f-strings) is never merged — it stays a loose file so the code still runs.
- Consolidation is skipped (files copied unchanged, flagged in warnings) when module stems collide, a source fails to parse, or the merged file fails to compile. `--no-merge-code` disables it.
- MATLAB `.m` files are copied unchanged; the two-file cap applies to Python only.

# Consolidation

When two or more selected sources of the same kind belong to one question, consolidate them into one multi-sheet workbook instead of copying them loose. Result-side metrics `.json` always goes into the workbook, even when it is the only source:

- Result tables → `qN_results.xlsx` (final-round `tables/` and `metrics/` CSVs, plus readable metrics `.json` files). Each JSON becomes one tabular sheet: a list of records becomes a records table, a dict of equal-length arrays becomes columns, anything else becomes `key`/`value` rows with dotted keys for nested fields. Numbers keep their numeric type.
- Cleaned input data → `qN_data.xlsx` (CSVs the code reads from `workspace/data_clean/` or `data_raw/`). Data-side `.json`, and any CSV the consolidated code does not read through a plain `read_csv("…")` literal, stays a separate file so the code keeps running.
- Each source becomes one sheet named after its file stem; a final `_sources` sheet maps every sheet back to its original workspace path, so the package stays self-explanatory.
- A single CSV source, and every artifact that is not merged (`.xlsx`, `.mat`, data-side `.json`, figures, code), is copied as its own file. A workbook is a pure consolidation: no values are edited.

The goal is zero loose `.json` on the result side: metrics belong in `qN_results.xlsx`, not as scattered files.

Trade-off to state when presenting the inclusion list: when code is consolidated, its `read_csv` calls are rewritten to the workbook sheets, so the package stays runnable as-is. Without code consolidation (`--no-merge-code` or a skipped consolidation), `qN_data.xlsx` breaks direct re-runs and the waiver is recorded in the manifest. Users who need the original split files disable merging with `--no-merge-data` / `--no-merge-tables`.

# Human Confirmation

Before copying, present the full inclusion list (per qN: files, kinds, sources) and unresolved items. Copy only after the human confirms. This is the packaging sign-off; do not infer it.

# Packaging Manifest

Write `planning/submission_packaging_manifest.json` — never inside the package — recording: timestamp, workspace, output path, paper Markdown source and destination, and per-question entries `{source, destination, kind, provenance}` where provenance is one of `summary_listed`, `import_resolved`, `section_referenced`, `shared_section`, `data_detected`, `consolidated`. Consolidated code entries list every source file, destination, and the pruned-comment count. Include collision notes, unresolved references, warnings, and all check results. Re-running the packager on the same tree must reproduce the same package.

# Verification

- Every qN folder is flat: no subdirectories inside.
- Every figure referenced by a section exists in that question's qN folder.
- Each qN holds at most two `.py` files; every consolidated file passed a `compile()` check; when consolidation was skipped, every local import in the copied code resolves inside the same qN folder.
- Every data file the consolidated code reads exists in the same qN folder or is read from a `qN_data.xlsx` / `qN_results.xlsx` sheet by a rewritten `read_excel` call.
- Every consolidated workbook contains one sheet per selected source plus `_sources`.
- The paper Markdown exists in the package.
- If `results/Qx/reports/frozen_numbers.json` exists, every referenced `source_file` still exists in the workspace (warning-level lineage check).

Report checks compactly; failures block the package until resolved or explicitly waived by the human.

# Rules

- Data, figures, and the paper are copied only. Code is transformed only by the deterministic consolidator (inline, dedupe, prune, rewrite reads); never hand-edit packaged code to make packaging easier, and never change computation logic.
- Never include decision ledgers, method cards, probes, audits, run summaries, logs, earlier experiment rounds, or archived REJECTED material.
- Never place the manifest or any workflow artifact inside the package.
- The package is regenerated, not hand-maintained: rebuild it after any CANONICAL or FROZEN change, and log the rebuild reason in `freeze_change_log.md` when frozen values moved.
- Do not delete or rearrange the workspace tree.

# Output

Return: package path, per-qN file counts by kind, check results, and the manifest path. Flag anything needing human review: missing paper Markdown, unresolved imports or figure references, code that could not be consolidated (copied unchanged), CSVs kept loose because their reads were not rewritable, `read_csv` calls with non-literal paths (variables or f-strings) whose package runnability could not be verified, data that could only be found in `data_raw/`, and shared-section figures copied into every qN.
