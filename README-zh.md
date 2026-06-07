<p align="center">
  <img src="docs/assets/logo.svg" alt="MathModeling-skills" width="640"/>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README-zh.md"><b>简体中文</b></a> ·
  <a href="./CLAUDE.md">项目规则</a> ·
  <a href="./Initial%20Prompt-zh.md">Initial Prompt</a> ·
  <a href="mailto:zjzhang0424@gmail.com">📧 联系我</a>
</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-2E9E44">
  <img alt="Skills" src="https://img.shields.io/badge/skills-28-1A6FC4">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-supported-E28E2C">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-supported-E28E2C">
</p>

---

> 我自己跑数模写的一套 skill，被同样几个低级失误坑过太多次之后写的。一共 28 个 skill，8 道门控（其中两道由你拍板），再加 3 个独立审计——审计说没问题论文才算能交。重点不是"自动化更多"，而是没有哪一步可以悄悄漏掉检查。论文里每个数字都要能追到一份冻结快照里。reviewer 必须在磁盘上留下文件。没有哪个 skill 能自己说一句"做完了"就过。
>
> 用了之后有 bug 或者想反馈跑比赛真实体验，邮件 **[zjzhang0424@gmail.com](mailto:zjzhang0424@gmail.com)**，或者直接提 issue。

## 为什么造这个

数模翻车的真正原因，基本不是"不会模型"。常见的就那几种：

- 题目其实问的是 A，队伍理解成了 B；
- 不跑 baseline 就直接上复杂模型，最后没人能解释为什么这么做；
- 论文里写了个数字，但你回过头查，没有任何一个脚本输出过这个数；
- 截止前一晚改了个 bug，论文里还是 bug 修复前的旧数字。

这些不是建模能力的问题，是流程的问题。这里面的 skill 就是按"让这几种漂移很难悄悄发生"的思路排出来的。

## 跟普通流程的差别

| | 一般的流程 | 这套 |
|---|---|---|
| 怎么往下走 | "这一步做完了，下一步" | 每个 gate 有明确通过条件，过不了，下游全部被标 stale |
| 哪个方法、为什么 | AI 选好、连理由一起写了 | AI 摆候选 + 跑可行性；**你**来拍板、用自己的话写理由。空的或复制粘贴的理由过不了门（Gate G2.5） |
| 从想法到代码 | 数学说得通就算过 | 每个候选方法必须有一段 ≤30 行的 PoC，在真实数据上跑出一个数（Gate G2） |
| 代码审查 | 有人说"看着没问题" | 写一个磁盘上的 review 文件，列 ≥ 5 条具体检查过的项，带 file:line（Gate G3） |
| 论文里的数字 | 每次从最新结果重新读 | 冻结到 `frozen_numbers.json` 里。改一个数字要先记录原因再重新冻结（Gate G4） |
| "做完了" | 一次 QA | 3 个独立审计，任何一个 fail 都不能交（Gate G6） |
| 被淘汰的方法 | 留在主目录碍事 | 自动挪到 `workspace/archived/`，免得不小心混进论文 |

## 整条流程

```text
workflow-orchestrator（session 开头 ping 环境）
 ▼  problem-parser → problem-classifier → related-paper-analyzer       [ G1: PROBLEM_PARSED ]
 ▼  symbol-table-builder + model-assumptions-builder + data-auditor-cleaner
 ▼  method-selector   ── 每候选附 ≤30 行 PoC + 可行性数字              [ G2: METHOD_VALIDATED  ★ ]
 ▼  ── 你来拍板选哪个方法 + 写为什么 ──────────────────────────────  [ G2.5: 由你拍板 👤 ]
 ▼  model-code-analyzer → {python,matlab}-model-code-generator
 ▼  code-reviewer（router）→ {python,matlab}-code-reviewer            [ G3: CODE_REVIEWED ]
 ▼  result-report-generator（[REJECTED] 自动归档）
 ▼  robustness-checker → final-method-explainer
 ▼  ── 你来判定结果好不好 + 稳不稳健 ────────────────────────────  [ G4.5: 由你判定 👤 ]
 ▼  figure-table-planner → math-figure-generator（render_check）
 ▼  solution-package-builder ── 生成 frozen_numbers.json              [ G4: RESULTS_FROZEN   ★ ]
 ▼  paper-section-writer（字数下限 + 每数值 ≥ 3 类讨论）                [ G5: PAPER_SECTION_READY ]
 ▼  paper-polisher → reference-manager
 ▼  独立审计层（三个必须全 PASS）：
       consistency-auditor · completeness-auditor · quality-assurance-auditor
                                                                       [ G6: AUDIT_LAYER_PASSED ]
 ▼  终稿组装
```

