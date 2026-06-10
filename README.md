<p align="center">
  <img src="docs/assets/logo.svg" alt="MathModeling-skills" width="640"/>
</p>

<p align="center">
  <a href="./README.md"><b>English</b></a> ·
  <a href="./README-zh.md">简体中文</a> ·
  <a href="./CLAUDE.md">Project Rules</a> ·
  <a href="./Initial%20Prompt.md">Initial Prompt</a> ·
  <a href="mailto:zjzhang0424@gmail.com">📧 Contact</a>
</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-2E9E44">
  <img alt="Skills" src="https://img.shields.io/badge/skills-28-1A6FC4">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-supported-E28E2C">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-supported-E28E2C">
</p>

---

> [!NOTE]
> **Update — this is now an assistant, not an autopilot.** The earlier version ran the whole contest end to end and left the user only clicking "confirm", which is closer to ghost-writing: it does not fit most contests' rules, and it does little for your own skills. This version hands the key judgments back to the user — the AI returns to a supporting role, and you stay in charge. The skill count went from 24 to 28. The previous full-auto version is kept intact on the [**`legacy-full-auto`**](https://github.com/zhnnky329/MathModeling-skills/tree/legacy-full-auto) branch; switch to it if you prefer the old behavior.

> A set of skills for math-modeling contests, built around the mistakes that tend to cost the most time. They sit behind a set of hard gates — two of which the user decides, not the AI — and a three-auditor layer that has the final say on whether the paper is ready to submit. The aim is not to automate more, but to make sure no step can quietly skip a check: every number in the paper traces back to a frozen snapshot, every reviewer leaves a file on disk, and no skill marks itself as "done".
>
> The principle it is built on: **the AI owns mechanical correctness; the user owns modeling judgment.** It runs the PoCs, freezes the numbers, render-checks the figures, and audits consistency. It does not choose the method, decide what a number means, or write the reasoning behind a choice — those belong to the user, and the gates fail on an empty or copy-pasted answer.
>
> Found a bug, or want to share how it went in a real contest? Email **[zjzhang0424@gmail.com](mailto:zjzhang0424@gmail.com)**, or open an issue.

## Why this exists

When a team loses a modeling contest, it is rarely because they did not know enough models. It is usually one of these:

- They misread what the problem was actually asking.
- They skipped the baseline and went straight to a complex model that nobody could explain later.
- The paper states a number that no script in the repo actually produces.
- A bug gets fixed late in the process, but the paper still carries the numbers from before the fix.

These are workflow problems, not modeling problems. The skills here are arranged to make these failures hard to hide.

## What's different

| | A typical pipeline | This one |
|---|---|---|
| How you move on | "this stage is done, next" | Each gate has an explicit pass condition. Fail it and everything downstream gets marked stale. |
| Which method, and why | The AI picks and writes the justification | The AI lays out candidates and runs the feasibility checks; **you** commit the choice and write the reason, in your own words. The gate fails on an empty or copy-pasted rationale (Gate G2.5). |
| From idea to code | A method is accepted if the math looks right | Each candidate ships with a ≤30-line PoC and a real number from running it on the actual data (Gate G2) |
| Code review | Someone says "looks fine" | A review file on disk with ≥ 5 specific things that were checked, file:line cited (Gate G3) |
| Numbers in the paper | Re-read from the latest results each time | Frozen into `frozen_numbers.json`. Changing one means logging the change and re-freezing (Gate G4) |
| "Done" | One QA pass | Three separate auditors. Any one fails, the paper doesn't ship (Gate G6) |
| Methods you dropped | Hang around the main folder | Get moved to `workspace/archived/` so they don't accidentally end up in the paper |

## The pipeline

