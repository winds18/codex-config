# 客户端与模型适配

核实日期：2026-09-05。本次测试主机：macOS，Codex CLI 0.153.3。配置可用性仍取决于实际客户端、账号与受管策略；本仓库不替用户切换账号或更改模型权限。

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

## 衡量是否提效

先固定模型比较旧/新规则，再固定规则比较可用模型。选单文件修复、跨模块实现、前端还原、非代码交付、真实权限受阻、长任务中途纠偏六种代表任务。

记录完成质量、耗时、实际追问、重复工具/测试、并行重叠和可获取的用量；失败的工作不能仅因速度快就胜出。字节减少和静态检查通过只证明规则负担与一致性，不能代替行为评估。
