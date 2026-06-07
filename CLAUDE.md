# Core Philosophy

- **The AI owns mechanical correctness; the human owns modeling judgment.** This is an assistant for the engineering discipline around a contest, not a solver and not a paper-writer. The AI keeps numbers traceable, runs PoCs, audits consistency, render-checks figures, enforces gates — the bookkeeping a machine should do. The human chooses the method and says why, decides what a number means, judges whether a result is good, frames the assumptions, and authorizes submission — the judgment a contest grades and a student must learn. A skill must never originate, on the human's behalf, a judgment a judge would grade.
- Start from goals, objects, constraints, data, outputs, variables, relationships, and checkable conclusions.
- Do not start from model names.
- Separate assumptions from validated conclusions at every stage.

# Workflow Discipline

- Follow the full workflow in order instead of skipping ahead.
- Keep file edits minimal and traceable.
- Do not overwrite validated artifacts casually.
- Only generate code from a validated method plan.
- **Change-propagation rule (P1)**: After modifying any file under `code/Qx/`, `methods/Qx/`, `results/Qx/reports/`, or `planning/`, grep the entire workspace for references to the changed artifact (symbol name, parameter name, file path, numerical value), list every file that now may be stale, and either update it in the same turn or flag it as STALE with recommended repair. Do not let the next turn discover the inconsistency. Specifically:
  1. `grep -rn '<changed_identifier>' methods/ code/ results/ paper/ planning/` before claiming the change is "done".
  2. If the changed file is under `code/Qx/` and `frozen_numbers.json` exists for that Qx, mark the freeze as stale in `results/Qx/reports/freeze_change_log.md` and recommend re-freezing.
  3. If the changed file is under `methods/Qx/` and `paper/sections/qx.tex` exists, flag that section as potentially stale.
  4. After any multi-file change, run `consistency-auditor` for the affected Qx as an incremental check — do not defer to the final G6 run.

# Workflow Gates (G1 – G6)

Gates are not stages. A stage is "where I am"; a gate is "what I must satisfy to leave". The orchestrator evaluates each gate against an explicit `enter_condition / pass_criteria / fail_fallback` contract. See [workflow-orchestrator](.claude/skills/workflow-orchestrator/SKILL.md) for the full contract.

- **G1 PROBLEM_PARSED**: parse + classification exist.
- **G2 METHOD_VALIDATED** (load-bearing — method→code boundary): each candidate has a ≤30-line PoC + feasibility number. No PoC ⇒ not validated.
- **G2.5 METHOD_CHOSEN_BY_HUMAN** (human-decision gate, pilot): `methods/Qx/decisions/method-selector_modeler_decision.md` is `DECIDED` by the human with a non-empty, non-copied, evidence-citing rationale. The AI suggests; the human chooses. `code_generation_allowed_Qx = G2 ∧ G2.5`.
- **G3 CODE_REVIEWED**: reviewer artifact exists at `code/Qx/reviews/qx_<lang>_review.md` with ≥ 5 explicit pass items.
- **G4.5 RESULTS_JUDGED_BY_HUMAN** (human-decision gate): before the freeze, the human renders the result verdict (`result-report-generator` → `qx_result_verdict`: per-method CHOSEN/BACKUP/REJECTED + round decision + confidence citing a number) and the stability verdict (`robustness-checker` → `qx_stability_verdict`, citing a number). `[REJECTED]` archival fires only off a human tag. `freeze_allowed_Qx = G3 ∧ G4.5`.
- **G4 RESULTS_FROZEN** (load-bearing — results→paper boundary): requires G4.5 passed + package sign-off (`solution-package-builder` → `qx_package_signoff`: keep/downgrade/drop per flagged claim). `frozen_numbers.json` exists, is newer than every source file, and every "why we chose X" sentence traces to a `decision_id` in the decision log.
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
  3. **重冻结** — re-invoke `solution-package-builder` to regenerate `frozen_numbers.json` with a new `frozen_at` timestamp.
- Never edit `frozen_numbers.json` by hand. Never edit it without the change log entry.
- `consistency-auditor` checks freeze staleness: if any `code/Qx/*` file's mtime is newer than `frozen_at`, the snapshot is STALE and the paper claim is suspect.

# Human Decision Artifact Convention

> Parallel to the Frozen Numbers Convention: just as numbers are frozen so a bug fix can't silently shift the paper, modeling *judgments* are pinned to a human-authored artifact so the AI can't silently author what a judge grades. The schema's char floors are still being calibrated against real usage — tune them, don't treat them as final.