```text
workflow-orchestrator (env ping at session start)
 ▼  problem-parser → problem-classifier → related-paper-analyzer       [ G1: PROBLEM_PARSED ]
 ▼  symbol-table-builder + model-assumptions-builder + data-auditor-cleaner
 ▼  method-selector   ── each candidate ships ≤30-line PoC + number    [ G2: METHOD_VALIDATED  ★ ]
 ▼  ── YOU commit the method choice + write why ──────────────────────  [ G2.5: CHOSEN_BY_HUMAN 👤 ]
 ▼  model-code-analyzer → {python,matlab}-model-code-generator
 ▼  code-reviewer (router) → {python,matlab}-code-reviewer             [ G3: CODE_REVIEWED ]
 ▼  result-report-generator ([REJECTED] archived)
 ▼  robustness-checker → final-method-explainer
 ▼  ── YOU render the result + stability verdicts ────────────────────  [ G4.5: JUDGED_BY_HUMAN 👤 ]
 ▼  figure-table-planner → math-figure-generator (render_check)
 ▼  solution-package-builder ── emits frozen_numbers.json              [ G4: RESULTS_FROZEN   ★ ]
 ▼  paper-section-writer (word floor + ≥3 discussion dims per number)  [ G5: PAPER_SECTION_READY ]
 ▼  paper-polisher → reference-manager
 ▼  Independent audit layer (all three must PASS):
       consistency-auditor · completeness-auditor · quality-assurance-auditor
                                                                       [ G6: AUDIT_LAYER_PASSED ]
 ▼  final assembly
```

★ marks the two stages where pipelines most often break down: G2 stops a method that looks good on paper but won't run on the real data; G4 stops a bug fix from leaving an outdated number in the paper. 👤 marks the two gates the user decides rather than the AI — the method choice (G2.5) and the result verdict (G4.5); neither passes on an empty or copy-pasted answer.

## The skills, by stage

### Stage 1 · Groundwork

Before any modeling begins, get the basics in order: what the problem is asking, what type each subquestion is, what data is available, and a single symbol table the whole team shares.

- **`workflow-orchestrator`** — Tracks where each subquestion stands, runs the gate checks, and confirms the environment at the start of a session.
- **`problem-parser`** — Breaks the problem into goals / objects / constraints / data / outputs / subquestions, written to `planning/parse/`.
- **`problem-classifier`** — Labels each subquestion with a task type, written to `planning/classification/`.
- **`related-paper-analyzer`** — Finds relevant literature without fabricating citations.
- **`symbol-table-builder`** — Maintains one shared symbol table, `planning/symbol_table.md`.
- **`model-assumptions-builder`** — Separates necessary assumptions from those made only for simplification, `planning/model_assumptions.md`.
- **`data-auditor-cleaner`** — Audits the raw data and produces a cleaned copy plus a report; the raw data under `data_raw/` stays read-only. Before cleaning, it confirms which attachment belongs to which subquestion, so the data is not used in the wrong place.

### Stage 2 · Method validation (Gate G2 ★)

Teams often discover only near the deadline that a method they had counted on does not run on the real data, when it is too late to switch. This stage is meant to surface that early.

- **`method-selector`** — Proposes 2–4 candidate methods per subquestion, each with a PoC under 30 lines that produces a concrete result on the real cleaned data. Candidates whose PoC fails are marked `[REJECTED]` and moved to `workspace/archived/`. It does not choose for the user; it lays out the candidates and their feasibility, and the user records which one and why at Gate G2.5. Outputs: `methods/Qx/qx_method_candidates.md` and `methods/Qx/poc/*`.
- **`decision-prompt-builder`** — At each decision point, it first poses 2–3 trade-off questions that only a person can answer, then gives the AI's suggestion, so the decision stays with the user. Used at every gate the user owns.
- **`modeler-decision-logger`** — A decision-level counterpart to `frozen_numbers.json`: it records the user's decisions in an append-only log. Every "why this method" statement in the paper must trace back to it, and the AI may not rewrite the reasoning on the user's behalf.

### Stage 3 · Code and review (Gate G3)

Write the code, then review it; the review is recorded as a file on disk, not a remark in chat.

- **`model-code-analyzer`** — Plans the `experiments/roundN/` layout and the `run_summary.json` fields before any code is written.
- **`python-model-code-generator`** — Generates `.py` when the target is `python`, with a fixed `SEED = 2026`.
- **`matlab-model-code-generator`** — Generates `.m` for MATLAB / 北太天元, avoiding Live Scripts, App Designer, and other features the contest environment may not support.
- **`code-reviewer`** — Detects the script language and routes to the matching reviewer.
- **`python-code-reviewer`** — Writes `code/Qx/reviews/qx_python_review.md` with at least 5 specific checks, each citing file:line, and lists every inequality constraint in a table so its direction can be verified.
- **`matlab-code-reviewer`** — The same for `code/matlab/Qx/reviews/qx_matlab_review.md`.

### Stage 4 · Results, robustness, figures, freeze (Gate G4 ★)

