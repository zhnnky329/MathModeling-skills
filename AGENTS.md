# Core Philosophy

- **The AI owns mechanical correctness; the human owns modeling judgment.** Assistant for the engineering discipline, not a solver or paper-writer. AI keeps numbers traceable, runs PoCs, audits, render-checks, enforces gates. The human chooses the method and says why, decides what a number means, judges results, frames assumptions, authorizes submission. A skill must never originate, on the human's behalf, a judgment a judge would grade.
- Start from goals, objects, constraints, data, outputs, variables, relationships, and checkable conclusions.
- Do not start from model names or favorite techniques.
- Separate assumptions, observations, derivations, and validated conclusions.

# Workflow Discipline

- Parse the problem before classifying it.
- Classify the task before selecting methods.
- Generate a candidate method pool before committing to one method.
- Validate the method plan before writing code or paper text.
- Run multi-round experiments before locking in the final method.
- Keep every change minimal, traceable, and easy to review.
- **Change-propagation rule (P1)**: After modifying any file under `code/Qx/`, `methods/Qx/`, `results/Qx/reports/`, or `planning/`, grep the entire workspace for references to the changed artifact (symbol name, parameter name, file path, numerical value), list every file that now may be stale, and either update it in the same turn or flag it as STALE with recommended repair. Specifically:
  1. `grep -rn '<changed_identifier>' methods/ code/ results/ paper/ planning/` before claiming "done".
  2. If the changed file is under `code/Qx/` and `frozen_numbers.json` exists for that Qx, mark the freeze as stale in `results/Qx/reports/freeze_change_log.md`.
  3. After any multi-file change, run `consistency-auditor` for the affected Qx as an incremental check — do not defer to the final G6 run.

# Workflow Gates (G1 – G6)

Gates are not stages. A stage is "where I am"; a gate is "what I must satisfy to leave". The orchestrator evaluates each gate against an explicit `enter_condition / pass_criteria / fail_fallback` contract. See `.codex/skills/workflow-orchestrator/SKILL.md` for the full contract.

- **G1 PROBLEM_PARSED**: parse + classification exist.
- **G2 METHOD_VALIDATED** (load-bearing — method→code boundary): each candidate has a ≤30-line PoC + feasibility number. No PoC ⇒ not validated.
- **G2.5 METHOD_CHOSEN_BY_HUMAN** (human-decision gate, pilot): `methods/Qx/decisions/method-selector_modeler_decision.md` is `DECIDED` by the human with a non-empty, non-copied, evidence-citing rationale. `method-selector` only emits `[CANDIDATE — PoC PASS]` + an AI suggestion; the human commits the choice. `code_generation_allowed_Qx = G2 ∧ G2.5`. The orchestrator never fills the decision artifact or infers the choice from the AI suggestion.
- **G3 CODE_REVIEWED**: reviewer artifact exists at `code/Qx/reviews/qx_<lang>_review.md` with ≥ 5 explicit pass items.
- **G4.5 RESULTS_JUDGED_BY_HUMAN** (human-decision gate): before the freeze, the human renders the result verdict (`result-report-generator` → `qx_result_verdict`) and stability verdict (`robustness-checker` → `qx_stability_verdict`, citing a number). `[REJECTED]` archival fires only off a human tag. `freeze_allowed_Qx = G3 ∧ G4.5`. The why-this-method narrative is transcribed from the decision log, not re-authored.
- **G4 RESULTS_FROZEN** (load-bearing — results→paper boundary): requires G4.5 passed + package sign-off (`solution-package-builder` → `qx_package_signoff`). `frozen_numbers.json` exists and is newer than every source file; solution package sources all numbers from it; every "why we chose X" traces to a decision_id.
- **G5 PAPER_SECTION_READY**: section meets word-count floor; every numerical result has ≥ 3 discussion dimensions; every figure passes render-check.
- **G6 AUDIT_LAYER_PASSED**: all three independent audits PASSED (see "Independent Audit Layer" below).

Rules:
- Do not select methods before G1.
- Do not generate code before G2 (every candidate must have a PoC).
- Do not write numerical paper claims before G4 (numbers must be frozen).
- Do not hand a subquestion to the paper writer before the three critical rules are satisfied.
- Do not assemble the final paper before G6.
- A gate failure marks all downstream artifacts DIRTY — files at later stages are not automatically valid.

# Independent Audit Layer

