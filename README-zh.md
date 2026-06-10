<p align="center">
  <img src="docs/assets/logo.svg" alt="MathModeling-skills" width="640"/>
</p>
<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README-zh.md"><b>简体中文</b></a> ·
  <a href="./CLAUDE.md">项目规则</a> ·
  <a href="./Initial%20Prompt-zh.md">Initial Prompt</a> ·
  <a href="mailto:zjzhang0424@gmail.com">📧 联系方式</a>
</p>


<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-2E9E44">
  <img alt="Skills" src="https://img.shields.io/badge/skills-28-1A6FC4">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-supported-E28E2C">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-supported-E28E2C">
</p>

---

> [!NOTE]
> **本次更新 — 从「自动驾驶」改回「skills辅助」。** 先前版本会把整场比赛从头跑到尾，使用者只需要点「确认」，这其实更接近全程代写：既不符合多数赛事的规则，也无助于使用者自身能力的提升。这一版把关键判断重新交还给使用者，让 skills 回到辅助的位置——在它的协助下，主导仍然是使用者本人。
>
> skill 数量从 24 增加到 28。原先的全自动版本完整保留在 [**`legacy-full-auto`**](https://github.com/zhnnky329/MathModeling-skills/tree/legacy-full-auto) 分支，需要旧版本可以直接切换过去。

> 使用过程中遇到 bug，或想反馈比赛中的真实体验，欢迎发邮件至 **[zjzhang0424@gmail.com](mailto:zjzhang0424@gmail.com)**，也欢迎直接提 issue。

## 项目初心

数模翻车的真正原因，基本不是"不会模型"，而出现在以下几类常见问题：

- 题目其实问的是 A，队伍理解成了 B；
- 不跑 baseline 就直接上复杂模型，最后没人能解释为什么这么做；
- 论文里写了个数字，但回过头查，没有任何一个脚本输出过这个数；
- 截止前一晚改了个 bug，论文里还是 bug 修复前的旧数字。

这些不是建模能力的问题，是流程的问题。这一套 skills 就是按"让这几种漂移很难悄悄发生"的思路排出来的。

## 和常见做法的区别

| | 常见做法 | 这套流程 |
|---|---|---|
| 如何推进到下一步 | 这一步做完就接着做下一步 | 每道 gate 有明确的通过条件，不通过则后续产物全部标记为 stale |
| 方法的选择 | AI 选好方法，连理由一起写了 | AI 给出候选并验证可行性，由使用者拍板、自己写理由；理由为空或照抄 AI 的内容都过不了（Gate G2.5） |
| 从想法到代码 | 数学上说得通就算可行 | 每个候选都要有一段不超过 30 行的 PoC，在真实数据上跑出结果（Gate G2） |
| 代码审查 | 一句"看着没问题"带过 | 落盘一份 review 文件，列出至少 5 条具体检查项并标注 file:line（Gate G3） |
| 论文中的数字 | 每次都从最新结果重新读 | 冻结到 `frozen_numbers.json`；要改某个数字，须先记录原因再重新冻结（Gate G4） |
| 何时算"完成" | 过一遍 QA 即可 | 三个独立审计，任何一个不通过都不能提交（Gate G6） |
| 被淘汰的方法 | 留在主目录里 | 自动移入 `workspace/archived/`，避免误用进论文 |

## 整条流程

```text
workflow-orchestrator（session 开头 ping 环境）
 ▼  problem-parser → problem-classifier → related-paper-analyzer       [ G1: PROBLEM_PARSED ]
 ▼  symbol-table-builder + model-assumptions-builder + data-auditor-cleaner
 ▼  method-selector   ── 每候选附 ≤30 行 PoC + 可行性数字              [ G2: METHOD_VALIDATED  ★ ]
 ▼  ── 使用者来拍板选哪个方法 + 写为什么 ──────────────────────────────  [ G2.5: 拍板 👤 ]
 ▼  model-code-analyzer → {python,matlab}-model-code-generator
 ▼  code-reviewer（router）→ {python,matlab}-code-reviewer            [ G3: CODE_REVIEWED ]
 ▼  result-report-generator（[REJECTED] 自动归档）
 ▼  robustness-checker → final-method-explainer
 ▼  ── 使用者来判定结果好不好 + 稳不稳健 ────────────────────────────  [ G4.5: 判定 👤 ]
 ▼  figure-table-planner → math-figure-generator（render_check）
 ▼  solution-package-builder ── 生成 frozen_numbers.json              [ G4: RESULTS_FROZEN   ★ ]
 ▼  paper-section-writer（字数下限 + 每数值 ≥ 3 类讨论）                [ G5: PAPER_SECTION_READY ]
 ▼  paper-polisher → reference-manager
 ▼  独立审计层（三个必须全 PASS）：
       consistency-auditor · completeness-auditor · quality-assurance-auditor
                                                                       [ G6: AUDIT_LAYER_PASSED ]
 ▼  终稿组装
```

★ 标的两处是最容易出问题的环节：G2 防止一个看上去漂亮、实际跑不通的方法进入编码阶段；G4 防止改完 bug 之后论文里还留着旧数字。👤 标的两个门（G2.5 选方法、G4.5 判结果）由使用者拍板，AI 只给建议，空着或直接照抄 AI 的答案都过不了。

## 28 个 skill，按所在阶段划分

### 第 1 阶段 · 前期准备

正式建模之前，先把基础信息整理清楚：题目到底在问什么、每个子问题属于哪一类、有哪些数据可用，以及一张全队统一的符号表。

- **`workflow-orchestrator`** — 跟踪每个子问题进行到哪一步，执行各道 gate 的检查，并在 session 开始时确认运行环境。
- **`problem-parser`** — 把题目拆成目标 / 对象 / 约束 / 数据 / 输出 / 子问题，写入 `planning/parse/`。
- **`problem-classifier`** — 为每个子问题标注题型，写入 `planning/classification/`。
- **`related-paper-analyzer`** — 检索相关文献，不会凭空编造引用。
- **`symbol-table-builder`** — 维护一张全队共用的符号表，`planning/symbol_table.md`。
- **`model-assumptions-builder`** — 区分"必要假设"与"为简化而设的假设"，`planning/model_assumptions.md`。
- **`data-auditor-cleaner`** — 审计原始数据，生成清洗后的副本和数据报告，原始数据 `data_raw/` 保持只读。它在开始前会先确认"哪个附件对应哪个子问题"，避免把数据用错地方。

### 第 2 阶段 · 方法验证（Gate G2 ★）

不少队伍是在截止前才发现：当初看好的方法，放到真实数据上根本跑不动，此时已经来不及更换。这道关就是为了提前暴露这类问题。

- **`method-selector`** — 为每个子问题给出 2–4 个候选方法，每个候选都要配一段不超过 30 行、能在真实清洗数据上跑出具体结果的 PoC。PoC 不通过的候选标记 `[REJECTED]`，脚本移入 `workspace/archived/`。它不替使用者做选择，只把候选和可行性结果摆出来；最终选哪个、为什么选，由使用者在 Gate G2.5 写明。产物：`methods/Qx/qx_method_candidates.md` 与 `methods/Qx/poc/*`。
- **`decision-prompt-builder`** — 在每个判断节点，先向使用者提出 2-3 个只有人能回答的取舍问题，再给出 AI 的建议，确保是使用者在做决定。后续每个由人拍板的门都会用到。
- **`modeler-decision-logger`** — 决策层面的 `frozen_numbers.json`：把使用者拍板的决策记入一份只追加的日志。论文里每一句"为什么选某方法"都要能追溯到它，AI 不能擅自替使用者重写理由。

### 第 3 阶段 · 编码与代码审查（Gate G3）

先写代码，再做审查；审查结果要落成磁盘上的文件，而不是对话里一句"没问题"。

- **`model-code-analyzer`** — 在写代码前先规划 `experiments/roundN/` 的目录结构和 `run_summary.json` 的字段。
- **`python-model-code-generator`** — 实现目标为 `python` 时生成 `.py`，统一使用 `SEED = 2026`。
- **`matlab-model-code-generator`** — 生成 MATLAB / 北太天元可运行的 `.m`，避开 Live Script、App Designer 等比赛环境未必支持的特性。
- **`code-reviewer`** — 判断脚本语言，分发给对应的 reviewer。
- **`python-code-reviewer`** — 落盘 `code/Qx/reviews/qx_python_review.md`，列出至少 5 条具体检查项并标注 file:line，同时把每个不等式约束列成一张表，方便核对方向是否写反。
- **`matlab-code-reviewer`** — 同上，落盘 `code/matlab/Qx/reviews/qx_matlab_review.md`。

### 第 4 阶段 · 结果、稳健性、图表与冻结（Gate G4 ★）

把原始实验输出整理成两部分：一份供论文手直接使用的材料包，以及一份记录"论文中所有数字"的冻结 JSON。冻结之后若因改 bug 等原因导致数值变化，须先记录变更、再重新冻结，不允许直接改动。

- **`result-report-generator`** — 生成多方法对比的实验报告和最终分析，方法标注 `[CHOSEN] / [BACKUP] / [REJECTED]`，淘汰的移入 `workspace/archived/`。
- **`robustness-checker`** — 做敏感性、误差、与 baseline 的对比，落盘 `robustness/Qx/qx_robustness_report.md`，含至少 5 条检查项。
- **`final-method-explainer`** — 撰写最终选定方法的完整说明，`methods/Qx/qx_final_method_explanation.md`。
- **`figure-table-planner`** — 将图分为四类：1 诊断、2 对比、3 论文、4 附录，其中诊断图不会进入论文。
- **`math-figure-generator`** — 用 matplotlib 出图，每张图都要通过 `render_check_and_log()`（检查文字重叠、超出画布、字号小于 6.5pt 等），通过后才能定为论文图。
- **`solution-package-builder`** — 生成供论文手使用的材料包，以及 `results/Qx/reports/frozen_numbers.json`，该文件不应手工编辑。

### 第 5 阶段 · 论文写作与审计（Gate G5 + G6）

论文手依据材料包和冻结快照撰写论文，随后由三个独立审计分别检查：跨文件一致性、各 reviewer 文件是否齐备、以及整体 QA。任何一个不通过，论文都不能提交。

- **`paper-section-writer`** — 依据材料包起草各章节，每章设有字数下限；每个数值结果至少要从敏感性、物理意义、与 baseline 对比、跨子问题一致性、不确定性这五类中选三类展开讨论。
- **`paper-polisher`** — 检查时态、措辞强弱、过度宣称、以及文档内公式的一致性。
- **`reference-manager`** — 生成 BibTeX 并核查引用真实性，虚构引用会被判为 blocking。
- **`consistency-auditor`** — 将论文里每个数字、文件名、符号与 `frozen_numbers.json`、磁盘文件、符号表逐一比对。
- **`completeness-auditor`** — 检查每份应有的 `*_review.md` / `*_audit.md` 是否齐备、是否满足至少 5 条通过项、是否过期。
- **`quality-assurance-auditor`** — 核查流程完整性、三条核心规则与反造假。作为最终一关，只有另外两个审计都通过时它才放行。

## 安装

推荐把仓库克隆到比赛项目所在的文件夹里使用，这样 `CLAUDE.md` / `AGENTS.md` / `.claude/settings.json` 会自动生效。也可以选择全局安装。

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

用 **Claude Code** 或 **Codex** 打开该文件夹，28 个 skill 会被自动识别。开场可以这样说：

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

重启 Claude Code 后，这些 skill 在任何项目中都可用。但 `CLAUDE.md` 和 `.claude/settings.json` 仍需放在各比赛项目内，gate 规则和约束都写在其中。

### 方案 C — 全局装到 Codex

```bash
git clone https://github.com/zhnnky329/MathModeling-skills.git
cd MathModeling-skills

mkdir -p ~/.codex/skills
for d in .codex/skills/*/; do
  cp -R "$d" ~/.codex/skills/
done
```

重启 Codex 后，把 `AGENTS.md` 放入各比赛项目即可。

### 后续更新

```bash
cd MathModeling-skills && git pull
# 若采用方案 B 或 C，记得再执行一次 cp 循环
```

### 开场指令

新对话开始时，先发送对应语言的 initial prompt：

- 英文：[Initial Prompt.md](Initial%20Prompt.md)
- 中文：[Initial Prompt-zh.md](Initial%20Prompt-zh.md)

### 常用的后续指令

- 继续推进：`Q2 round1 实验报告已出。让 workflow-orchestrator 判断是迭代还是锁方法。`
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

几条硬性约定：`data_raw/` 只读；论文中每个数字都须出现在 `frozen_numbers.json`；`[REJECTED]` 方法自动归档；`frozen_numbers.json` 不允许手工编辑。

</details>

## 不做什么

- 不会一键生成整篇论文。
- 不会编造缺失的数据、结果或引用。
- 在结果跑出来之前，不会在论文中写入带数字的结论。
- 在缺少 baseline 和稳健性分析时，不会下"我们的模型更好"这类结论。
- 不改动原始数据。
- 不替使用者做建模决策，方法仍由使用者决定。

## 相关文档

- [CLAUDE.md](CLAUDE.md) — 项目规则（gate / 审计层 / frozen 约定）。
- [AGENTS.md](AGENTS.md) — 同一套规则的 Codex 版本。
- [docs/implementation-targets.md](docs/implementation-targets.md) — 选 `python` 还是 `matlab`。
- [docs/matlab-beita-tianyuan-guidelines.md](docs/matlab-beita-tianyuan-guidelines.md) — 如何让 MATLAB 代码在比赛环境中正常运行。
- 单个 skill：[.claude/skills/](.claude/skills/) · [.codex/skills/](.codex/skills/)。

## 联系方式

如有 bug、建议，或想分享比赛中的使用体验，欢迎邮件 **[zjzhang0424@gmail.com](mailto:zjzhang0424@gmail.com)**，也欢迎提 issue 或 PR。

## 致谢

- **[nature-skills](https://github.com/Yuan1z0825/nature-skills)** — `math-figure-generator` 借鉴了 `nature-figure` 的图表合约、语义配色、多面板布局思路与 SVG 优先导出。作者 [Yuan1z0825](https://github.com/Yuan1z0825)，MIT。
- **[figures4papers](https://github.com/ChenLiu-1996/figures4papers)** — `nature-figure` 所基于的生产级绘图脚本。

## License

MIT.