Turn the raw experiment outputs into two things: a package the writer can use directly, and a frozen JSON of every number that will appear in the paper. After the freeze, any change to a number must be logged and re-frozen rather than edited directly.

- **`result-report-generator`** — Produces a multi-method comparison report and a final analysis; methods are tagged `[CHOSEN] / [BACKUP] / [REJECTED]`, and rejected ones move to `workspace/archived/`.
- **`robustness-checker`** — Runs sensitivity, error, and baseline comparisons; writes `robustness/Qx/qx_robustness_report.md` with at least 5 checks.
- **`final-method-explainer`** — Writes the full explanation of the selected method, `methods/Qx/qx_final_method_explanation.md`.
- **`figure-table-planner`** — Sorts figures into four types: 1 diagnostic, 2 comparison, 3 paper, 4 appendix; diagnostic figures never enter the paper.
- **`math-figure-generator`** — Produces figures with matplotlib; each must pass `render_check_and_log()` (checking text overlap, out-of-canvas text, and fonts under 6.5pt) before it can be designated a paper figure.
- **`solution-package-builder`** — Builds the writer's package and emits `results/Qx/reports/frozen_numbers.json`, which should not be edited by hand.

### Stage 5 · Paper writing and audits (Gates G5 + G6)

The writer drafts the paper from the package and the frozen snapshot. Three independent auditors then check it: cross-file consistency, whether every reviewer file is present, and overall QA. If any one fails, the paper cannot be submitted.

- **`paper-section-writer`** — Drafts sections from the package, with a word-count floor per section; every numerical result must be discussed from at least three of: sensitivity, physical meaning, baseline comparison, cross-subquestion consistency, uncertainty.
- **`paper-polisher`** — Checks tense, hedging, overclaiming, and formula consistency within the document.
- **`reference-manager`** — Generates BibTeX and verifies that citations are real; fabricated citations are blocking.
- **`consistency-auditor`** — Compares every number, file name, and symbol in the paper against `frozen_numbers.json`, the files on disk, and the symbol table.
- **`completeness-auditor`** — Checks that every expected `*_review.md` / `*_audit.md` exists, meets the 5-pass-item bar, and is not stale.
- **`quality-assurance-auditor`** — Checks workflow completeness, the three core rules, and anti-fabrication; as the final gate, it signs off only after the other two auditors have.

## Installing

The recommended setup is to clone this into the folder where you'll do the contest work, so `CLAUDE.md` / `AGENTS.md` / `.claude/settings.json` apply automatically. A global install is also possible.

### Option A — clone into your contest project (recommended)

```bash
# inside the folder that will hold methods/ code/ results/ paper/ ...
git clone https://github.com/zhnnky329/MathModeling-skills.git .skills-tmp
mv .skills-tmp/.claude .claude
mv .skills-tmp/.codex .codex
mv .skills-tmp/CLAUDE.md .
mv .skills-tmp/AGENTS.md .
mv .skills-tmp/docs ./skills-docs
rm -rf .skills-tmp
```

Open the folder in **Claude Code** or **Codex**, and the 28 skills are picked up automatically. An opening message:

```text
Read CLAUDE.md, then run workflow-orchestrator. Our contest problem is in workspace/problem/. Follow the gates in order and do not skip.
```

### Option B — install globally for Claude Code

```bash
git clone https://github.com/zhnnky329/MathModeling-skills.git
cd MathModeling-skills

mkdir -p ~/.claude/skills
for d in .claude/skills/*/; do
  cp -R "$d" ~/.claude/skills/
done
```

Restart Claude Code, and the skills are available in any project. `CLAUDE.md` and `.claude/settings.json` still need to be in each contest project, since that is where the gate rules and guardrails live.

### Option C — install globally for Codex

```bash
git clone https://github.com/zhnnky329/MathModeling-skills.git
cd MathModeling-skills

mkdir -p ~/.codex/skills
for d in .codex/skills/*/; do
  cp -R "$d" ~/.codex/skills/
done
```

Restart Codex, and place `AGENTS.md` in each contest project for the gate rules.

### Updating later

```bash
cd MathModeling-skills && git pull
# then re-run the cp loop from B or C if you installed globally
```

### Opening prompt

Send the initial prompt at the start of a new conversation:

- English: [Initial Prompt.md](Initial%20Prompt.md)
- 中文: [Initial Prompt-zh.md](Initial%20Prompt-zh.md)