The five C-layer (judgment-bearing) skills — `method-selector` (G2.5), `result-report-generator` / `robustness-checker` / `final-method-explainer` (G4.5), `solution-package-builder` (G4 sign-off) — must NOT originate the graded verdict (which method, why, `[CHOSEN]`/`[REJECTED]`, confidence, what a number means). Each lays out evidence + an AI suggestion, then STOPS and requires a human decision artifact before its gate passes. The seven B-layer (drafts-for-review) skills draft prose but mark every judgment-bearing span with a sentinel (`[AI-DRAFT — modeler must confirm: …]` or `[MODELER INPUT NEEDED: …]`) the human must replace; a surviving sentinel blocks the gate exactly like `<<<HUMAN>>>`.

**Path:** `methods/Qx/decisions/<skill>_modeler_decision.md` (global-scope skills use `planning/decisions/`).

**Format:** machine-readable front-matter (the orchestrator / `completeness-auditor` parse this) + a human-authored prose body.

```markdown
---
schema_version: 1
skill: method-selector
scope: Q2
decision_id: q2_method_choice      # stable id; referenced by frozen_numbers.json / audits
status: DECIDED                    # PENDING => gate FAILS
decided_by: human                  # "ai" / "auto" => gate FAILS
decided_at: 2026-06-06T14:20:00+08:00
ai_suggestion: "M2 entropy-TOPSIS — highest PoC feasibility"   # AI's pick, kept in its OWN field
choice: "M2"
rejected_alternatives:
  - { id: "M1", reason: "<<<HUMAN>>>" }
  - { id: "M3", reason: "<<<HUMAN>>>" }
confidence: medium
evidence_refs:
  - "methods/Q2/poc/m2_poc_result.txt"     # must resolve to a real file on disk
---

## Modeler's rationale  <!-- human-authored; the AI must NOT write this -->
<<<HUMAN: in your own words, why this method over the rejected ones, tied to a specific
number or criterion from the evidence.>>>
```

**What is enforced (and honest limits):**
- **FAIL by default.** Passes only if `status: DECIDED` AND `decided_by: human` AND every mandatory field is present, over its floor, and contains no sentinel (`<<<`, `TODO`, `TBD`, `待补充`, `...`, empty).
- **Anti-copy = near-verbatim only.** The human rationale must not be a near-exact copy of `ai_suggestion` (normalized-whitespace equality / tiny edit distance). Fuzzy similarity (Jaccard/trigram) is NOT a hard gate — Chinese technical paraphrase reuses terms legitimately; fuzzy scores go to a provenance ledger as a WARN signal, to be calibrated against real samples later. Formulas and symbols from `symbol_table.md` are exempt from copy-checking.
- **Evidence citation is the strong lever.** The rationale must reference a concrete token from the evidence (a number, a candidate id, a symbol). This is what actually forces engagement — a char floor only forces length. Keep the char floor low (enough for one sentence with a number) and lean on the evidence-citation requirement.
- **Cannot prove human authorship.** A determined user can paraphrase AI text. The gate makes rubber-stamping a dead end and leaves a visible engagement trail; it does not claim authorship proof.

**Recovery after a FAIL:** edit the artifact → `status` flips to DECIDED, `decided_at` refreshes → next orchestrator run re-checks the file (stateless) → on pass, the gate's human sub-flag flips true. Downstream DIRTY artifacts are NOT auto-trusted: `consistency-auditor` must re-run incrementally for that Qx (the Change-propagation rule P1) before DIRTY clears. If the edited decision sat behind a frozen number, walk `解冻 → 修改 → 重冻结`; the decision record appends a new entry with `supersedes`, never overwrites.

# AI-Use Disclosure Convention

Contests permit AI **assistance** and forbid AI **doing the modeling for the team**. The pipeline already knows exactly which skill touched which artifact and which fields were AI-drafted vs human-authored — so it can produce a more honest disclosure than a human writing one from memory.

