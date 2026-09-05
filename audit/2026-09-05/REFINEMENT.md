# 工程流程与约束凝练

> 本文及配套 JSON 保留本轮完成时的快照。后续安装入口、诊断与测试改动见 [一键安装优化](INSTALLATION.md)。

日期：2026-09-05。基于首轮优化工作区继续调整，保留已有安全与安装修复。用户追加要求为：自主并行开发、先架构再接口定义、之后并行实现，以及测试、目录规范和临时文件用完删除。

## 本轮结果

全局约定从 **5,672 → 3,795 字节，进一步减少 33.1%**，56 → 35 行。自主执行技能入口从 1,834 → 1,329 字节。重复的协作文档改为导航，具体流程分别由“软件工程”和“并行交接”两个按需参考维护。

新增软件工程参考 5,536 字节，以容纳本轮明确要求的架构、接口、测试和清理细节；它只在相关任务阶段读取。凝练针对常驻与重复内容，不以删掉必要工程约束取得更小总字数。

本轮更新 **18 个已有自维护文件，新增 1 个工程流程文件**；目前合计 66 个自维护文件。安装器、hooks、扫描器、验证脚本及 294 个上游快照均未在本轮改动。逐文件变化见下表，首轮完整审计见 [历史清单](file-review.md)。

## 软件开发执行顺序

**需求与验收 → 架构及模块边界 → 接口契约 → 并行实现 → 集成验证 → 清理与交付。**

- 需求先明确可观察结果、兼容性和验收场景。
- 架构明确职责、依赖和相关数据/失败边界；接口明确输入输出、类型约束、错误语义及消费者。
- 共享接口确定后才启动依赖实现。以语言类型/schema/已有 API 规范为权威来源，文档引用它，避免双方各自猜接口。
- 同时开发独立模块；共享基础、锁文件及冲突运行资源由单一负责人管理。主任务继续关键路径并做真实集成。
- 现有架构和契约充分时直接复用；局部修复无需重建框架或补齐固定文档。阶段推进由主任务依据已有授权判断，不新增逐阶段用户审批。

入口：[软件工程流程](../../skills/autonomous-project-execution/references/software-engineering-workflow.md)。

## 加强的可执行约束

| 约束 | 避免的问题 | 遵守方式 |
| --- | --- | --- |
| 接管须确认停止 | 原代理失联但仍写文件，新代理覆盖其工作 | 核对实际执行状态、遗留 diff 和运行资源，再交接；超时不等于停止 |
| 授权随工作包传递且不扩大 | 子代理重复追问、自行发布或绕过既有拒绝 | 明确已有授权、禁止动作；约束变化同步受影响代理 |
| 证据对应当前集成状态 | 局部旧测试通过，被当成后来集成成功 | 记录实际检查及对应状态；相关共享变更后重跑受影响检查 |
| 验收强度不能被削弱 | 删除测试、放宽断言或忽略错误制造通过 | 以原需求判断；错误测试可修，但说明依据并保留等效或更强验证 |
| 文件与运行资源都划归属 | 不同文件测试仍抢同一数据库、端口或输出目录 | 能隔离则隔离，冲突步骤串行；worktree 不被当作服务隔离 |
| 自有临时文件用完即删 | 根目录堆积、异常退出泄留、误删同伴文件 | 任务独占目录、上下文/finally/trap 清理；强杀后核实归属再清理 |

这些属于行为与工程约束，没有新增关键词 hook 或人工批准阶段。新规则的维护要求也写入仓库 override：须明确故障、适用范围和可观察的遵守方式，不把偏好积累为全局门禁。

## 测试和目录

测试规则按改动类型选择：业务规则与回归、接口/数据契约、存储/副作用、用户关键路径、构建配置、低风险机械修改各有验收重点；完成项目既有必要检查，不设置统一覆盖率或无条件全套测试。Mock 用于隔离，真实集成需单独证明。

沿用现有目录职责；新项目只建立实际需要的源码、测试/fixtures、运维脚本与文档。临时文件优先系统临时目录，项目内需要时放任务独占子目录；保留的交付证据放指定产物目录并说明用途。gitignore 不能证明已清理，清洁脚本也不自动删除未知所有者的文件。

初始化技能、模板、worker/orchestrator、人工 prompts 和 Git 文档已同步，避免其他入口绕过这套顺序或清理责任。

## 行为验证