`workflow-orchestrator` does NOT decide "completion". Three orthogonal auditors do — and any one of them failing blocks final assembly:

1. **consistency-auditor** → `paper/audits/cross_media_consistency_audit.md`
   Cross-media facts (numbers / file names / symbols / parameters) match across tex ↔ code ↔ frozen_numbers.json ↔ symbol_table.md.
2. **completeness-auditor** → `paper/audits/completeness_audit.md`
   Every skill that claims "完成" produced a substantive artifact on disk with ≥ 5 explicit pass items. Verbal completion does not count.
3. **quality-assurance-auditor** → `paper/qa_report.md`
   Workflow completeness, three critical rules, anti-fabrication, paper quality.

A single auditor's "✅" is NOT sufficient. The three are orthogonal — they catch different failure modes. Treat the entire layer as Gate G6.

# Frozen Numbers Convention

Numbers flow code → results → paper. Without a freeze layer, a bug fix in code silently shifts the paper's numbers. To prevent this:

- After `solution-package-builder` runs for Qx, it MUST emit `results/Qx/reports/frozen_numbers.json` capturing every numerical claim with provenance: `{value, source_file, source_line, frozen_at, frozen_by_skill}`.
- The solution package and all downstream paper sections source numerical claims from this file, not from raw results.
- A frozen snapshot is **immutable** by convention. To change a frozen number, the modeler must explicitly walk the three-step:
  1. **解冻** — log the reason in `results/Qx/reports/freeze_change_log.md`.
  2. **修改** — update the canonical source (code or analysis report); re-run experiments if needed.
  3. **重冻结** — re-invoke `solution-package-builder` to regenerate `frozen_numbers.json`.
- Never edit `frozen_numbers.json` by hand.
- `consistency-auditor` checks freeze staleness: if any `code/Qx/*` file's mtime is newer than `frozen_at`, the snapshot is STALE.

# Rejected-Method Archival Convention

Failed or eliminated candidate methods do not stay in the main code tree. Once `result-report-generator` or `method-selector` marks a method as `[REJECTED]`:

- Move its PoC script, code, and output figures to `workspace/archived/<Qx>/<method>_REJECTED_roundN/`.
- Keep a one-line breadcrumb in `methods/Qx/qx_method_iteration_log.md` explaining why it was rejected.
- Main tree keeps only `[CHOSEN]` and `[BACKUP]` methods.

# Per-Question Delivery Chain (MANDATORY)

For each subquestion Qx, it is FORBIDDEN to treat "code ran successfully" as "the subquestion is done."

Every subquestion must complete the following chain:

```
Stage 1:  建模手提出多个候选方法
          → methods/Qx/qx_method_candidates.md

Stage 2:  编程手实现多候选方法, 运行实验
          → code/Qx/*.py (or *.m)
          → results/Qx/experiments/roundN/

Stage 3:  编程手生成实验报告, 对比各方法
          → results/Qx/experiments/roundN/qx_experiment_report_roundN.md

Stage 4:  建模手根据实验报告修改、淘汰或合并方法
          → methods/Qx/qx_method_iteration_log.md

Stage 5:  多轮迭代后 (重复 Stage 2-4), 建模手确定最终方法
          → State: Final Method Selected (confirmed by modeler)

Stage 6:  AI/建模手写最终方法详解
          → methods/Qx/qx_final_method_explanation.md

Stage 7:  编程手/result-report-generator 生成最终结果分析
          → results/Qx/reports/qx_final_result_analysis.md

Stage 8:  robustness-checker 执行稳健性分析
          → robustness/Qx/qx_robustness_report.md

Stage 9:  solution-package-builder 生成论文手材料包
          → results/Qx/reports/qx_solution_package_for_writer.md

Stage 10: 论文手撰写 Qx 论文段落
          → paper/sections/qx.tex (or .md)

Stage 11: 建模手审核论文模型部分, 编程手审核论文结果和图表

Stage 12: 审核通过后 Qx 状态改为 Finalized
```

If `qx_final_method_explanation.md`, `qx_final_result_analysis.md`, or `qx_solution_package_for_writer.md` is missing, that subquestion MUST NOT enter the paper writing stage.

# Minimum Files Per Subquestion

Each subquestion Qx must have at least these 7 files before being considered "Ready for Writer":

