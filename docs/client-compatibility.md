# 客户端与模型适配

可用性取决于客户端、账号、当前工具契约与受管策略；本文不触发安装、模型切换或实验 feature 启用。

## 模型路由

主任务保持用户所选模型；子代理默认按根主任务低一能力档动态选型，不固定型号。判断依据、同档例外、旧角色锁定与不可用时的处理统一见 [角色与模型选择](../skills/autonomous-project-execution/references/agent-role-matrix.md)。

显式选型以客户端可用列表为准，不按代际禁用仍支持的模型。[官方模型](https://learn.chatgpt.com/docs/models)

异步工具、mid-turn steering 与 `configuration_update` 是 API 能力，不代表所有桌面工具可用；客户端执行、等待和中途纠偏仍按当前契约，不能据此改机器配置或推定提速。[模型指导](https://developers.openai.com/api/docs/guides/latest-model)

角色 TOML 使用 `name`、`description`、`developer_instructions`，可选 `model`、`model_reasoning_effort`。模型/推理配置按角色文件、显式创建参数、`[agents]` 默认、父任务的优先级解析；创建参数或 `[agents]` 显式选模型且未配置推理强度时，采用所选模型默认值。当前文档未提供原生“次一级”参数，须由编排者选择实际模型。自定义角色与内置角色同名会覆盖后者。[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## 技能与配置入口

本地技能入口包括 `~/.agents/skills`、项目 `.agents/skills`；`.codex/skills` 兼容入口按宿主实际发现情况使用，不重复安装同名技能。[技能发现](https://learn.chatgpt.com/docs/build-skills)

AGENTS 层级和同目录 override 仍有效；本仓库 override 只用于维护，不能装到用户全局。项目权限模板仅在宿主支持且不违背受管策略时采用。[AGENTS](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)

支持的客户端可在既有会话刷新插件工具、技能与 hooks，不等于任意 AGENTS 或角色配置自动热刷新。本地规则更新可显式重读适用文件并保留目标、成果和授权；实际发现结果仍需确认，hook 信任仍由用户审查。仅在刷新未生效或宿主要求时重建会话。[变更日志](https://learn.chatgpt.com/docs/changelog)

## 工具与生命周期

- 子代理适合任务内部独立工作；新用户任务需要对应用户请求，按当前工具契约创建和等待。
- 原生 Goal 只在显式请求时建立，运行中补充要求继续当前工作。[长期工作](https://learn.chatgpt.com/docs/long-running-work)。自动化须有后续工作请求，同任务跟进优先当前上下文，独立运行按独立任务处理；无变化静默，通知策略用工具字段保存。
- 桌面定时本地工作要求应用/电脑运行；网页工作不能直接读取本机目录。网页/移动事件触发不能视为桌面已有能力。[Scheduled tasks](https://learn.chatgpt.com/docs/automations)
- [官方 Hooks](https://learn.chatgpt.com/docs/hooks) 支持 MCP 拦截、PermissionRequest/Interrupt；本仓库仅分发 PreToolUse。其 ask 不作审批实现，hook 不替代客户端权限，见 [Hooks 与验证边界](hook-enforcement-policy.md)。
- 按需发现工具/插件并读取相关技能，先利用已提供能力；确认缺失才回退到其他获授权方式，不把发现入口当成安装或信任授权。
- MCP OAuth 恢复不自动重放已拒工具调用；重试先核对授权与执行状态。

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

Local environments 复用项目脚本准备 worktree 与 Run/Test；`.worktreeinclude` 复制适用于本地受管 worktree，不外推到远程或手工创建。[本地环境](https://learn.chatgpt.com/docs/environments/local-environment)、[Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)。支持 worktree 不等于每个任务默认创建 worktree；写入隔离仍须按实际执行环境核对。

同任务稍后续办或独立定时运行，须有后续工作请求并按当前工具契约执行；多项目与事件触发能力不跨端推定。先验证跟进提示与结果，再安排定时，明确通知及结束条件。[定时任务](https://learn.chatgpt.com/docs/automations)

异步澄清须当前会话提供相应工具，必要答案仍是依赖工作的前置条件。记忆只作线索，不替代契约、授权与证据。[记忆](https://learn.chatgpt.com/docs/customization/memories)

## 版本核验（2026-09-29）

本机 macOS 实测：PATH 中 `codex` 为 0.149.1；桌面内置 `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex` 为 0.158.0-alpha.2.1。桌面 alpha 版本不等于正式版能力，且不能外推到 PATH CLI 或其他客户端。

[官方变更日志](https://learn.chatgpt.com/docs/changelog)：0.156.0 默认启用 worktree 支持，不代表每个任务默认创建 worktree；`/usage` 提供用量及插件、技能统计。0.157.0 会在合适的交互会话中自动共享后台服务，不能据此推定所有会话或跨端共享；资源归属与回收仍按实际会话核对。

## 衡量是否提效

技能描述简短准确、参考按需读取，避免全仓必读与小改全套测试。[9/11 官方指导](https://learn.chatgpt.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)。固定模型比较规则，再固定规则比较模型；覆盖局部修复、跨模块、前端、非代码、权限受阻与长任务纠偏。记录质量、耗时、追问、重复检查、并行及用量；失败不能凭速度胜出，静态检查不替代行为评估。

流程调优时优先使用可用的 `/usage` 等原生统计，结合任务耗时与验收质量抽样比较技能加载和委派收益；不为每个任务新建用量台账。视觉链路更新只复验受影响场景，见 [前端交付技能](../skills/refero-design-prompts/SKILL.md)；相关修复依据见 [API 更新日志](https://developers.openai.com/api/docs/changelog)。
