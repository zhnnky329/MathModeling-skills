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
> The principle it is built on: **the AI owns mechanical correctness; the user owns modeling judgment.** It profiles data, runs method-specific risk probes, freezes numbers, render-checks figures, and audits consistency. It does not choose the method, decide what a number means, or invent the reasoning behind a choice.
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
| Which method, and why | The AI picks and writes the justification | You choose the trade-off; the AI screens a main candidate, a usable baseline, and at most one conditional fallback; **you** commit the route and reason (Gate G2.5). |
| From idea to code | A method is accepted if the math looks right | A time-bounded risk probe checks data coverage, assumptions, output degeneracy, perturbation sensitivity, and scale (Gate G2). |
| Code review | Someone says "looks fine" | A compact JSON review must pass named syntax, input, method-alignment, reproducibility, and output checks (Gate G3). |
| Numbers in the paper | Re-read from the latest results each time | Frozen into `frozen_numbers.json`. Changing one means logging the change and re-freezing (Gate G4) |
| Exploration cost | Full reports and audits at every step | `lean` keeps manifests, decisions, probes, and run summaries; `submission` adds freeze, paper, and final audits. |
| "Done" | One QA pass | Three separate final auditors. Any one fails, the paper doesn't ship (Gate G6). |
| Methods you dropped | Hang around the main folder | Get moved to `workspace/archived/` so they don't accidentally end up in the paper |

## The pipeline

```text
workflow-orchestrator (reads interaction_mode + rigor_profile)
 ▼  problem-parser → problem-classifier → related-paper-analyzer       [ G1: PROBLEM_FRAMED ]
 ▼  symbol-table-builder + model-assumptions-builder + data-auditor-cleaner
 ▼  YOU choose priorities/risks/budget → method-selector
       main + usable baseline + optional triggered fallback
       method-specific risk probe (including output concentration)     [ G2: METHOD_SCREENED  ★ ]
 ▼  ── YOU commit the method choice + write why ──────────────────────  [ G2.5: CHOSEN_BY_HUMAN 👤 ]
 ▼  model-code-analyzer → {python,matlab}-model-code-generator
 ▼  code-reviewer (router) → named-check JSON review                   [ G3: CODE_AND_EXPERIMENT_REVIEWED ]
 ▼  result-report-generator (report only at a decision point/final)
 ▼  robustness-checker → final-method-explainer
 ▼  ── YOU choose proceed / adjust / activate fallback ───────────────  [ G4: JUDGED_BY_HUMAN 👤 ]
 ▼  figure-table-planner → math-figure-generator (render_check)
 ▼  switch rigor_profile to submission
 ▼  solution-package-builder ── emits frozen_numbers.json              [ G4: RESULTS_FROZEN   ★ ]
 ▼  paper-section-writer                                               [ G5: PAPER_SECTION_READY ]
 ▼  paper-polisher → reference-manager
 ▼  Independent audit layer (all three must PASS):
       consistency-auditor · completeness-auditor · quality-assurance-auditor
                                                                       [ G6: AUDIT_LAYER_PASSED ]
 ▼  final assembly
```

★ marks the two load-bearing boundaries: G2 catches assumption, concentration, feasibility, and scale failures before full implementation; G4 prevents stale numbers from entering the paper. 👤 marks judgments owned by the user.

## The skills, by stage

### Stage 1 · Groundwork

Before any modeling begins, get the basics in order: what the problem is asking, what type each subquestion is, what data is available, and a single symbol table the whole team shares.

- **`workflow-orchestrator`** — Tracks where each subquestion stands, runs the gate checks, and confirms the environment at the start of a session.
- **`problem-parser`** — Breaks the problem into goals / objects / constraints / data / outputs / subquestions, written to `planning/parse/`.
- **`problem-classifier`** — Labels each subquestion with a task type, written to `planning/classification/`.
- **`related-paper-analyzer`** — Finds relevant literature without fabricating citations.
- **`symbol-table-builder`** — Maintains one shared symbol table, `planning/symbol_table.md`.
- **`model-assumptions-builder`** — Separates necessary assumptions from those made only for simplification, `planning/model_assumptions.md`.
- **`data-auditor-cleaner`** — Audits the raw data and produces a cleaned copy plus a compact data profile; the raw data under `data_raw/` stays read-only. Before cleaning, it confirms which attachment belongs to which subquestion, so the data is not used in the wrong place.