★ = 数模翻车最多的两处：G2 拦"会上说得头头是道、一到代码就跑不动"，G4 拦"半夜改了个 bug、论文里还是旧数字"。👤 = 两个属于**你**而不是 AI 的门——选方法（G2.5）和判结果（G4.5），空的或复制粘贴的答案都过不了。

## 28 个 skill，按流程的位置分

### 第 1 阶段 — 把基本盘弄齐

动模型之前先把地基打好：题目究竟问的什么、每个子问题属于哪一类题、有什么数据可用、再加一张大家共用的符号表。

- **`workflow-orchestrator`** — 跟着每个子问题走到哪一步、负责跑 gate 检查、session 开头先 ping 一下环境。
- **`problem-parser`** — 把题目拆成目标 / 对象 / 约束 / 数据 / 输出 / 子问题，写到 `planning/parse/`。
- **`problem-classifier`** — 给每个子问题打题型标签。`planning/classification/`。
- **`related-paper-analyzer`** — 找相关论文，不会编引用。
- **`symbol-table-builder`** — 全员共用的一张符号表。`planning/symbol_table.md`。
- **`model-assumptions-builder`** — 分清"必要假设"和"为了简化做的假设"。`planning/model_assumptions.md`。
- **`data-auditor-cleaner`** — 审计原始数据、出清洗副本和报告。`data_raw/` 只读。**另外它一上来会做一步"附件到子问题的归属确认表"**——这步实际比想象中重要得多。

### 第 2 阶段 — 方法验证（Gate G2 ★）

很多队伍是在截止前三天倒在这一步：会上看着特别优雅的方法，一上真实数据就跑不动，但已经来不及换了。

- **`method-selector`** — 每个子问题出 2–4 个候选。**每个候选必须配一段可跑的 ≤ 30 行 PoC，在真实清洗数据上跑出一个具体的数。** PoC 失败的候选标 `[REJECTED]`，脚本自动挪到 `workspace/archived/`。它**不替你选**——只把候选摆出来就停，由你拍板并写为什么（Gate G2.5）。产物：`methods/Qx/qx_method_candidates.md` + `methods/Qx/poc/*`。
- **`decision-prompt-builder`** — 每个判断门，AI 先问你 2-3 个「只有你能答」的 trade-off 问题，再亮出它的建议——让你是在决策，不是盖章。这里和之后每个人类门都用。
- **`modeler-decision-logger`** — 决策版的 `frozen_numbers.json`：把你拍板的决策收进一份 append-only 日志。论文里每句「为什么选 X」都要追溯到它，AI 不能偷偷替你重写理由。

### 第 3 阶段 — 写代码、然后真的审一遍（Gate G3）

写代码 → 审代码。审完得在磁盘上留一份文件，不能是聊天里说一句"没问题"。

- **`model-code-analyzer`** — 写代码之前先规划 `experiments/roundN/` 目录结构和 `run_summary.json` 的 schema。
- **`python-model-code-generator`** — `target = python` 时生成 `.py`，固定 `SEED = 2026`。
- **`matlab-model-code-generator`** — 生成 MATLAB / 北太天元能跑的 `.m`。不用 Live Script、不用 App Designer、不用比赛机器上不一定有的东西。
- **`code-reviewer`** — 看是什么语言的脚本，分发给对应 reviewer。
- **`python-code-reviewer`** — 落盘 `code/Qx/reviews/qx_python_review.md`，里面列 ≥ 5 条具体的检查项，每条带 file:line。另外会把代码里每个不等式约束列成一张小表，方便你扫一眼方向有没有写反。
- **`matlab-code-reviewer`** — 同上，写 `code/matlab/Qx/reviews/qx_matlab_review.md`。

### 第 4 阶段 — 结果、稳健性、图表、冻结（Gate G4 ★）

