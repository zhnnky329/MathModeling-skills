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
| 方法的选择 | AI 选好方法，连理由一起写了 | 使用者先选择取向；AI 筛选主方法、可信 baseline 和最多一个条件性备用；再由使用者拍板（Gate G2.5） |
| 从想法到代码 | 数学上说得通就算可行 | 风险探针检查数据覆盖、关键假设、输出集中/退化、扰动敏感性和规模（Gate G2） |
| 代码审查 | 一句"看着没问题"带过 | JSON review 必须通过语法、输入契约、方法对齐、可复现性、输出契约五项命名检查（Gate G3） |
| 论文中的数字 | 每次都从最新结果重新读 | 冻结到 `frozen_numbers.json`；要改某个数字，须先记录原因再重新冻结（Gate G4） |
| 探索成本 | 每一步都写完整报告和审计 | `lean` 只保留 manifest、决策、探针和运行摘要；`submission` 才增加冻结、论文和三项终审 |
| 何时算"完成" | 过一遍 QA 即可 | 三个独立终审，任何一个不通过都不能提交（Gate G6） |
| 被淘汰的方法 | 留在主目录里 | 自动移入 `workspace/archived/`，避免误用进论文 |

## 整条流程

```text
workflow-orchestrator（读取 interaction_mode + rigor_profile）
 ▼  problem-parser → problem-classifier → related-paper-analyzer       [ G1: PROBLEM_FRAMED ]
 ▼  symbol-table-builder + model-assumptions-builder + data-auditor-cleaner
 ▼  使用者先选取向/风险/预算 → method-selector
       主方法 + 可信 baseline + 可触发备用
       风险探针（包含输出集中度）                                      [ G2: METHOD_SCREENED  ★ ]
 ▼  ── 使用者来拍板选哪个方法 + 写为什么 ──────────────────────────────  [ G2.5: 拍板 👤 ]
 ▼  model-code-analyzer → {python,matlab}-model-code-generator
 ▼  code-reviewer（router）→ 命名检查 JSON review                    [ G3: CODE_AND_EXPERIMENT_REVIEWED ]
 ▼  result-report-generator（只在决策点/最终轮写报告）
 ▼  robustness-checker → final-method-explainer
 ▼  ── 使用者选择继续 / 调整 / 启用备用 ──────────────────────────────  [ G4: 判定 👤 ]
 ▼  figure-table-planner → math-figure-generator（render_check）
 ▼  rigor_profile 切换为 submission
 ▼  solution-package-builder ── 生成 frozen_numbers.json              [ G4: RESULTS_FROZEN   ★ ]
 ▼  paper-section-writer                                               [ G5: PAPER_SECTION_READY ]
 ▼  paper-polisher → reference-manager
 ▼  独立审计层（三个必须全 PASS）：
       consistency-auditor · completeness-auditor · quality-assurance-auditor
                                                                       [ G6: AUDIT_LAYER_PASSED ]
 ▼  终稿组装
```

★ 标的是两个承重边界：G2 在完整实现前发现假设、集中度、可行性和规模问题；G4 防止旧数字进入论文。👤 标的是由使用者负责的判断。

## 28 个 skill，按所在阶段划分

### 第 1 阶段 · 前期准备

正式建模之前，先把基础信息整理清楚：题目到底在问什么、每个子问题属于哪一类、有哪些数据可用，以及一张全队统一的符号表。

- **`workflow-orchestrator`** — 跟踪每个子问题进行到哪一步，执行各道 gate 的检查，并在 session 开始时确认运行环境。
- **`problem-parser`** — 把题目拆成目标 / 对象 / 约束 / 数据 / 输出 / 子问题，写入 `planning/parse/`。
- **`problem-classifier`** — 为每个子问题标注题型，写入 `planning/classification/`。
- **`related-paper-analyzer`** — 检索相关文献，不会凭空编造引用。
- **`symbol-table-builder`** — 维护一张全队共用的符号表，`planning/symbol_table.md`。
- **`model-assumptions-builder`** — 区分"必要假设"与"为简化而设的假设"，`planning/model_assumptions.md`。
- **`data-auditor-cleaner`** — 审计原始数据，生成清洗后的副本和紧凑数据画像，原始数据 `data_raw/` 保持只读。它在开始前会先确认"哪个附件对应哪个子问题"，避免把数据用错地方。

