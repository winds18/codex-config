# 客户端与模型适配

可用性取决于客户端、账号、当前工具契约与受管策略；本文不触发安装、模型切换或实验 feature 启用。

## 模型路由

主任务保持用户所选模型；内置子代理默认按根主任务低一能力档动态选型，不固定型号。外部 Agent 按能力与总成本选择，不假定其模型档位或配置与 Codex 相同。判断依据、同档例外与不可用时的处理见 [角色与模型选择](../skills/autonomous-project-execution/references/agent-role-matrix.md)；两种执行模式见 [并行执行与交接](../skills/autonomous-project-execution/references/autonomous-execution-workflow.md#划分工作)。

显式选型以执行端可用列表为准。例如 GPT-6.2 Astra 适合跨服务诊断，Sol 适合常规实现与复核，不构成固定配对。Max 加深单任务推理；Ultra 可自动派出子代理，适合能独立推进的工作。使用 Ultra 时只手动委派尚未覆盖的工作包，共用主任务资源额度；它不授权接入外部 Agent。[官方模型](https://learn.chatgpt.com/docs/models)、[Codex 提示指南](https://learn.chatgpt.com/guides/prompting-gpt-6-2-astra)

API 的异步工具、mid-turn steering 与 `configuration_update` 不代表所有客户端均支持。CLI 0.163 起即时纠偏默认开启；打断会停止活跃 Code Mode 单元及其嵌套工具调用，但不证明由它们启动的外部进程已经回收。仍须按进程所有权和实际状态确认清理。[模型指导](https://developers.openai.com/api/docs/guides/latest-model)、[变更日志](https://learn.chatgpt.com/docs/changelog)

角色 TOML 使用 `name`、`description`、`developer_instructions`，可选 `model`、`model_reasoning_effort`。模型/推理配置按角色文件、显式创建参数、`[agents]` 默认、父任务的优先级解析；创建参数或 `[agents]` 显式选模型且未配置推理强度时，采用所选模型默认值。当前没有原生“低一档”参数，须由编排者选型。自定义角色与内置角色同名会覆盖后者。[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## 技能与配置入口

交互端用于显示界面和发出请求，不代表 Agent 或工具的执行位置。路径、`localhost`、端口和进程归属按工具实际执行环境解释，配置与技能以 Agent 实际加载来源为准，不假定跨环境自动继承。无需先检测 SSH 或推断连接方式；跨环境访问、传输或预览时再明确两端。能力缺失时采用可用替代方式，保持验收目标并说明未验证面。

本仓库配置按 [安装说明](restore-codex-setup.md) 分发到 Agent 运行账号实际使用的配置根和技能目录；交互端安装不代表另一执行环境已加载。技能入口包括 `~/.agents/skills`、项目 `.agents/skills`；`.codex/skills` 兼容入口按宿主实际发现情况使用，不重复安装同名技能。[技能发现](https://learn.chatgpt.com/docs/build-skills)

AGENTS 层级和同目录 override 仍有效；本仓库 override 只用于维护，不能装到用户全局。项目权限模板仅在宿主支持且不违背受管策略时采用。非交互 CLI 缺少项目配置或 MCP 时，区分沙箱写权限与项目信任；支持的 `exec` / `review` 中，`--trust` 持久生效，不作为临时修复自动追加。[AGENTS](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[非交互项目信任](https://github.com/openai/codex/pull/60041)

支持的客户端可在既有会话刷新插件工具、技能与 hooks，不等于任意 AGENTS 或角色配置自动热刷新。规则更新可显式重读适用文件并保留目标、成果和授权；实际发现结果仍需确认，hook 信任仍由用户审查。仅在刷新未生效或宿主要求时重建会话。[变更日志](https://learn.chatgpt.com/docs/changelog)

## 工具与生命周期

### 子代理权限与生命周期

子代理继承父任务权限；角色文件中的 `sandbox_mode`、`approval_policy`、`model_provider`、`mcp_servers` 不覆盖父配置。“不修改文件”是行为约束，不建立只读沙箱；实际写入限制由父任务权限策略和执行环境提供。可按职责试用关闭无关技能或受支持能力，以验证收益决定是否保留，不默认全关。[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

CLI 0.164 改进旧安装、废弃 marketplace checkout 和 daemon 日志清理，不替代任务自建资源的回收。CLI 0.166 提供 `codex doctor --network-only` 做配置、连通性和 WebSocket 诊断；`codex queue --resume` 在排队后尝试恢复既有线程，恢复失败时命令仍可能成功，须检查恢复结果。仅在实际排障或已授权续办时使用，不设为常规必跑步骤。[变更日志](https://learn.chatgpt.com/docs/changelog)

- 子代理适合任务内部独立工作；新用户任务需要对应用户请求，按当前工具契约创建和等待。
- 原生 Goal 只在显式请求时建立，运行中补充要求继续当前工作。[长期工作](https://learn.chatgpt.com/docs/long-running-work)。自动化须有后续工作请求，同任务跟进优先当前上下文，独立运行按独立任务处理；无变化静默，通知策略用工具字段保存。
- 本地步骤依赖在线、已连接且获授权的电脑。启用本机访问后，符合条件的 Work Cloud 新任务可从网页或移动端续接并使用获准本机资源；旧任务保留原模式，Codex 不据此改变执行方式。按实际编排位置、执行环境和授权判断可达性，不按聊天入口推断；环境改变后核对所依赖的权限与 hooks。[本机访问](https://learn.chatgpt.com/docs/enterprise/cloud-local-access)、[Scheduled tasks](https://learn.chatgpt.com/docs/automations)
- [官方 Hooks](https://learn.chatgpt.com/docs/hooks) 支持 MCP 拦截、PermissionRequest/Interrupt；本仓库仅分发 PreToolUse。其 ask 不作审批实现，hook 不替代客户端权限，见 [Hooks 与验证边界](hook-enforcement-policy.md)。
- 按需发现工具/插件并读取相关技能，先利用已提供能力；确认缺失才回退到其他获授权方式，不把发现入口当成安装或信任授权。
- MCP OAuth 恢复不自动重放已拒工具调用；重试先核对授权与执行状态。

## 代码审查

审查分流、基线和结果复用统一见 [变更审查](../skills/autonomous-project-execution/references/software-engineering-workflow.md#变更审查)；客户端入口不构成新的必跑流程。

| 入口 | 适用范围与限制 |
| --- | --- |
| 本地 `/review` / CLI `codex review` | 审查 Git 检出差异；桌面支持基准分支与未提交改动，CLI 还支持指定提交。`--uncommitted` 包含已暂存、未暂存及未跟踪文件；实际参数先核对当前二进制，不能把聊天命令当作代理工具调用 |
| Code Review 插件 | 查看 PR 差异、评论和检查，并发起审查；需对应源账号及仓库权限。插件的 Review instructions 用于其 `Review with Codex` 入口，不假定本地角色、全局规范或客户端设置自动同步到云端审查 |
| Codex Security | 用于安全变更复核或按需仓库扫描，不等同于一般代码审查；需实际可用的插件与权限，不默认安装或叠加运行 |

本地审查默认在当前会话报告发现；Detached 设置和 PR 的 `Review with Codex` 可启动独立会话，不为内部复核擅自改变会话设置。审查不直接修改工作区，修复另按授权执行。差异面板默认的 Unstaged 和 Last turn 不是完整交付范围，多仓需核对所选仓库。[代码审查](https://learn.chatgpt.com/docs/code-review)

PR 聊天中的分析不会自动发布意见；在 Summary / Changes 中发表评论会立即发送，不必等 Submit review。批准、请求修改、合并及推送也须各自核对授权。CI 的 Fix 入口只准备消息，不等于已执行修复或复验。[反馈与跟进](https://learn.chatgpt.com/docs/code-review#share-feedback-and-follow-up)

## 跨项目与任务工具

工程流程见 [跨项目与既有任务统筹](../skills/autonomous-project-execution/references/autonomous-execution-workflow.md#跨项目与既有任务统筹)。下列桌面接口仅作定位线索，名称、参数、上限与可用性以当前工具契约为准，不外推到子代理、CLI 或其他客户端。

多端任务可按“项目·职责·阶段目标”命名，见 [多端任务分工](../skills/autonomous-project-execution/references/autonomous-execution-workflow.md#按职责组织多端任务)。分类、移动或重命名须有用户相应请求及可用工具。侧栏与标题只作导航，不代表上下文共享、从属或写入隔离；用户任务平级，调度以真实 ID 和归属为准。

| 用途 | 当前接口与关键边界 |
| --- | --- |
| 查找/读取既有工作 | `list_projects`、`list_threads`、`read_thread`；按返回 ID、宿主和项目定位，先摘要后必要历史，动态状态不另建台账 |
| 续接/等待 | `send_message_to_thread` 会向用户显示提示并触发执行，须按已有授权发送增量；`wait_threads` 按契约优先事件/游标或有界等待，期间继续独立工作，不循环回读全历史 |
| 创建/分叉 | `create_thread` 需明确新任务请求，先查项目并遵从指定起点；隔离方式按契约确认。异步创建标识不等于就绪任务 ID；`fork_thread` 的历史范围按契约确认，不假定包含未完成回答 |
| 移动执行环境 | `handoff_thread` 可能中断执行并迁移 Git 状态；核对授权、源任务与目标宿主限制，按返回操作 ID 用 `get_handoff_status` 确认完成，无变化时退避 |

本地多目录项目的 Git 默认操作、AGENTS/技能/config 自动发现，以及 worktree/PR 操作以主目录或主仓为中心；次目录仍挂载，不能假设其规则已加载或写入已隔离。跨仓操作需逐仓核对。[项目文档](https://learn.chatgpt.com/docs/projects)

Local environments 复用项目脚本准备 worktree 与 Run/Test；`.worktreeinclude` 复制范围以宿主的受管 worktree 实现为准，不假定其他环境或手工创建的检出也会执行。[本地环境](https://learn.chatgpt.com/docs/environments/local-environment)、[Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)。支持 worktree 不等于每个任务默认创建 worktree；写入隔离仍须按实际执行环境核对。

同任务稍后续办或独立定时运行，须有后续工作请求并按当前工具契约执行；多项目与事件触发能力不跨端推定。先验证跟进提示与结果，再安排定时，明确通知及结束条件。[定时任务](https://learn.chatgpt.com/docs/automations)

异步澄清须当前会话提供相应工具，必要答案仍是依赖工作的前置条件。记忆只作线索，不替代契约、授权与证据。[记忆](https://learn.chatgpt.com/docs/customization/memories)

桌面端重启可能自动续办同账号近 24 小时内活跃且仍中断的本地会话。先确认原任务及其外部操作状态，再决定是否续办或补做；不据此推断 SSH 会话也已恢复。CLI 0.168 起，已打开或恢复的会话保留原模型提供方，变更新会话默认值不迁移旧会话。[客户端变更日志](https://learn.chatgpt.com/docs/changelog)

## 衡量是否提效

调整默认策略前，按影响选代表任务（如局部修复、跨模块交付、前端还原），固定输入、起点和验收标准；模型、推理强度、规则一次只改一项。先比验收结果，再比耗时、用量与返工。未做对照，不声称提效；不把评测设为日常任务门禁。

流程调优时优先使用可用的 `/usage` 等原生统计，结合任务耗时与验收质量抽样比较技能加载和委派收益；不为每个任务新建用量台账。视觉链路更新只复验受影响场景，见 [前端交付技能](../skills/refero-design-prompts/SKILL.md)；相关修复依据见 [API 更新日志](https://developers.openai.com/api/docs/changelog)。