把原始实验输出加工成两样东西：一份论文手能直接读的材料包，外加一份"论文里所有数字"的冻结 JSON。冻结之后如果你改了 bug、某个数变了，要先记录变更再重新冻结，不许悄悄改。

- **`result-report-generator`** — 多方法对比的实验报告，再加一份最终分析。方法标 `[CHOSEN] / [BACKUP] / [REJECTED]`，淘汰的挪到 `workspace/archived/`。
- **`robustness-checker`** — 敏感性 / 误差 / baseline 对比，写 `robustness/Qx/qx_robustness_report.md`，里面 ≥ 5 条检查项。
- **`final-method-explainer`** — 最后锁定的方法的完整说明。`methods/Qx/qx_final_method_explanation.md`。
- **`figure-table-planner`** — 图分四类：1 诊断、2 对比、3 论文、4 附录。Type 1 永远不进论文。
- **`math-figure-generator`** — 出版级 matplotlib。每张图都得过 `render_check_and_log()`（不能有文字重叠、不能超出画布、字号不能 < 6.5pt），过了才能升级成 Type 3。
- **`solution-package-builder`** — 给论文手写的材料包，外加 `results/Qx/reports/frozen_numbers.json`。这个 json 不要手工编辑。

### 第 5 阶段 — 写论文、然后过审计（Gate G5 + G6）

论文手从材料包和冻结快照写论文。然后三个独立审计分别看：一个看跨文件一致性，一个看 reviewer 文件是不是都真的留下了，一个做端到端 QA。任何一个 fail，论文都不能交。

- **`paper-section-writer`** — 按材料包起草章节。每个章节有字数下限。每个数值结果至少要从 5 类里挑 3 类讨论：敏感性、物理意义、跟 baseline 比、跨题一致性、不确定性。
- **`paper-polisher`** — 时态、hedging 校准、过度宣称、文档内公式一致性。
- **`reference-manager`** — BibTeX 加引用真实性检查。虚构引用是 blocking。
- **`consistency-auditor`** — 把论文里每个数字、文件名、符号都跟 `frozen_numbers.json` / 磁盘文件 / 符号表对一遍。
- **`completeness-auditor`** — 检查每份应该存在的 `*_review.md` / `*_audit.md` 是不是都在，是不是都 ≥ 5 条通过项，是不是 stale。
- **`quality-assurance-auditor`** — 流程完整性、三条 critical rules、反造假。最终门——另外两个审计也 PASS 它才放行。

## 安装

大多数人是把仓库克隆到自己比赛项目的文件夹里用，这样 `CLAUDE.md` / `AGENTS.md` / `.claude/settings.json` 自动生效。如果你想全局装也可以。

### 方案 A — 克隆到比赛项目里（推荐）

```bash
# 在将要存 methods/ code/ results/ paper/ 的文件夹里
git clone https://github.com/zhnnky329/MathModeling-skills.git .skills-tmp
mv .skills-tmp/.claude .claude
mv .skills-tmp/.codex .codex
mv .skills-tmp/CLAUDE.md .
mv .skills-tmp/AGENTS.md .
mv .skills-tmp/docs ./skills-docs
rm -rf .skills-tmp
```

用 **Claude Code** 或 **Codex** 打开当前文件夹，28 个 skill 自动识别。第一句话：

```text
读一下 CLAUDE.md，然后调用 workflow-orchestrator。我们的题目在 workspace/problem/，按 gate 顺序走，不要跳步。
```

### 方案 B — 全局装到 Claude Code

```bash
git clone https://github.com/zhnnky329/MathModeling-skills.git
cd MathModeling-skills

mkdir -p ~/.claude/skills
for d in .claude/skills/*/; do
  cp -R "$d" ~/.claude/skills/
done
```

重启 Claude Code。任何项目里都能用到这些 skill。但 `CLAUDE.md` 和 `.claude/settings.json` 还是要放在每个比赛项目里——gate 规则和 guardrail 是写在那里的。

### 方案 C — 全局装到 Codex

```bash
git clone https://github.com/zhnnky329/MathModeling-skills.git
cd MathModeling-skills

mkdir -p ~/.codex/skills
for d in .codex/skills/*/; do
  cp -R "$d" ~/.codex/skills/
done
```