### 第 2 阶段 · 方法验证（Gate G2 ★）

不少队伍是在截止前才发现：当初看好的方法，放到真实数据上根本跑不动，此时已经来不及更换。这道关就是为了提前暴露这类问题。

- **`method-selector`** — 生成角色化短名单：一个主方法、一个可信 baseline、最多一个条件性备用；并输出覆盖假设、数据、输出退化、扰动和规模的风险探针摘要。
- **`decision-prompt-builder`** — 在真正的建模判断点提供简短选择卡，先问目标和取舍，不让使用者过早在算法名之间盲选。
- **`modeler-decision-logger`** — 将使用者答案忠实追加到 `methods/Qx/qx_decisions.jsonl`，不再为每个 skill 生成 PENDING 文件。

### 第 3 阶段 · 编码与代码审查（Gate G3）

先写代码，再做审查；审查结果要落成磁盘上的文件，而不是对话里一句"没问题"。

- **`model-code-analyzer`** — 在写代码前先规划 `experiments/roundN/` 的目录结构和 `run_summary.json` 的字段。
- **`python-model-code-generator`** — 实现目标为 `python` 时生成 `.py`，统一使用 `SEED = 2026`。
- **`matlab-model-code-generator`** — 生成 MATLAB / 北太天元可运行的 `.m`，避开 Live Script、App Designer 等比赛环境未必支持的特性。
- **`code-reviewer`** — 判断脚本语言，分发给对应的 reviewer。
- **`python-code-reviewer`** — 落盘 `code/Qx/reviews/qx_python_review.json`，为五项命名语义检查保存证据。
- **`matlab-code-reviewer`** — 使用相同检查，并补充运行时和兼容性证据。

### 第 4 阶段 · 结果、稳健性、图表与冻结（Gate G4 ★）

把原始实验输出整理成两部分：一份供论文手直接使用的材料包，以及一份记录"论文中所有数字"的冻结 JSON。冻结之后若因改 bug 等原因导致数值变化，须先记录变更、再重新冻结，不允许直接改动。

- **`result-report-generator`** — 普通轮次只读取运行摘要；决策点和最终轮才写报告，淘汰归档只依据使用者判定。
- **`robustness-checker`** — 只做与风险相关的敏感性、误差、baseline 和集中度检查，不为了数量填充通用清单。
- **`final-method-explainer`** — 撰写最终选定方法的完整说明，`methods/Qx/qx_final_method_explanation.md`。
- **`figure-table-planner`** — 将图分为四类：1 诊断、2 对比、3 论文、4 附录，其中诊断图不会进入论文。
- **`math-figure-generator`** — 从保存的证据出图，并实际检查渲染结果后才能定为论文图。
- **`solution-package-builder`** — 生成供论文手使用的材料包，以及 `results/Qx/reports/frozen_numbers.json`，该文件不应手工编辑。

### 第 5 阶段 · 论文写作与审计（Gate G5 + G6）

论文手依据材料包和冻结快照撰写论文，随后由三个独立审计分别检查：跨文件一致性、各 reviewer 文件是否齐备、以及整体 QA。任何一个不通过，论文都不能提交。