| # | File | Primary Author | Purpose |
|---|------|---------------|---------|
| 1 | `methods/Qx/qx_method_candidates.md` (with PoC under `methods/Qx/poc/`) | 建模手 + method-selector | 候选方法池 + 每个候选 ≤30 行 PoC |
| 2 | `methods/Qx/qx_method_iteration_log.md` | 建模手 + 编程手 | 方法迭代记录 (含 [REJECTED] 归档 trace) |
| 3 | `methods/Qx/qx_final_method_explanation.md` | 建模手 + final-method-explainer | 最终方法详解 |
| 4 | `code/Qx/reviews/qx_<lang>_review.md` (≥ 5 通过项) | python/matlab-code-reviewer | 代码审查记录 |
| 5 | `results/Qx/reports/qx_final_result_analysis.md` | 编程手 + result-report-generator | 最终结果分析 |
| 6 | `results/Qx/reports/qx_solution_package_for_writer.md` | solution-package-builder | 论文手材料包 |
| 7 | `results/Qx/reports/frozen_numbers.json` | solution-package-builder | 不可变数字快照 (Gate G4) |

# Three Critical Rules (ENFORCED AT GATES)

These three rules are enforced by `workflow-orchestrator` and `paper-section-writer`. Violation of any rule means the subquestion is NOT Ready for Writer.

## Rule 1: 没有最终方法详解，不准写最终论文

`paper-section-writer` MUST NOT write final paper sections for Qx based on `qx_method_candidates.md` or early method plans. The file `methods/Qx/qx_final_method_explanation.md` MUST exist first.

## Rule 2: 没有最终结果分析，不准交给论文手

Program execution outputs alone are NOT a deliverable. The programmer (or `result-report-generator`) MUST produce `results/Qx/reports/qx_final_result_analysis.md` before the writer can proceed.

## Rule 3: 论文手只看材料包，不从零散 results 里猜

The paper writer's primary source for Qx is `results/Qx/reports/qx_solution_package_for_writer.md`. If this file is missing, Qx is NOT Ready for Writer, and the writer should not hunt through scattered results.

# Figure Type Classification

All figures must be classified into one of four types:

| Type | Name | Audience | Paper Use |
|------|------|----------|-----------|
| Type 1 | 诊断图 Diagnostic | 建模手 (modeler) | NOT for paper — internal model debugging only |
| Type 2 | 对比图 Comparison | 建模手 + 论文手 | MAY appear in paper — supports method selection narrative |
| Type 3 | 论文图 Paper | 论文读者 (judges) | MUST appear in paper — supports main claims |
| Type 4 | 附录图 Appendix | 论文读者 (supplementary) | Referenced from main text, shown in appendix |

Type 1 diagnostic figures must NOT appear in the final paper. Type 3 paper figures must be publication-quality (≥300 dpi, clear labels, informative captions).

# Experiments Output Structure

Every round of experiments MUST output to:

```
results/Qx/experiments/roundN/
├── figures/          # All generated figures
├── tables/           # All result tables (.csv)
├── metrics/          # All evaluation metrics (.csv, .json)
├── logs/             # Execution logs
└── run_summary.json  # Machine-readable execution record
```

`run_summary.json` must record: question ID, round number, methods executed, their statuses, input/output files, metrics summaries, random seeds, and environment info.

# Project Structure (Recommended)

```
project/
├── planning/                   # Global planning: parse, classify, symbol table, assumptions, dashboard
│   ├── parse/                  # Problem parse outputs
│   ├── classification/         # Problem classification outputs
│   ├── symbol_table.md         # Unified symbol table across all subquestions
│   ├── model_assumptions.md    # Global model assumptions
│   ├── question_dependency.md  # Subquestion dependency map
│   └── progress_dashboard.md   # Live progress tracking
├── methods/                    # 建模手区: method design and iteration
│   └── Qx/                     # Per-subquestion method artifacts
├── code/                       # 编程手区: executable code
│   └── Qx/                     # Per-subquestion code
├── results/                    # 正式结果区: experiment outputs and reports
│   └── Qx/
│       ├── experiments/        # Raw experiment outputs by round
│       │   └── roundN/
│       └── reports/            # Analysis reports and solution packages
├── robustness/                 # 稳健性分析区
│   └── Qx/                     # Per-subquestion robustness artifacts
├── paper/                      # 论文手区: final paper
│   ├── sections/               # Paper section drafts
│   ├── figures/                # Final paper figures (Type 3 + Type 4)
│   ├── main.tex                # Main paper file
│   └── qa_report.md            # QA report
├── docs/                       # Long-term reference materials
│   ├── references/             # Method references
│   ├── past_papers/            # Example excellent papers
│   └── templates/              # Paper templates, report templates
└── scratch/                    # Temporary exploration (not for final delivery)
```