### Stage 2 · Method validation (Gate G2 ★)

Teams often discover only near the deadline that a method they had counted on does not run on the real data, when it is too late to switch. This stage is meant to surface that early.

- **`method-selector`** — Builds one main candidate, one usable baseline, and at most one conditional fallback. It writes `qx_method_card.md` and a risk-probe summary covering assumptions, data coverage, output degeneracy, perturbations, and scale.
- **`decision-prompt-builder`** — Presents compact choice cards at genuine modeling judgments. It asks about goals and trade-offs before algorithm names.
- **`modeler-decision-logger`** — Faithfully appends the user's answers to `methods/Qx/qx_decisions.jsonl`; no per-skill PENDING decision files are created.

### Stage 3 · Code and review (Gate G3)

Write the code, then review it; the review is recorded as a file on disk, not a remark in chat.

- **`model-code-analyzer`** — Plans the `experiments/roundN/` layout and the `run_summary.json` fields before any code is written.
- **`python-model-code-generator`** — Generates `.py` when the target is `python`, with a fixed `SEED = 2026`.
- **`matlab-model-code-generator`** — Generates `.m` for MATLAB / 北太天元, avoiding Live Scripts, App Designer, and other features the contest environment may not support.
- **`code-reviewer`** — Detects the script language and routes to the matching reviewer.
- **`python-code-reviewer`** — Writes `code/Qx/reviews/qx_python_review.json` with evidence for five named semantic checks.
- **`matlab-code-reviewer`** — Uses the same checks plus runtime and compatibility evidence.

### Stage 4 · Results, robustness, figures, freeze (Gate G4 ★)

Turn the raw experiment outputs into two things: a package the writer can use directly, and a frozen JSON of every number that will appear in the paper. After the freeze, any change to a number must be logged and re-frozen rather than edited directly.

- **`result-report-generator`** — Routine rounds stay compact; decision points and final rounds get reports. Rejection and archival happen only after the user's verdict.
- **`robustness-checker`** — Runs only risk-relevant sensitivity, error, baseline, and concentration checks; it does not pad a generic checklist.
- **`final-method-explainer`** — Writes the full explanation of the selected method, `methods/Qx/qx_final_method_explanation.md`.
- **`figure-table-planner`** — Sorts figures into four types: 1 diagnostic, 2 comparison, 3 paper, 4 appendix; diagnostic figures never enter the paper.
- **`math-figure-generator`** — Produces figures from saved evidence and visually verifies the rendered result before designation as a paper figure.
- **`solution-package-builder`** — Builds the writer's package and emits `results/Qx/reports/frozen_numbers.json`, which should not be edited by hand.

### Stage 5 · Paper writing and audits (Gates G5 + G6)

The writer drafts the paper from the package and the frozen snapshot. Three independent auditors then check it: cross-file consistency, whether every reviewer file is present, and overall QA. If any one fails, the paper cannot be submitted.

- **`paper-section-writer`** — Drafts from the package and frozen snapshot; human-owned physical meaning and contribution claims come from the decision ledger.
- **`paper-polisher`** — Checks tense, hedging, overclaiming, and formula consistency within the document.
- **`reference-manager`** — Generates BibTeX and verifies that citations are real; fabricated citations are blocking.
- **`consistency-auditor`** — Compares every number, file name, and symbol in the paper against `frozen_numbers.json`, the files on disk, and the symbol table.
- **`completeness-auditor`** — Checks semantic evidence required by the active profile rather than one verbose artifact per skill.
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

`.claude/skills/` and `.codex/skills/` are both complete standalone copies. You may install or use either tree independently; repository maintenance keeps every skill and its references present in both.

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
├── planning/
│   ├── parse/  classification/  manifests/Qx.json
│   ├── symbol_table.md  model_assumptions.md
│   └── session_config.json     # interaction_mode + rigor_profile
├── methods/Qx/
│   ├── qx_method_card.md  qx_decisions.jsonl
│   └── probes/risk_probe_summary.json
├── code/
│   ├── Qx/                     # Python; reviews/qx_python_review.json
│   └── matlab/Qx/              # MATLAB (parallel structure)
├── results/Qx/
│   ├── experiments/roundN/     # figures / tables / metrics / run_summary.json
│   └── reports/                # final analysis + solution package + frozen_numbers.json
├── robustness/Qx/
├── paper/
│   ├── sections/
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