- **`paper-section-writer`** — 依据材料包和冻结数字写作；物理意义与贡献表述从人类决策账本转述。
- **`paper-polisher`** — 检查时态、措辞强弱、过度宣称、以及文档内公式的一致性。
- **`reference-manager`** — 生成 BibTeX 并核查引用真实性，虚构引用会被判为 blocking。
- **`consistency-auditor`** — 将论文里每个数字、文件名、符号与 `frozen_numbers.json`、磁盘文件、符号表逐一比对。
- **`completeness-auditor`** — 按当前 profile 检查必要的语义证据，不再要求每个 skill 都留下长报告。
- **`quality-assurance-auditor`** — 核查流程完整性、三条核心规则与反造假。作为最终一关，只有另外两个审计都通过时它才放行。

## 安装

本仓库现已同时打包为 **Claude Code** 与 **Codex/ChatGPT** 原生插件。一个安装脚本即可注册本仓库的 marketplace，并为其中一个或两个平台安装插件。

### 一键安装原生插件（推荐）

```bash
git clone https://github.com/zhnnky329/MathModeling-skills.git
cd MathModeling-skills
./install.sh
```

默认会以用户级范围为 Claude Code 与 Codex 同时安装 `mathmodeling-skills`。请保留这个克隆目录，它也是后续更新使用的本地 marketplace 源。安装后新开一个 Claude Code 或 Codex 会话。

只安装一个平台、预览操作或选择 Claude 安装范围：

```bash
./install.sh --target claude
./install.sh --target codex
./install.sh --dry-run
./install.sh --target claude --scope project --project-dir /path/to/contest
```

Claude 支持 `user`、`project`、`local` 三种 scope。Codex 目前通过已注册的 marketplace 管理插件，不使用这个 scope 参数。

### 部署完整的项目级约束

原生插件模式会提供全部 28 个 skill 和内置工作流规则。如果还希望把 `CLAUDE.md`、`AGENTS.md`、Claude 权限/Hook 以及两套独立 skill 树直接部署到比赛项目，请使用 project 模式：

```bash
./install.sh --mode project --target both --project-dir /path/to/contest
```

安装器不会静默覆盖不同内容。发生冲突时会停止；加 `--force` 后，脚本会先把被替换的文件或目录移动到带时间戳的备份，再写入新版本：

```bash
./install.sh --mode project --target both --project-dir /path/to/contest --force
```

任意命令都可加 `--dry-run` 先查看将执行的变更。完整参数见 `./install.sh --help`。

### 后续更新

```bash
cd MathModeling-skills
git pull
./install.sh
```

Claude 会刷新 marketplace 并更新已安装插件；Codex 会从当前 marketplace 包重新安装。更新后请新开会话。

### 原生插件结构

- Claude marketplace：`.claude-plugin/marketplace.json`
- Codex marketplace：`.agents/plugins/marketplace.json`
- 两个平台共享的可安装包：`plugins/mathmodeling-skills/`
- Claude manifest：`plugins/mathmodeling-skills/.claude-plugin/plugin.json`
- Codex manifest：`plugins/mathmodeling-skills/.codex-plugin/plugin.json`

`.claude/skills/` 与 `.codex/skills/` 仍是两套完整、可独立使用的开发副本。维护者同时更新两套副本后运行 `./scripts/sync-plugin.sh`；`./scripts/sync-plugin.sh --check` 会在分发包过期时失败。

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
├── planning/
│   ├── parse/  classification/  manifests/Qx.json
│   ├── symbol_table.md  model_assumptions.md
│   └── session_config.json     # interaction_mode + rigor_profile
├── methods/Qx/
│   ├── qx_method_card.md  qx_decisions.jsonl
│   └── probes/risk_probe_summary.json
├── code/
│   ├── Qx/                     # Python；reviews/qx_python_review.json
│   └── matlab/Qx/              # MATLAB 代码（同构）
├── results/Qx/
│   ├── experiments/roundN/     # figures / tables / metrics / run_summary.json
│   └── reports/                # 最终分析 + 材料包 + frozen_numbers.json
├── robustness/Qx/
├── paper/
│   ├── sections/
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
