# 客户端与模型适配

基线核实：2026-09-05，macOS / Codex CLI 0.153.3；跨项目与任务能力于 2026-09-08 复核，本机 CLI 已为 0.153.4。配置可用性仍取决于实际客户端、账号与受管策略；本仓库不替用户切换账号或更改模型权限。

## 模型路由

主任务、worker、orchestrator、planner 和深度安全复核默认继承宿主模型/推理设置，避免把高难实现静默降档。轻量探索/总结保留 Luna，常规首轮复核和整理保留 Terra 的可选角色；不是每轮必须使用的固定团队。

当前官方列出 Astra 与 5.6 系列；Astra 适合复杂工作，但有分阶段开放信息。需要显式选型时先查看当前客户端可用列表；能用时再选，不因名称新旧硬禁仍支持的模型。`gpt-5.3-codex-spark` 不再被仓库 guard 按代际禁止。[官方模型](https://learn.chatgpt.com/docs/models)

Astra 的改进重点体现在主动跟进、规则敏感性、并行委派和适度验证。本仓库通过明确并行启动条件、授权继承和停止重复检查来适配；不能保证对任意任务都有固定比例提速。[模型指导](https://developers.openai.com/api/docs/guides/latest-model)

角色 TOML 仍使用 name、description、developer_instructions。自定义 worker 与内置同名角色有覆盖关系，只有安装本角色后才生效；不想覆盖时不安装该项或另取名称。[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## 技能与配置入口

官方本地编写文档列出 `~/.agents/skills`、项目 `.agents/skills`；当前本机也实际加载 `.codex/skills`。保留默认兼容入口，按目标宿主选择安装目录，不同时安装同名技能到多个发现位置。[技能发现](https://learn.chatgpt.com/docs/build-skills)

AGENTS 层级和同目录 override 仍有效；本仓库 override 只用于维护，不能装到用户全局。项目权限模板仅在宿主支持且不违背受管策略时采用。[AGENTS](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)

## 工具与生命周期

- 子代理适合任务内部独立工作；新用户任务需要对应用户请求，按当前工具契约创建和等待。
- 原生 Goal 只在显式请求时建立；普通复杂开发可用短计划，无需额外 Goal。运行中补充要求继续当前工作。[长期工作](https://learn.chatgpt.com/docs/long-running-work)
- 自动化仅在用户要求后续工作时建立；同任务跟进优先当前上下文，独立运行按独立任务处理。无变化静默，通知策略用工具字段保存。
- 桌面定时本地工作要求应用/电脑运行；网页工作不能直接读取本机目录。网页/移动事件触发不能视为桌面已有能力。[Scheduled tasks](https://learn.chatgpt.com/docs/automations)
- Hooks 的 Bash matcher 也覆盖 unified exec；apply_patch 有 Edit/Write aliases。PreToolUse 的 ask 尚不支持，不能当成审批实现。自定义 hook 是额外检查，不能替代客户端权限。[Hooks](https://learn.chatgpt.com/docs/hooks)
- 外部软件、浏览器、文档/表格等任务按实际插件和工具执行，技能说明按需读取，不复制完整产品工具手册。

## 跨项目与任务工具

工程流程统一维护在 [跨项目与既有任务统筹](../skills/autonomous-project-execution/references/autonomous-execution-workflow.md#跨项目与既有任务统筹)。下列工具是 2026-09-08 根任务提供的桌面接口，子代理、CLI 或其他客户端不保证相同；先看当前契约，不把工具名或参数上限写成全局要求。

| 用途 | 当前接口与关键边界 |
| --- | --- |
| 查找/读取既有工作 | `list_projects`、`list_threads`、`read_thread`；按返回 ID、宿主和项目定位，先摘要后必要历史，动态状态不另建台账 |
| 续接/等待 | `send_message_to_thread` 会形成用户可见提示并触发执行；按已有授权发送增量。`wait_threads` 优先游标/事件，当前最多 8 个目标，`timeoutMs: 0` 适合即时快照；等待中继续独立工作，不循环回读全历史 |
| 创建/分叉 | `create_thread` 需明确新任务请求，先查项目；Git 项目默认 worktree，遵从用户明确起点。异步 `clientThreadId` 不是就绪 `threadId`，先定位真实任务再供后续工具使用。`fork_thread` 仅复制已完成历史，不包含运行中的本轮及未完成回答 |
| 移动执行环境 | `handoff_thread` 移动其他任务及 Git 状态并中断其运行；不能移动调用任务自己，当前不支持 cloud handoff。按返回 operationId 用 `get_handoff_status` 确认完成，无变化时退避；可选宿主以实际列表为准 |

本地多目录项目的 Git 默认操作、AGENTS/技能/config 自动发现，以及 worktree/PR 操作以主目录或主仓为中心；次目录仍挂载，不能假设其规则已加载或写入已隔离。跨仓操作需逐仓核对。[项目文档](https://learn.chatgpt.com/docs/projects)

Local environments 可复用 worktree 初始化与 Run/Test 等 Actions；配置放所属项目，调用已有脚本并按实际需要准备依赖。`.worktreeinclude` 的忽略文件复制适用于本地受管 worktree，远程或手工 worktree 不应推定相同。[本地环境](https://learn.chatgpt.com/docs/environments/local-environment)、[Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)

需要同任务稍后续办时，按后续工作请求使用 `automation_update` 的 heartbeat；独立定时运行依工具契约。公开文档的多项目定时和网页/移动事件触发，不代表当前桌面创建接口提供同样参数；本轮 cron 接口仅有单个 projectId。可用时先用普通任务验证跟进提示与结果，再安排定时，通知及结束条件明确。[定时任务](https://learn.chatgpt.com/docs/automations)

异步澄清只在当前会话确实提供相应工具时使用；必要答案仍是依赖工作的前置条件。记忆用于召回线索，不能替代当前契约、授权和验证证据；实验性上下文管理不作为必需工具或默认安装项。[变更日志](https://learn.chatgpt.com/docs/changelog)、[记忆](https://learn.chatgpt.com/docs/customization/memories)

## 衡量是否提效

先固定模型比较旧/新规则，再固定规则比较可用模型。选单文件修复、跨模块实现、前端还原、非代码交付、真实权限受阻、长任务中途纠偏六种代表任务。

记录完成质量、耗时、实际追问、重复工具/测试、并行重叠和可获取的用量；失败的工作不能仅因速度快就胜出。字节减少和静态检查通过只证明规则负担与一致性，不能代替行为评估。