### Common follow-up prompts

- Resuming: `Q2 has experiment report round1 done. Let workflow-orchestrator decide whether to iterate or lock the method.`
- Just robustness: `Use robustness-checker for Q1. Inputs in results/Q1/reports/, baseline in results/Q1/experiments/round2/. Do not rerun the main model.`
- Triggering the audit layer: `All Qx sections drafted. Run consistency-auditor, then completeness-auditor, then quality-assurance-auditor.`

## Workspace layout

<details>
<summary>Click to expand</summary>

```text
project/
├── planning/                   # parse / classification / symbol table / assumptions / dashboard
├── methods/Qx/                 # candidates + iteration log + final method explanation + figure plan
│   └── poc/                    # ≤30-line PoC per candidate (Gate G2)
├── code/
│   ├── Qx/                     # Python; reviews/qx_python_review.md (Gate G3)
│   └── matlab/Qx/              # MATLAB (parallel structure)
├── results/Qx/
│   ├── experiments/roundN/     # figures / tables / metrics / logs / run_summary.json
│   └── reports/                # experiment + final analysis + solution package + frozen_numbers.json (Gate G4)
├── robustness/Qx/
├── paper/
│   ├── sections/               # word floor + ≥3 discussion dims (Gate G5)
│   ├── figures/                # Type 3 + Type 4 (render_check passed)
│   ├── audits/                 # cross_media / completeness / reference / polish (Gate G6)
│   ├── refs.bib  main.tex  qa_report.md
├── workspace/
│   ├── data_raw/               # read-only (settings.json deny)
│   ├── data_clean/
│   └── archived/<Qx>/<method>_REJECTED_roundN/
└── scratch/                    # temporary; nothing here has to be reproducible
```

A few hard rules: `data_raw/` is read-only. Every paper number lives in `frozen_numbers.json`. `[REJECTED]` methods get archived automatically. `frozen_numbers.json` is never edited by hand.

</details>

## What this isn't

- It's not a one-button paper generator.
- It won't invent missing data, results, or references.
- It won't write a number into the paper before some script has produced it.
- It won't claim a model is better than a baseline without a baseline and a robustness check actually existing.
- It doesn't touch your raw data.
- **It's not a ghost-writer.** The parts a judge grades and a student needs to learn — which method and why, what the numbers mean, how the assumptions are framed, what the contribution is — come from the user. The AI drafts the scaffolding around them and marks every judgment span as needing input; the gates do not pass on an empty box or text copy-pasted from the AI's own suggestion. If everything is left to the AI, the pipeline blocks before submission.
- It does not replace your judgment; the modeling decisions remain yours.

> **⚠️ Your contest's rules are yours to check.** AI-use policies differ sharply between contests and change every year — COMAP (MCM/ICM) currently allows disclosed AI assistance; CUMCM and several Chinese contests are originality-first and may not permit it at all. This repo encodes no contest's authoritative policy; its defaults aim at the strictest plausible reading. Every run can emit an `ai_use_disclosure.md` recording what was AI-drafted vs human-authored, so you can disclose honestly where required. Read your contest's current official rules before you rely on this — the final compliance call is yours.

## Documentation

- [CLAUDE.md](CLAUDE.md) — the project rules (gates, audit layer, the frozen-numbers convention).
- [AGENTS.md](AGENTS.md) — the Codex-side equivalent.
- [docs/implementation-targets.md](docs/implementation-targets.md) — choosing `python` vs `matlab`.
- [docs/matlab-beita-tianyuan-guidelines.md](docs/matlab-beita-tianyuan-guidelines.md) — keeping MATLAB code runnable in the contest environment.
- Per-skill: [.claude/skills/](.claude/skills/) · [.codex/skills/](.codex/skills/).

## Contact

For a bug, an idea, or feedback from a real contest, email **[zjzhang0424@gmail.com](mailto:zjzhang0424@gmail.com)**. Issues and PRs are welcome too.

## Acknowledgments

- **[nature-skills](https://github.com/Yuan1z0825/nature-skills)** — `math-figure-generator` draws on `nature-figure`'s figure contract, semantic palette, multi-panel layout, and SVG-first export. By [Yuan1z0825](https://github.com/Yuan1z0825), MIT.
- **[figures4papers](https://github.com/ChenLiu-1996/figures4papers)** — the production-grade plotting scripts that `nature-figure` is based on.

## License

MIT.