- The pipeline emits `paper/ai_use_disclosure.md` enumerating, per artifact, what was AI-drafted vs human-authored, derived from the decision artifacts and the surviving/replaced sentinels.
- **The disclosure must tell the truth about rubber-stamping.** If a human-owned field was never edited from the AI's `ai_suggestion` (near-verbatim), the disclosure records `AI-drafted, accepted without modification` — NOT `human-authored`. A clean "I wrote this" attestation must be earned, so faking engagement gains nothing.
- Granularity follows a `contest_profile` (`COMAP` | `CUMCM` | `OTHER`): COMAP gets the full AI-use report formatted to the contest's spec; CUMCM/strict gets an internal warning ("this contest may not permit AI assistance — verify; this disclosure is for your records / integrity pledge, not necessarily for submission") rather than auto-inserting an appendix into a paper for a contest with no disclosure channel.
- **No contest's AI policy is encoded here as authoritative.** AI rules change every cycle and differ sharply (COMAP disclose-and-allow vs CUMCM originality-first). Defaults target the strictest plausible interpretation so a workflow compliant under the loosest contest is also compliant under the strictest. The team must read their contest's current-year official rules; the final compliance call is the human's.

# Rejected-Method Archival Convention

Failed or eliminated candidate methods do not stay in the main code tree. Once `result-report-generator` or `method-selector` marks a method as `[REJECTED]`:

- Move its PoC script, code, and any output figures to `workspace/archived/<Qx>/<method_name>_REJECTED_roundN/`.
- Keep a one-line breadcrumb in `methods/Qx/qx_method_iteration_log.md` explaining why it was rejected.
- Do NOT keep `[REJECTED]` methods in `code/Qx/` or `results/Qx/experiments/`. The main tree should contain only `[CHOSEN]` (final selected) and `[BACKUP]` (still under consideration).
- This keeps the main tree audit-clean and prevents `[REJECTED]` outputs from drifting into the paper by accident.

# Three Critical Rules

Rule 1 — 没有最终方法详解，不准写最终论文:
  `paper-section-writer` must not write final paper sections for Qx unless
  `methods/Qx/qx_final_method_explanation.md` exists.

Rule 2 — 没有最终结果分析，不准交给论文手:
  Raw experiment outputs are not a deliverable. `results/Qx/reports/qx_final_result_analysis.md`
  must exist before the writer can proceed for Qx.

Rule 3 — 论文手只看材料包，不从零散 results 里猜:
  The writer's primary source for Qx is `results/Qx/reports/qx_solution_package_for_writer.md`.
  If this file is missing, Qx is NOT Ready for Writer.

# Per-Question Delivery Chain

For each subquestion Qx, it is forbidden to treat "code ran successfully" as "the subquestion is done."

Every subquestion must go through:
```
1. method-selector        → methods/Qx/qx_method_candidates.md  +  PoC scripts under methods/Qx/poc/
                            (each candidate has a ≤30-line PoC + feasibility number — Gate G2)
2. model-code-analyzer    → code/model-code-analyzer.md (with experiments/roundN/ plan)
3. code generators        → code/Qx/*.py (or code/matlab/Qx/*.m)
4. <lang>-code-reviewer   → code/Qx/reviews/qx_<lang>_review.md  (≥ 5 explicit pass items — Gate G3)
5. result-report-generator → results/Qx/experiments/roundN/qx_experiment_report_roundN.md
                             (failed candidates marked [REJECTED], moved to workspace/archived/)
6. [loop 3-5 until method converges]
7. final-method-explainer → methods/Qx/qx_final_method_explanation.md
8. result-report-generator → results/Qx/reports/qx_final_result_analysis.md
9. robustness-checker      → robustness/Qx/qx_robustness_report.md  (≥ 5 explicit pass items)
10. figure-table-planner    → methods/Qx/qx_figure_table_plan.md
11. math-figure-generator   → paper/figures/qx_*.svg  (each figure passes render-check)
12. solution-package-builder → results/Qx/reports/qx_solution_package_for_writer.md
                              + results/Qx/reports/frozen_numbers.json  (Gate G4 freeze)
13. paper-section-writer   → paper/sections/qx.tex (or .md)
                              (word-count floor + ≥ 3 discussion dimensions per number — Gate G5)
14. modeler review + programmer review
```

Then the independent audit layer runs (Gate G6) — see "Independent Audit Layer" above.

Minimum 7 files per subquestion before "Ready for Writer":
- methods/Qx/qx_method_candidates.md (with PoC scripts under methods/Qx/poc/)
- methods/Qx/qx_method_iteration_log.md
- methods/Qx/qx_final_method_explanation.md
- code/Qx/reviews/qx_<lang>_review.md (≥ 5 pass items)
- results/Qx/reports/qx_final_result_analysis.md
- results/Qx/reports/qx_solution_package_for_writer.md
- results/Qx/reports/frozen_numbers.json (immutable freeze)