# Symbol Discipline

- Create a unified symbol table early (at `planning/symbol_table.md`).
- Same meaning must use the same symbol across all subquestions.
- Different meanings must use different symbols.
- Distinguish: decision variables, state variables, parameters, inputs, intermediate values, and outputs.
- Every symbol must be defined before first use.
- Include units where applicable.

# Model Assumptions

- State model assumptions at `planning/model_assumptions.md` early, and refine them.
- Distinguish "necessary" assumptions (model breaks without them) from "simplifying" assumptions (model works approximately without them).
- Every assumption must be linked to a modeling need.
- State the possible impact if an assumption is violated.
- Do not include filler assumptions that don't affect the model.

# Artifact Discipline

- Treat problem parses, method plans, cleaned data, scripts, results, figures, robustness reports, and paper sections as traceable artifacts.
- Claims must point back to artifacts.
- Preserve artifact lineage from problem statement to final delivery.

# Modeling Rules

- Define the problem structure before proposing methods.
- Generate 2-4 candidate methods per subquestion — do not commit to the first idea.
- Match model choice to task type, available data, interpretability needs, and contest constraints.
- Every main model must have a baseline.
- Do not choose complex models only because they look advanced.
- Do not invent missing evidence.
- Final method selection happens AFTER experiments, by the modeler reviewing experiment reports.

# Coding Rules

- Generate code only from a validated method plan.
- Code must produce output in the experiments/roundN/ structure.
- Prefer clear, minimal, reviewable implementations over clever ones.
- Do not hide assumptions inside code.
- Save all outputs to files (CSV, JSON, PNG) — do not rely on console output only.
- Use fixed random seeds for reproducibility.

# Paper Writing Rules

- Write from validated artifacts, not from guesswork.
- The solution package (`qx_solution_package_for_writer.md`) is the primary source.
- Keep claims aligned with actual models, data, figures, and checks.
- Do not fabricate references, numerical results, experiments, or conclusions.
- Do not write final paper sections for Qx if any of the three critical rules are violated.
- Method description must match the final method explanation, not an early candidate pool.
- Results must come from the final result analysis, not raw experiment outputs.
- Mention eliminated methods to demonstrate thoroughness.

# Verification and QA

- Check logic, units, definitions, and output consistency before handoff.
- Robustness or sensitivity checks are required before final delivery.
- The three independent auditors (consistency / completeness / QA) are orthogonal — all must PASS before final assembly. A single auditor's "✅" is NOT sufficient.
- Every major claim must have at least one supporting robustness check or a stated limitation.
- Reviewer / auditor / QA skills must produce a substantive `*_review.md` / `*_audit.md` file on disk with ≥ 5 explicit pass items. A verbal "passed" without a file does not count.
- Final delivery requires Gate G6 approval (all three auditors PASS).
- QA checks BOTH paper quality AND workflow completeness (all 7 minimum files per subquestion).
- Flag uncertainty explicitly instead of smoothing it over.
- Do not fabricate data.
- Do not hide uncertainty.
- Do not approve final assembly with blocking issues.
- Do not edit `frozen_numbers.json` by hand. Use the **解冻 → 修改 → 重冻结** three-step.

# Team Role Responsibilities

| Role | Primary Artifacts | Review Responsibility |
|------|------------------|----------------------|
| 建模手 (Modeler) | `methods/Qx/qx_method_candidates.md`, `methods/Qx/qx_method_iteration_log.md`, `methods/Qx/qx_final_method_explanation.md` | Review paper's model description |
| 编程手 (Programmer) | `code/Qx/*`, `results/Qx/experiments/`, `results/Qx/reports/qx_final_result_analysis.md` | Review paper's result claims and figures |
| 论文手 (Writer) | `paper/sections/qx.tex`, final assembly | N/A (reviewed by modeler + programmer) |
| AI/工作流 | All intermediate reports, solution package, figure plans, robustness reports | Automated consistency checks |

# Git Discipline

- Push only intentional changes.
- Do not push raw data, scratch files, intermediate experiment outputs, or generated figures unless they are final.
- Use `.gitignore` to exclude `scratch/`, `results/Qx/experiments/` (keep only `results/Qx/reports/`).
- Resolve merge conflicts carefully — do not discard others' work.