重启 Codex。把 `AGENTS.md` 放到每个比赛项目里。

### 后面更新

```bash
cd MathModeling-skills && git pull
# 如果你用的是方案 B 或 C，记得再跑一遍 cp 循环
```

### 第一句话发什么

新对话先发对应版本的 initial prompt：

- 英文：[Initial Prompt.md](Initial%20Prompt.md)
- 中文：[Initial Prompt-zh.md](Initial%20Prompt-zh.md)

### 中途接着做时常用的几句

- 回来继续：`Q2 round1 实验报告已出。让 workflow-orchestrator 判断是迭代还是锁方法。`
- 只跑稳健性：`让 robustness-checker 跑 Q1，输入在 results/Q1/reports/，baseline 在 results/Q1/experiments/round2/。不要重跑主模型。`
- 触发审计层：`所有 Qx 章节起草完毕。依次跑 consistency-auditor、completeness-auditor、quality-assurance-auditor。`

## workspace 结构

<details>
<summary>展开</summary>

```text
project/
├── planning/                   # 解析 / 分类 / 符号表 / 假设 / dashboard
├── methods/Qx/                 # 候选 + 迭代记录 + 最终方法详解 + 图表规划
│   └── poc/                    # 每候选 ≤30 行 PoC（Gate G2）
├── code/
│   ├── Qx/                     # Python 代码；reviews/qx_python_review.md（Gate G3）
│   └── matlab/Qx/              # MATLAB 代码（同构）
├── results/Qx/
│   ├── experiments/roundN/     # figures / tables / metrics / logs / run_summary.json
│   └── reports/                # 实验 + 最终分析 + 材料包 + frozen_numbers.json（Gate G4）
├── robustness/Qx/
├── paper/
│   ├── sections/               # 字数下限 + ≥3 类讨论（Gate G5）
│   ├── figures/                # Type 3 + Type 4（render_check 已过）
│   ├── audits/                 # cross_media / completeness / reference / polish（Gate G6）
│   ├── refs.bib  main.tex  qa_report.md
├── workspace/
│   ├── data_raw/               # 只读（settings.json deny）
│   ├── data_clean/
│   └── archived/<Qx>/<method>_REJECTED_roundN/
└── scratch/                    # 临时探索，不保证能复现
```

几条硬规则：`data_raw/` 只读、论文里每个数字都得出现在 `frozen_numbers.json`、`[REJECTED]` 自动归档、`frozen_numbers.json` 不许手工编辑。

</details>

## 不做什么

- 不会一键给你写完整篇论文。
- 不会编缺失的数据 / 结果 / 引用。
- 结果还没跑出来之前，不会在论文里写带数字的结论。
- 没有 baseline 和稳健性，不会写"我们的模型更好"。
- 不动你的原始数据。
- 不替你做建模决定，怎么建模还是你拿主意。

## 你可能会用到的文档

- [CLAUDE.md](CLAUDE.md) — 项目规则（gate / 审计层 / frozen 约定）。
- [AGENTS.md](AGENTS.md) — 同一套，Codex 端。
- [docs/implementation-targets.md](docs/implementation-targets.md) — `python` 还是 `matlab`。
- [docs/matlab-beita-tianyuan-guidelines.md](docs/matlab-beita-tianyuan-guidelines.md) — 怎么让 MATLAB 代码在比赛机器上能跑。
- 单个 skill：[.claude/skills/](.claude/skills/) · [.codex/skills/](.codex/skills/)。

## 联系

bug、想法，或者只是想告诉我比赛里真用过感觉怎么样——邮箱 **[zjzhang0424@gmail.com](mailto:zjzhang0424@gmail.com)**。issue 和 PR 也欢迎。

## 致谢

- **[nature-skills](https://github.com/Yuan1z0825/nature-skills)** — `math-figure-generator` 借了 `nature-figure` 的图表合约、语义配色、多面板布局思路、SVG 优先导出这些东西。作者 [Yuan1z0825](https://github.com/Yuan1z0825)，MIT。
- **[figures4papers](https://github.com/ChenLiu-1996/figures4papers)** — `nature-figure` 底下的生产级绘图脚本。

## License

MIT.