使用独立代理在临时 Python 3.9 项目完成库存解析与汇总。输入仅包含现有不可变 Stock 契约、原测试、用户草稿和其他任务临时文件，没有提供预期架构方案。

实际顺序：核实既有契约 → 划分解析/汇总 → 一个子代理写汇总、主执行者写解析 → 核对差异 → 集成测试 → 临时文件清理。**16/16 测试通过**；保存产物后主任务独立重跑同样通过。临时 JSON 输入跑通解析到汇总，非法布尔数量在正确行报错；所有原文件保留，没有多余缓存/产物。

可复查 [试用项目](engineering-trial/README.md) 与 [验证记录](refinement-verification.json)。保留源码和测试作为审计证据；系统临时试验目录在提取证据后清理。

最终全仓 guard 通过：74 个 hook、22 个敏感信息扫描、26 个安装恢复及 7 个模板依赖行为用例，共 **129 个**；4 个技能通过官方校验，11 个角色 TOML 与 UI metadata 通过完整解析。此次使用及上一轮已不用的 7 个自有临时文件/目录已清除，保留的 audit 内容为明确的交付证据。

这证明本样本中顺序、模块委派、集成验收和清理可执行；没有运行复杂业务项目、强杀并行开发代理或模型 A/B，不能据此承诺固定倍数提速。

## 本轮文件清单

字节以首轮优化文件摘要为起点，统计实际文本；不是 token 或运行费用。

| 文件 | 字节（上一轮 → 本轮） |
| --- | ---: |
| [AGENTS.md](../../AGENTS.md) | 5,672 → 3,795 |
| [AGENTS.override.md](../../AGENTS.override.md) | 1,483 → 1,663 |
| [README.md](../../README.md) | 4,546 → 4,905 |
| [agents/orchestrator.toml](../../agents/orchestrator.toml) | 535 → 487 |
| [agents/worker.toml](../../agents/worker.toml) | 535 → 484 |
| [docs/codex-global-setup-overview.md](../../docs/codex-global-setup-overview.md) | 1,967 → 2,053 |
| [docs/git-workflow-policy.md](../../docs/git-workflow-policy.md) | 1,907 → 2,257 |
| [docs/project-AGENTS-template.md](../../docs/project-AGENTS-template.md) | 1,394 → 1,438 |
| [docs/project-expansion-workflow.md](../../docs/project-expansion-workflow.md) | 1,658 → 1,858 |
| [docs/project-plan-template.md](../../docs/project-plan-template.md) | 891 → 960 |
| [docs/thread-governance-policy.md](../../docs/thread-governance-policy.md) | 3,701 → 933 |
| [prompts/agent-work-habits.md](../../prompts/agent-work-habits.md) | 621 → 342 |
| [prompts/init-project.md](../../prompts/init-project.md) | 585 → 537 |
| [prompts/subagent-work-habits.md](../../prompts/subagent-work-habits.md) | 513 → 507 |
| [skills/autonomous-project-execution/SKILL.md](../../skills/autonomous-project-execution/SKILL.md) | 1,834 → 1,329 |
| [skills/autonomous-project-execution/references/agent-role-matrix.md](../../skills/autonomous-project-execution/references/agent-role-matrix.md) | 1,711 → 1,362 |
| [skills/autonomous-project-execution/references/autonomous-execution-workflow.md](../../skills/autonomous-project-execution/references/autonomous-execution-workflow.md) | 1,912 → 2,835 |
| [skills/project-bootstrap/SKILL.md](../../skills/project-bootstrap/SKILL.md) | 1,401 → 1,509 |
| [skills/autonomous-project-execution/references/software-engineering-workflow.md](../../skills/autonomous-project-execution/references/software-engineering-workflow.md) | 0 → 5,536 |

## 依据与验证边界

设计以本仓库的实际重复/缺口、用户工程流程要求及独立试用为依据。当前官方建议明确有收益的委派条件，并按变化与风险限制重复验证；关于含糊技能造成停工的指导也支持减少跨层重复。[模型指导](https://developers.openai.com/api/docs/guides/latest-model)

本地 Codex 可以依据 AGENTS/技能中的明确要求委派；并行写入需要处理冲突和协调成本。[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

本次修改仅保存在克隆仓库，未安装真实全局配置、未修改实际 Git hooks、未提交或推送。已有脚本的恢复、安全和模板验证继续由全仓 guard 检查；实际客户端的技能发现与 hook 信任不由隔离试验推定。