# Full Skill List (27 skills)

| Skill | Role |
|-------|------|
| workflow-orchestrator | 总调度：跟踪每小问状态，按 G1–G6 gate 决定下一步 |
| problem-parser | 题目解析：拆成目标/对象/约束/数据/输出/子问题 |
| problem-classifier | 题型分类：评价/预测/优化/机理/分类/图/仿真/混合 |
| related-paper-analyzer | 论文分析：从真实文献提炼方法，不编造引用 |
| method-selector | 候选方法池：每小问 2-4 个候选 + 每个候选附 ≤30 行 PoC + 可行性数字；只发 `[CANDIDATE]` 不发 `[CHOSEN]`，方法选择交人(G2.5) |
| **modeler-decision-logger** | **决策版 frozen_numbers：收集/盖戳/冻结人写决策成单一 append-only 日志；论文叙述从它转述，赛后当复盘日记。不产决策。** |
| symbol-table-builder | 全局符号表构建：统一所有小问的符号约定 |
| model-assumptions-builder | 全局模型假设：区分必要/简化，评估影响 |
| data-auditor-cleaner | 数据审计清洗：副本操作，不碰原始数据 |
| model-code-analyzer | 代码规划：定义 experiments/roundN/ 结构 + run_summary.json |
| python-model-code-generator | Python 代码生成 |
| matlab-model-code-generator | MATLAB / 北太天元 代码生成 |
| code-reviewer | 代码路由：检测语言并交给对应 reviewer |
| python-code-reviewer | Python 代码审查，强制落盘 `code/Qx/reviews/qx_python_review.md` ≥ 5 通过项 |
| matlab-code-reviewer | MATLAB / 北太天元 代码审查，强制落盘 `code/matlab/Qx/reviews/qx_matlab_review.md` ≥ 5 通过项 |
| result-report-generator | 实验报告 + 最终结果分析 + 失败方案 [REJECTED] 归档 |
| robustness-checker | 稳健性/敏感性/baseline 对比 |
| final-method-explainer | 最终方法详解：假设/符号/目标/约束/求解/评价 |
| figure-table-planner | 图表规划：诊断图/对比图/论文图/附录图四类 |
| math-figure-generator | 图表生成：出版级 matplotlib + 强制 render-check（bbox/出界/字号） |
| solution-package-builder | 论文材料包 + 生成 `frozen_numbers.json` 冻结快照 |
| paper-section-writer | 论文写作：字数下限 + 每数值结果 ≥ 3 类讨论 gate |
| paper-polisher | 论文润色：句法/时态/hedging/过度宣称/公式一致性 |
| reference-manager | 参考文献管理：BibTeX 生成 + 虚构引用检测 |
| **consistency-auditor** | **【独立审计层 1/3】跨媒介数字/文件/符号/参数一致性比对** |
| **completeness-auditor** | **【独立审计层 2/3】所有应落盘 audit/review 文件必须存在且 ≥ 5 通过项** |
| quality-assurance-auditor | 【独立审计层 3/3】流程完整性 + 三条规则 + 反造假 |

# Workspace Convention (updated)

```
project/
├── planning/                   # 全局规划
│   ├── parse/                  # 题目解析
│   ├── classification/         # 题型分类
│   ├── symbol_table.md         # 统一符号表
│   ├── model_assumptions.md    # 全局模型假设
│   ├── question_dependency.md  # 小问依赖关系
│   └── progress_dashboard.md   # 进度看板
├── methods/                    # 建模手区
│   └── Qx/                     # 候选方法/迭代记录/最终方法详解/图表规划
├── code/                       # 编程手区
│   ├── model-code-analyzer.md  # 代码规划文档
│   ├── Qx/                     # Python 代码 (code/Qx/*.py)
│   └── matlab/Qx/              # MATLAB 代码 (code/matlab/Qx/*.m)
├── results/                    # 正式结果区
│   └── Qx/
│       ├── experiments/roundN/  # 实验输出 (figures/tables/metrics/logs/run_summary.json)
│       └── reports/             # 实验报告/最终结果分析/论文材料包
├── robustness/                 # 稳健性分析区
│   └── Qx/                     # 稳健性报告 + 图表
├── paper/                      # 论文手区
│   ├── sections/               # 各章节草稿
│   ├── figures/                # 最终论文图表 (Type 3 + Type 4)
│   ├── audits/                 # 独立审计层产物 (consistency / completeness)
│   │   ├── cross_media_consistency_audit.md
│   │   ├── completeness_audit.md
│   │   ├── reference_audit.md
│   │   └── polish_report.md
│   ├── refs.bib                # 参考文献
│   ├── main.tex                # 主文件
│   └── qa_report.md            # QA 报告 (独立审计层 3/3)
├── docs/                       # 长期资料库
│   ├── references/             # 方法参考资料
│   ├── past_papers/            # 优秀论文案例
│   └── templates/              # 论文/报告模板
├── workspace/data_raw/         # 原始数据（只读，不修改）
├── workspace/data_clean/       # 清洗后的数据
├── workspace/archived/         # [REJECTED] 方案归档区（主代码树永远干净）
│   └── <Qx>/<method>_REJECTED_roundN/
└── scratch/                    # 临时探索区（不保证可复现）
```

