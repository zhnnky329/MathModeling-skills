# Initial Prompt

[English](<./Initial Prompt.md>) | [简体中文](<./Initial Prompt-zh.md>)

你正在使用本仓库帮助我完成一道数学建模竞赛题。

在开始建模、写代码或写论文之前，请先阅读项目规则和 skills：

- AGENTS.md 或 CLAUDE.md
- .codex/skills/ 或 .claude/skills/ 下相关的 SKILL.md

请把这个仓库当作一个分阶段的数学建模工作流，而不是一键论文生成器。

除非我明确要求跳过，否则请按照以下标准流程执行：

workflow-orchestrator
→ problem-parser
→ problem-classifier
→ related-paper-analyzer
→ data-auditor-cleaner
→ decision-prompt-builder
→ method-selector
→ symbol-table-builder
→ model-assumptions-builder
→ model-code-analyzer
   ├── python-model-code-generator
   └── matlab-model-code-generator
→ code-reviewer
   ├── python-code-reviewer
   └── matlab-code-reviewer
→ result-report-generator
→ robustness-checker
→ final-method-explainer
→ figure-table-planner
→ math-figure-generator
→ solution-package-builder
→ paper-section-writer
→ paper-polisher
→ reference-manager
→ consistency-auditor
→ completeness-auditor
→ quality-assurance-auditor
→ workflow-orchestrator

核心规则：

- 不要一开始就选模型。
- 先从目标、对象、约束、数据、输出、变量、关系和可检验结论开始。
- 题目没有解析完成前，不要进入方法选择。
- 方法卡没有通过风险探针、且使用者尚未记录方法选择前，不要生成代码。
- 没有结果 artifact 前，不要写带具体数字的论文结论。
- 没有 baseline 和稳健性/敏感性检查前，不要声称模型更优。
- QA 没通过前，不要组装最终论文。
- 不要修改 workspace/data_raw/ 下的原始数据。
- 不要编造数据、数值结果、参考文献、图表、实验或模型性能结论。
- 默认使用 `interaction_mode: learning` 与 `rigor_profile: lean`；只有论文手交接或终稿阶段才切换为 `submission`。
- `lean` 阶段不强制每轮长报告、成功日志、冻结数字或最终审计。
- 使用者决策统一写入 `methods/Qx/qx_decisions.jsonl`，不再为每个 skill 生成 PENDING 文件。

三条关键规则：
- 规则 1：没有最终方法详解（methods/Qx/qx_final_method_explanation.md），不准写最终论文。
- 规则 2：没有最终结果分析（results/Qx/reports/qx_final_result_analysis.md），不准交给论文手。
- 规则 3：论文手只看材料包（results/QX/reports/qx_solution_package_for_writer.md），不从零散结果里猜。

请使用以下 workspace 约定：

project/
├── planning/                   # 解析/分类/符号表/假设/manifest/session 配置
├── methods/Qx/                 # 方法卡/决策账本/风险探针/最终方法详解/图表规划
├── code/Qx/                    # Python 代码
├── code/matlab/Qx/             # MATLAB 代码
├── results/Qx/
│   ├── experiments/roundN/     # 实验输出（figures/tables/metrics/run_summary.json）
│   └── reports/                # 实验报告/最终结果分析/论文材料包
├── robustness/Qx/              # 稳健性报告
├── paper/                      # 论文手区（sections/figures/refs.bib/main.tex/qa_report.md）
├── workspace/data_raw/         # 原始数据（只读）
├── workspace/data_clean/       # 清洗后数据
└── scratch/                    # 临时探索

如果这是一个新的竞赛题，请先运行 workflow-orchestrator 判断当前阶段，然后从 problem-parser 开始。

在 problem-parser 阶段，请提取：

- 题目背景
- 总目标
- 研究对象
- 子问题
- 约束条件
- 数据清单
- 所需输出
- 初步变量
- 初步关系
- 歧义点
- 风险点
- 缺失信息
- 推荐的下一个 skill

在问题解析阶段不要选择最终模型。

分析题目时，请考虑：

1. 问题背景  
   重述题目的关键点，识别真实背景和相关领域。

2. 假设与变量  
   提出必要的简化假设，识别关键变量、参数和变量关系。区分可控变量、可观测量和外部参数。

3. 题型判断  
   对每个子问题分别分类。不要因为题目标题像某一类，就把整道题强行归成一个题型。

4. 相关论文分析  
   在最终定方法前，收集并分析相关论文、报告或参考解法。提炼可迁移的方法思路、假设、数据需求和风险。不要编造参考文献，也不要盲目照搬论文模型。

5. 建模路线  
   先让我选择输出形式、可解释性、不可接受风险和实验预算；再筛选一个主方法、一个可信 baseline，以及最多一个条件性备用。不要为了数量凑候选。风险探针必须包含输出集中或退化检查。

6. 求解与验证  
   明确需要哪些输出、指标、表格和图。需要和 baseline 对比，并规划稳健性或敏感性检查。

7. 局限性  
   说明模型不能支持什么，哪些假设较强，哪些数据限制仍然存在。

后续写论文分节时：

- 使用连贯、自然的学术表达。
- 避免空泛套话。
- 避免明显 AI 味的表达。
- 除符号表、算法、表格、检查清单等必要场景外，不要滥用分点。
- 不要加入现有 artifacts 不支持的内容。
- 每个数值结论都必须来自结果文件。
- 每个图表引用都必须对应已有或明确规划的 artifact。
- 每个结论都必须回扣原始子问题。

第一个任务：

现在运行 workflow-orchestrator。

请返回：

- 当前阶段
- 已完成 artifacts
- 缺失 artifacts
- 阻塞项
- 下一个 skill
- 具体下一步动作
