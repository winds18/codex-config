# 自维护文件逐项审计清单

本清单保留首轮 65 个自维护文件的审计快照；后续新增工程流程及改动清单见 [REFINEMENT.md](REFINEMENT.md)，下列字节数不是当前工作区计量。

基线：`9618e008c3cbb387d8894e27dca52ab55dc58a60`；日期：2026-09-05。

覆盖 **65 个自维护文件**：原有 57 个，新增 8 个。逐文件审查结论与相应验证如下；仅语法/静态检查的地方明确标出，不将其等同运行验证。跨文件集成与产品来源见 [优化报告](IMPLEMENTATION.md)。

按同一范围计算的自维护 Markdown/TOML/YAML 共 42 个（当前数量，含新增适配文档）：**175,562 → 86,417 字节，减少 50.8%**。不含 audit/vendor/代码，字节不是 token。行数与文档减少不自动代表执行提速。

| 文件 | 状态 | 字节（前 → 后） | 审查与处理 |
| --- | --- | ---: | --- |
| [.gitattributes](../../.gitattributes) | 保留 | 280 → 280 | 保留第三方快照尾随空格规则；不隐藏正常文本差异。 |
| [.gitignore](../../.gitignore) | 已优化 | 178 → 202 | 保留凭证与临时产物忽略，增加 Python 字节码；忽略规则不替代扫描。 |
| [AGENTS.md](../../AGENTS.md) | 已优化 | 9,305 → 5,672 | 全局自主交付、授权持续、明确有收益委派、主任务关键路径、有限验证与能力边界。 |
| [AGENTS.override.md](../../AGENTS.override.md) | 已优化 | 2,084 → 1,483 | 仓库维护规则与待分发全局规则分开；跨文件同步与临时恢复测试；不真实安装。 |
| [README.md](../../README.md) | 已优化 | 6,941 → 4,546 | 统一新行为、默认预览、安装/卸载入口、技能与角色路由、审计导航。 |
| [agents/explorer-lite.toml](../../agents/explorer-lite.toml) | 已优化 | 716 → 486 | 只读定向定位，Luna/low；不全仓泛读或重复主任务已知调查。 |
| [agents/orchestrator.toml](../../agents/orchestrator.toml) | 已优化 | 1,066 → 535 | 可选复杂统筹，仍实现关键路径与集成；继承宿主模型/推理。 |
| [agents/planner.toml](../../agents/planner.toml) | 已优化 | 773 → 476 | 只读最小计划，无固定文档或审批前置；继承宿主。 |
| [agents/pr-preparer.toml](../../agents/pr-preparer.toml) | 已优化 | 676 → 464 | 只读起草实际变更说明；Terra/medium，不自行发布。 |
| [agents/refiner.toml](../../agents/refiner.toml) | 已优化 | 627 → 447 | 限定文件机械整理；Terra/medium，公共接口改动回报负责人。 |
| [agents/reviewer-lite.toml](../../agents/reviewer-lite.toml) | 已优化 | 686 → 486 | 只读可复现正确性/回归问题；Terra/medium，不以风格偏好造缺陷。 |
| [agents/security-lite.toml](../../agents/security-lite.toml) | 已优化 | 768 → 446 | 只读限定初筛；Terra/low，不声称全面安全结论。 |
| [agents/security-reviewer.toml](../../agents/security-reviewer.toml) | 已优化 | 780 → 450 | 只读高风险数据流/权限复核；继承宿主模型，测试隔离。 |
| [agents/summarizer-lite.toml](../../agents/summarizer-lite.toml) | 已优化 | 691 → 469 | 只读压缩已给证据；Luna/low，保留冲突和未验证面。 |
| [agents/tester-lite.toml](../../agents/tester-lite.toml) | 已优化 | 751 → 563 | 只读失败归因；Terra/medium，可能写入的测试使用有权限的执行环境。 |
| [agents/worker.toml](../../agents/worker.toml) | 已优化 | 806 → 535 | 按文件组自主实现和验证，保留同伴改动；继承宿主模型/推理。 |
| [docs/client-compatibility.md](../../docs/client-compatibility.md) | 新增 | 0 → 3,764 | 新增模型/客户端差异、技能发现、原生 Goal/自动化边界及测量方法；核实官方来源。 |
| [docs/codex-global-setup-overview.md](../../docs/codex-global-setup-overview.md) | 已优化 | 9,335 → 1,967 | 各层只维护自身职责，连接入口；不复制完整规则。 |
| [docs/git-workflow-policy.md](../../docs/git-workflow-policy.md) | 已优化 | 6,404 → 1,907 | 授权分别判断，扫描真实历史，明确本地 hooks 与内容扫描边界。 |
| [docs/hook-enforcement-policy.md](../../docs/hook-enforcement-policy.md) | 已优化 | 5,701 → 2,192 | 与实际单 PreToolUse 对齐；提示不授予权限，覆盖范围与恢复明确。 |
| [docs/project-AGENTS-template.md](../../docs/project-AGENTS-template.md) | 已优化 | 13,582 → 1,394 | 短模板只保留项目事实、真实命令与文件/接口归属。 |
| [docs/project-codex-config-template.md](../../docs/project-codex-config-template.md) | 已优化 | 1,623 → 2,068 | 权限例子保持按项目采用，补可选并发容量；不锁机器模型。 |
| [docs/project-expansion-workflow.md](../../docs/project-expansion-workflow.md) | 已优化 | 12,012 → 1,658 | 初始化服务真实主路径；没有固定五件套，成熟仓库不重做 bootstrap。 |
| [docs/project-plan-template.md](../../docs/project-plan-template.md) | 已优化 | 4,848 → 891 | 必要阶段、依赖、负责文件和验收；不复制应用任务台账。 |
| [docs/restore-codex-official-state.md](../../docs/restore-codex-official-state.md) | 已优化 | 1,598 → 1,868 | 明确恢复安装前状态，默认预览，配置与 Git 两类中断恢复。 |
| [docs/restore-codex-setup.md](../../docs/restore-codex-setup.md) | 已优化 | 1,717 → 2,178 | 逐项安装、单技能目录、CODEX_HOME、旧安装迁移限制及信任说明。 |
| [docs/thread-governance-policy.md](../../docs/thread-governance-policy.md) | 已优化 | 9,363 → 3,701 | 统一当前任务/子代理/worktree 概念；明确拆分、主任务、等待、集成与失败处理。 |
| [git-hooks/pre-commit](../../git-hooks/pre-commit) | 保留 | 130 → 130 | 保留真实 guard 入口；检查方式由 guard 更新，shell 语法通过。 |
| [git-hooks/pre-push](../../git-hooks/pre-push) | 已优化 | 184 → 344 | 使用 pre-push 广告 ref 输入检查目标历史，再执行 guard。 |
| [hooks/codex-policy-guard.py](../../hooks/codex-policy-guard.py) | 已优化 | 11,697 → 13,493 | 取消所有生命周期文本门禁；有限直接命令、结构化目标、live 链接及 Git 提示；74 回归。 |
| [hooks/hooks.json](../../hooks/hooks.json) | 已优化 | 2,958 → 402 | 只保留 PreToolUse matcher；受控 command 安装时绑定配置根；结构/安装集成检查。 |
| [prompts/agent-work-habits.md](../../prompts/agent-work-habits.md) | 已优化 | 7,184 → 621 | 缩为可选人工入口，取消启动/压缩 hook 注入。 |
| [prompts/init-project.md](../../prompts/init-project.md) | 已优化 | 1,068 → 585 | 引导 bootstrap 最小运行路径，用户已要求实现则继续。 |
| [prompts/subagent-work-habits.md](../../prompts/subagent-work-habits.md) | 已优化 | 969 → 513 | 短工作包模板，明确文件、依赖、证据；无固定输出长度。 |
| [scripts/codex-config-doctor.sh](../../scripts/codex-config-doctor.sh) | 新增 | 0 → 410 | 新增只读诊断入口；语法及真实仓库临时 roundtrip。 |
| [scripts/codex-config-guard.sh](../../scripts/codex-config-guard.sh) | 已优化 | 10,703 → 1,014 | 移除口号/模型代际断言，串接结构/语法/行为/资产/敏感与安装验证。 |
| [scripts/install-git-hooks.sh](../../scripts/install-git-hooks.sh) | 已优化 | 876 → 400 | 统一 Python 管理器入口；默认预览，支持卸载/恢复；Bash 3.2 兼容验证。 |
| [scripts/manage-codex-config.py](../../scripts/manage-codex-config.py) | 新增 | 0 → 21,834 | 新增逐项清单/备份/合并/锁/事务/诊断；两轮独立复核与安装回归。 |
| [scripts/manage-git-hooks.py](../../scripts/manage-git-hooks.py) | 新增 | 0 → 9,701 | 新增 worktree 作用域/原值保真/共享扩展保护/pending 恢复；独立复核及真实骤停测试。 |
| [scripts/restore-codex-global-links.sh](../../scripts/restore-codex-global-links.sh) | 已优化 | 2,709 → 747 | 保留旧命令名，默认预览；已安装入口识别自身配置根；参数兼容验证。 |
| [scripts/restore-codex-official-state.sh](../../scripts/restore-codex-official-state.sh) | 已优化 | 3,154 → 751 | 保留旧命令名，精准卸载；不按时间猜备份；自定义根与参数验证。 |
| [scripts/secret-scan.py](../../scripts/secret-scan.py) | 已优化 | 7,309 → 9,442 | merge/多远程/新 ref/类型变化历史覆盖；blob 去重但路径单独检查；22 回归。 |
| [scripts/test-policy-guard.py](../../scripts/test-policy-guard.py) | 已优化 | 5,162 → 7,627 | 74 正反例，覆盖文本误报、直接命令、patch move、自定义根和废弃事件。 |
| [scripts/test-restore-roundtrip.py](../../scripts/test-restore-roundtrip.py) | 新增 | 0 → 20,297 | 新增 26 个安装与 Git 行为场景；含完整仓库临时安装与真实 os._exit 中断。 |
| [scripts/test-restore-roundtrip.sh](../../scripts/test-restore-roundtrip.sh) | 已优化 | 2,781 → 179 | 改为隔离 Python 测试入口；保持旧使用命令。 |
| [scripts/test-secret-scan.sh](../../scripts/test-secret-scan.sh) | 已优化 | 2,444 → 6,051 | 22 隔离 Git 场景，无真实凭证/远程推送。 |
| [scripts/validate-config.py](../../scripts/validate-config.py) | 新增 | 0 → 5,619 | 新增 TOML/skill/hook 结构及本地引用验证；3.9 有限语法回退，另用完整解析器复核。 |
| [scripts/workspace-cleanliness-check.sh](../../scripts/workspace-cleanliness-check.sh) | 已优化 | 874 → 1,512 | 未暂存噪音提示，暂存临时文件阻断，NUL 路径处理；三个隔离场景验证。 |
| [skills/autonomous-project-execution/SKILL.md](../../skills/autonomous-project-execution/SKILL.md) | 已优化 | 2,789 → 1,834 | 无 spec/plan 前置；主任务关键路径与独立模块委派；实际任务试用。 |
| [skills/autonomous-project-execution/references/agent-role-matrix.md](../../skills/autonomous-project-execution/references/agent-role-matrix.md) | 已优化 | 5,839 → 1,711 | 按需角色和继承模型；不默认全团队，不把高能力模型只留给管理。 |
| [skills/autonomous-project-execution/references/autonomous-execution-workflow.md](../../skills/autonomous-project-execution/references/autonomous-execution-workflow.md) | 已优化 | 8,283 → 1,912 | 依赖启动、并行写入、集成证据、失败归因与最小续接信息。 |
| [skills/feature-thread-launch/SKILL.md](../../skills/feature-thread-launch/SKILL.md) | 已优化 | 3,178 → 1,392 | 显式独立任务请求才触发；真实项目/ID/默认模型与异步状态。 |
| [skills/feature-thread-launch/references/feature-thread-launch-checklist.md](../../skills/feature-thread-launch/references/feature-thread-launch-checklist.md) | 已优化 | 3,199 → 768 | 短交接包，不复制任务台账；按实际工具追踪。 |
| [skills/project-bootstrap/SKILL.md](../../skills/project-bootstrap/SKILL.md) | 已优化 | 2,487 → 1,401 | 精确触发空/缺入口项目；建立可运行结果，普通实现无需额外文档。 |
| [skills/refero-design-prompts/SKILL.md](../../skills/refero-design-prompts/SKILL.md) | 已优化 | 7,205 → 3,931 | 缩短入口、按需参考、设计事实源与并行归属；许可和渲染边界。 |
| [skills/refero-design-prompts/agents/openai.yaml](../../skills/refero-design-prompts/agents/openai.yaml) | 已优化 | 284 → 285 | 缩小默认 prompt 到实际交付；完整 YAML/UI metadata 检查。 |
| [skills/refero-design-prompts/references/design-md-contract.md](../../skills/refero-design-prompts/references/design-md-contract.md) | 已优化 | 7,260 → 3,662 | 取消 token 双真源；DESIGN 记录来源/差异/共享接口与验收。 |
| [skills/refero-design-prompts/references/motion-craft-workflow.md](../../skills/refero-design-prompts/references/motion-craft-workflow.md) | 已优化 | 6,177 → 3,271 | 取消绝对美学门禁及未安装术语依赖；保留状态/中断/降级/性能验证。 |
| [skills/refero-design-prompts/references/output-templates.md](../../skills/refero-design-prompts/references/output-templates.md) | 已优化 | 5,624 → 2,302 | 固定五段与重复 schema 改为按需骨架；实现请求继续代码。 |
| [skills/refero-design-prompts/references/style-taxonomy.md](../../skills/refero-design-prompts/references/style-taxonomy.md) | 已优化 | 5,816 → 5,968 | 全文复核六类方向；保留参考，明确用户/项目选择优先。 |
| [skills/refero-design-prompts/references/substyle-recipes.md](../../skills/refero-design-prompts/references/substyle-recipes.md) | 已优化 | 4,586 → 4,738 | 全文复核三类细分；保留可选深化，不升级全局风格规则。 |
| [skills/refero-design-prompts/references/visual-archetypes.md](../../skills/refero-design-prompts/references/visual-archetypes.md) | 已优化 | 10,761 → 10,877 | 全文复核 14 原型；修正许可/复制边界和绝对美学禁令。 |
| [skills/refero-design-prompts/scripts/test-template-dependencies.py](../../skills/refero-design-prompts/scripts/test-template-dependencies.py) | 新增 | 0 → 3,025 | 新增 7 故障注入场景，在临时副本验证真实检查能力。 |
| [skills/refero-design-prompts/scripts/verify-template-assets.sh](../../skills/refero-design-prompts/scripts/verify-template-assets.sh) | 已优化 | 3,905 → 4,034 | 保留快照结构入口，接入离线依赖验证，不执行 vendor。 |
| [skills/refero-design-prompts/scripts/verify-template-dependencies.py](../../skills/refero-design-prompts/scripts/verify-template-dependencies.py) | 新增 | 0 → 9,855 | 新增全文件分类/语法/来源/引用/package-lock/媒体摘要检查。 |

## 其余文件与证据

- 294 个上游快照文件逐文件记录在 [前端文件清单](frontend-file-review.md#全部-vendor-文件清单)。已检查离线可验证项并确认相对本次基线没有内容修改；未声称全部运行或逐行语义审计。
- `REPORT.md` 与 `global-guidance-candidate.md` 保留初次审计语境；已加历史说明，原代码位置链接固定基线 commit，避免随实现变化失真。
- `reproduce.py` 固定从基线 commit 加载原 hook/scanner，隔离复现原缺陷；`reproduction-results.json` 保留首次原结果。
- `IMPLEMENTATION.md`、本清单、`frontend-file-review.md`、`workflow-evaluation.md` 保存本次结论；`verification-results.json`、`format-validation.json`、`delivery-checks.json` 保存检查结果，`reviewed-files.json` 记录 359 个配置/资产文件摘要。它们均不安装到用户规则目录。
- `workflow-trial/` 的 README、orders.py、summary.py、export_csv.py、三个 tests 文件分别检查输入契约、实现行为与边界测试；9 个测试通过。该小样本不代表真实并行速度评估。