# Workspace Artifact Contract

- Raw data must remain untouched under `workspace/data_raw/`.
- Cleaned data goes under `workspace/data_clean/`.
- Generated code goes under `code/Qx/` (Python) or `code/matlab/Qx/` (MATLAB).
- Experiment outputs go under `results/Qx/experiments/roundN/` with subdirs: `figures/`, `tables/`, `metrics/`, `logs/`, `run_summary.json`.
- Analysis reports go under `results/Qx/reports/`.
- Robustness artifacts go under `robustness/Qx/`.
- Final paper figures go under `paper/figures/`.
- Paper section drafts go under `paper/sections/`.
- Final assembled materials go under `paper/`.

# Figure Type Classification

All figures must be classified into one of four types:
- Type 1 诊断图: For modeler only — internal debugging. NOT for paper.
- Type 2 对比图: Method comparison — MAY appear in paper.
- Type 3 论文图: Final results — MUST appear in paper. Publication-quality required.
- Type 4 附录图: Supplementary — referenced from main text, shown in appendix.

# Modeling Rules

- Parse first, classify second, select methods third.
- Generate 2-4 candidate methods per subquestion — do not commit to the first idea.
- Match method choice to problem type, data, and contest limits.
- Every main model must have a baseline.
- Do not choose complex models only because they look advanced.
- Do not invent missing data, results, or references.
- Final method selection happens AFTER experiments, by the modeler reviewing experiment reports.
- Create global symbol table early — same symbol for same concept across all subquestions.

# Coding Rules

- Make surgical edits.
- Preserve existing style.
- Make the smallest necessary change when reading or editing files.
- Keep code readable and easy to audit.
- Code must output to `results/Qx/experiments/roundN/` structure.
- Always generate `run_summary.json` after execution.
- Save all outputs to files (CSV, JSON, PNG) — do not rely on console output only.
- Use fixed random seeds for reproducibility (SEED = 2026).
- Do not overwrite validated artifacts unless explicitly repairing them.
- When modifying generated code, explain what changed and how to verify it.

# Paper Writing Rules

- Write only from available problem analysis, method plans, results, figures, and robustness checks.
- The solution package (`qx_solution_package_for_writer.md`) is the primary source per subquestion.
- Keep claims proportional to evidence.
- Do not write numerical claims before results exist.
- Avoid filler prose and unsupported conclusions.
- Method description must match the final method explanation, not an early candidate pool.
- Results must come from the final result analysis, not raw experiment outputs.
- Mention eliminated methods to demonstrate thoroughness.
- Polish before final QA (use paper-polisher).

# Verification and QA

- Re-check assumptions, outputs, and narrative consistency before handoff.
- Robustness or sensitivity checks are required before final delivery.
- The three independent auditors (consistency / completeness / QA) are orthogonal — all must PASS before final assembly. A single auditor's "✅" is NOT sufficient.
- Every major claim must have at least one supporting robustness check or a stated limitation.
- Reviewer / auditor / QA skills must produce a substantive `*_review.md` / `*_audit.md` file on disk with ≥ 5 explicit pass items. A verbal "passed" without a file does not count.
- Final delivery requires Gate G6 approval (all three auditors PASS).
- Mark blocking issues clearly.
- Return control to the workflow instead of improvising around unresolved problems.
- Do not fabricate data, references, results, figures, or experiments.
- Do not hide uncertainty.
- Do not edit `frozen_numbers.json` by hand. Use the **解冻 → 修改 → 重冻结** three-step.
