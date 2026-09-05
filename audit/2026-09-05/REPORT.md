# codex-config 审计报告

这是优化前基线的历史报告。后续修复、逐文件覆盖与验证状态见 [IMPLEMENTATION.md](IMPLEMENTATION.md)；本报告中的“未修改”等描述仅指第一轮审计。

审计日期：2026-09-05。基线：`9618e008c3cbb387d8894e27dca52ab55dc58a60`（2026-09-01）。本机 CLI：`0.153.3`。

结论：保留“可恢复配置、最小正确改动、证据交付、敏感信息保护”的骨架；优先修正安全扫描缺陷，删除强制线程分层和文字式完成门禁，把领域流程从全局注入移到按需技能。仅替换模型名称，不能解决当前主要问题。

本次交付是审计与候选文本，没有修改原有规范、安装配置、信任 hooks、提交或推送。候选总纲见 [global-guidance-candidate.md](global-guidance-candidate.md)，不作为生效入口。

## 范围与证据等级

- 逐段检查：全局及仓库 AGENTS、README、11 个 agent TOML、主/子代理 prompt、hooks、安装/还原/guard/secret scan/Git hooks、四个自维护 skill 入口、项目 AGENTS/plan/config 模板、执行和线程治理文档。
- 前端范围：审查自维护设计契约、技能路由、模板资产校验；没有逐一执行 74 个品牌参考或 19 个主页模板，也没有做第三方源码的完整安全/许可证审计。
- **复现**：运行原有 guard，并使用临时 Git 仓库和合成测试值验证额外缺陷；没有真实密钥和远程推送。
- **静态确认**：能由代码或规范直接确定的行为，但没有在真实配置目录执行安装。
- **建议**：基于当前官方文档、当前会话工具契约和维护成本的设计判断；未宣称通过模型 A/B 实验。
- 在线资料反映审计当日状态，不等于所有账号、客户端和受管工作区都已开放。本文单独标明当前会话工具限制，避免将其冒充通用产品规则。

## 优先级总表

P1：优先修复的安全或执行可靠性缺陷。P2：明显影响适配、效率或维护性的规则。P3：可渐进实施的优化。

| ID | 级别 | 问题 | 建议处置 | 证据 |
| --- | --- | --- | --- | --- |
| A01 | P1 | 待推送扫描跳过 merge 独有改动 | 修复历史遍历 | 已复现 |
| A02 | P1 | 新远程分支扫描错误排除其他远程历史 | 按目标远程计算或保守全扫 | 已复现 |
| A03 | P1 | 危险命令正则误拦文档、漏拦实际命令 | 缩小 hook 职责，修复解析与用例 | 已复现 |
| A04 | P2 | Stop/SubagentStop 用关键词与长度判断完成 | 删除语义硬阻断 | 已复现 |
| A05 | P2 | 所有实现默认新建用户可见功能任务 | 改为当前任务完成，独立任务显式选择 | 规范/工具冲突 |
| A06 | P2 | 授权后仍要求因联网、依赖、发布等再次停下 | 区分授权与技术权限 | 静态确认 |
| A07 | P2 | 全局注入领域架构与前端长清单 | 移入按需 skill | 计量/静态确认 |
| A08 | P2 | 项目模板重复全局治理，四层目标常态化 | 小模板默认、复杂治理可选 | 静态确认 |
| A09 | P2 | guard 强制口号原文，锁死过时策略 | 验结构与行为，移除词句断言 | 静态确认 |
| A10 | P2 | 模型矩阵停在 5.6，且硬禁 Spark | 更新可选路由，保留支持中的模型 | 官方文档 |
| A11 | P2 | 安装与 hooks 对自定义配置根目录不一致 | 统一路径发现并补集成测试 | 静态确认 |
| A12 | P2 | 整目录替换及“官方恢复”含义不准确 | 分项安装、清单回滚、默认预览 | 静态确认 |
| A13 | P2 | 本地 skill 安装路径缺少兼容说明 | 支持文档所列发现目录及插件分发 | 官方文档 |
| A14 | P2 | 自动化每次回报，与少打扰目标冲突 | 仅对可行动变化通知 | 规范/工具冲突 |
| A15 | P2 | 无原生 Goal、运行中纠偏的适配边界 | 补能力感知规则 | 官方文档/工具契约 |
| A16 | P3 | 11 个角色有重叠且覆盖内置 worker | 精简并说明覆盖作用域 | 官方文档/静态确认 |
| A17 | P3 | 全局前端美学禁令及双 token 真源 | 改成偏好，依从项目设计事实源 | 静态确认 |
| A18 | P3 | 验证四件套、压缩后全量重读、根目录噪音门禁 | 根据风险/变化选择 | 静态确认 |

## 关键缺陷与修正方向

### A01：merge 提交中的 secret 可以漏过历史扫描

位置：[secret-scan.py:161](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/scripts/secret-scan.py#L161)。`commit_paths()` 对合并提交执行普通 `git diff-tree -r`，没有指定合并差异策略，返回空路径。

触发：两个分支合并时新加入敏感值，再用后续提交删除，然后推送整段历史。当前工作区是干净的，普通扫描看不到已经删除的值；历史扫描也跳过引入值的 merge。

复现结果：直接扫描 merge 中的合成测试值得到 1 项；merge 路径列表为 `[]`；整段待推送历史得到 0 项。

修正：扫描所有待发送提交可达的新增 blob 并按对象 ID 去重；或明确实现 merge 相对父提交的完整差异遍历。补“merge 引入→随后删除”回归测试。不要只添加一个普通线性提交用例。

### A02：新分支推送不应排除所有远程

位置：[secret-scan.py:141](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/scripts/secret-scan.py#L141)、[pre-push](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/git-hooks/pre-push)。目标 ref 不存在时使用 `rev-list local_sha --not --remotes`，但 `--remotes` 包括与此次推送无关的所有远程。

触发：提交只存在于私有远程的本地 tracking ref，随后推到另一个新建的公开远程。代码误认为该提交不需要扫描。测试建立 `refs/remotes/private/main` 后确认该历史被排除。

修正：pre-push 传入目标 remote 信息，按目标远程可信的可达集合计算；无法确定时保守扫描本地目标 ref 的完整历史。补多远程、新分支、首次推送、远程 tracking ref 陈旧等用例。

### A03：危险命令匹配没有区分“代码”和“引用数据”

位置：[codex-policy-guard.py:23](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/hooks/codex-policy-guard.py#L23)、[249](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/hooks/codex-policy-guard.py#L249)。对整段命令或补丁全文先运行同一危险正则。

已复现：

| 输入 | 实际结果 | 问题 |
| --- | --- | --- |
| printf 打印危险命令的文档示例 | deny | 只打印文本也被阻断 |
| apply_patch 增加“不要使用危险命令”的文档 | deny | 补丁内容被当成执行代码 |
| `git checkout -- file.txt` | allow | `--` 后的 `\b` 无法匹配空格，漏拦原本声称保护的行为 |

修正：按工具类型解析。补丁只检查实际目标（包括重命名目标），不能按正文判断 shell 执行；shell 检查要区分参数、引号、重定向和语句边界。不要继续堆正则并声称覆盖任意解释器、MCP、UI 和嵌套调用。实际权限交由客户端沙箱、permission profiles、rules 和审批机制；hook 只补充高置信检查。

`CODEX_ALLOW_DESTRUCTIVE` 是进程环境开关，并不是能核验本次人工批准的凭据。不应把它作为全局通用授权协议。

### A04：删除 Stop/SubagentStop 的自然语言硬门禁

位置：[codex-policy-guard.py:321](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/hooks/codex-policy-guard.py#L321)、[348](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/hooks/codex-policy-guard.py#L348)。

| 最终文本 | 实际结果 |
| --- | --- |
| “尚未完成，需要你提供目标文件。” | 阻断，否定语义误报 |
| “已完成，测试以后再说。” | 放行，没有验证证据 |
| “结论：未发现问题。证据：目标测试通过。” | 子代理阻断，少于 30 字 |

这些规则同时诱发套话、无意义补测试和额外回合，不能证明质量。建议删除这两项硬阻断；保留“给出真实证据及未验证边界”的行为要求。提交边界运行确定性 guard。确需结构化门禁时，应绑定任务、变更版本、检查命令与退出状态，并明确适用任务，而不是检查一个关键词。

### A05–A06：消除“想自主，实际不断停下”的矛盾

位置：[AGENTS.md:58](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/AGENTS.md#L58)、[79](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/AGENTS.md#L79)、[83](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/AGENTS.md#L83)，以及线程治理、autonomous-project-execution、feature-thread-launch、project-AGENTS 和 plan 模板。

当前规定主任务不能承担真实实现，且普通修复也默认新建用户可见任务。这迫使代理先处理编排与交接，工具不允许时还可能停下。当前会话的 `create_thread` 明确只用于用户显式请求新任务；任务内部委派使用 subagent，并另受委派授权约束。该限制是本会话工具契约，不能用仓库偏好覆盖。

建议统一：相关工作在当前任务持续完成；只有用户要求独立任务时创建任务；子代理用于有边界且有净收益的独立子工作；需要隔离文件写入时使用 worktree。三层协作保留为用户主动选择的大项目模式。官方长期任务文档同样建议相关工作保留同一聊天，独立工作再分开。[长期任务](https://learn.chatgpt.com/docs/long-running-work)

“需要网络/外部服务/新增生产依赖/即将发布”不应自动意味着重新询问。先检查当前请求、已给授权和真实权限。明确授权的部署不重复确认；超范围的外部动作、真正的产品取舍和运行时权限升级才需要用户。依赖仍须有合理必要性与风险判断，不能变成无条件添加。

### A07–A09：规则下沉必须真的减少常驻上下文

实测：全局 AGENTS 305 行、9,305 bytes；SessionStart 注入的工作习惯 81 行、7,184 bytes；项目 AGENTS 模板 621 行、13,582 bytes。前两者若同时启用就有 16,489 bytes；再完整采用模板为 30,071 bytes。这是 UTF-8 字节统计，不是 token 计数，也不代表所有文档都会自动加载。

把规则从 AGENTS 搬到每次启动/恢复/压缩都注入的 prompt，没有实现按需加载。尤其系统架构与前端流程对非代码工作无关。`additionalContextLimit=8000` 只是输出阈值，不是严格 8000 token 的成本上限。官方要求避免多个 hooks/plugins 的上下文累积；当前格式本身仍有效。[Hooks](https://learn.chatgpt.com/docs/hooks)

建议：全局只保留语言、授权、范围、工具诚实性、验证与交付；架构流程留在自主开发技能，前端规则留在设计技能。项目模板默认 50–100 行、只填实际命令与约束；这是维护目标，不是官方限制。四层目标、goal delta、线程总表、五件套文档仅用于真正需要的长期项目。

guard 的大量 `require_text` 把“统一领域模型”“Motion Gate”等原话当成正确性条件，会阻止正常精简。删去口号断言，保留引用存在性、可解析结构、合法值、行为回归、文件清单和 secret 扫描。前端快照 commit 与数量可用于固定版本完整性检查，但不能替代内容哈希或行为验证。

官方仍支持 AGENTS 层级和同目录 override；不要删除本仓库 override。官方提到默认项目文档加载上限，但不能把这个上限解释成推荐把规则写满。[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

### A10：更新模型策略，取消按代际硬封禁

位置：[orchestrator.toml:31](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/agents/orchestrator.toml#L31)、其他 agent TOML、总览和角色矩阵、[guard:304](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/scripts/codex-config-guard.sh#L304)。

审计日官方推荐包含 `gpt-6-astra`；5.6 Sol/Terra/Luna 仍在模型列表中。不能称 5.6 已淘汰，也不能因为 5.3 Spark 名称较旧就判定不可用。当前会话模型列表也仍列出 Spark。[模型列表](https://learn.chatgpt.com/docs/models)

建议路由：高难跨系统实现、架构和重要复核可选 Astra；常规工作保留 Sol/Terra；明确的轻量任务保留 Luna，Spark 只在客户端提供且符合任务条件时选择。不要在 AGENTS 写永久版本号；在配置与带日期的兼容说明中维护。未指定模型时优先尊重用户当前选择，避免技能静默降档。

不要武断认定“强模型用于实现就是浪费”。比较整项任务的完成质量、耗时、重试、交接和费用，不能只看单 token 价格。需要以代表性任务测试选型，而非把所有文件批量替换成 Astra。

Astra 官方提示特别强调：更敏感地遵循规则、可能多问问题、可能过度验证。因此本仓库最该适配的是冲突指令、授权继承和验证规模。API 的异步工具调用或推理参数不应直接写进桌面 AGENTS，运行机制由实际客户端工具提供。[当前模型指导](https://developers.openai.com/api/docs/guides/latest-model)

### A11–A13：安装层需要产品适配与清晰所有权

1. **配置根目录不一致**：安装脚本支持自定义 `CODEX_HOME`，hooks.json 却硬编码 `$HOME/.codex/hooks/...`，Python live 路径保护也使用 `Path.home()/.codex`。隔离配置可能调用真实 home 中另一份 hook，或漏保护实际入口。现有 roundtrip 只验证链接，不执行安装后的 hook 命令。应统一配置根目录解析，并在隔离环境执行入口验证。
2. **整目录替换会停用其他配置**：[安装脚本:75](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/scripts/restore-codex-global-links.sh#L75) 备份后替换整个 agents/prompts/docs/hooks 目录及 hooks.json。备份保护原文件，但安装期间其他 agent/hook 不再位于原入口。建议按项目拥有的文件安装，冲突明确处理；hook 配置采用受控合并或独立可组合入口。
3. **恢复名义大于实际保证**：[还原脚本:23](https://github.com/winds18/codex-config/blob/9618e008c3cbb387d8894e27dca52ab55dc58a60/scripts/restore-codex-official-state.sh#L23) 无参数默认 apply；恢复的是最新匹配备份，可能本就是其他自定义状态。建议改称“卸载本配置/恢复安装前状态”，默认 dry-run，以安装清单关联精确备份；补中途失败、重复安装、仓库迁移、既有断链等测试。现有单轮恢复测试值得保留。
4. **skill 发现路径**：当前官方本地编写说明列出 `~/.agents/skills` 和项目 `.agents/skills`；仓库只安装到 `~/.codex/skills`。本会话确实加载了 `.codex/skills` 技能，因此不能断言旧路径已经失效。应标注并实测目标客户端的发现路径，避免双目录导致重复技能；跨设备复用可将四个技能做成可选插件分发。[Build skills](https://learn.chatgpt.com/docs/build-skills)

不要在审计过程中运行真实安装来“证明兼容”。应先增加 doctor：检查 CLI 版本、Git/Python/rg、文件发现、配置 schema、权限能力和 hook 信任状态，再由用户选择安装配置档。

### A14–A15：接入当前 ChatGPT 工作流，而非所有工作都套开发流程

当前全局定位只覆盖软件开发；ChatGPT Work 还可能进行网页研究、文档、表格、演示、连接应用操作。建议补充能力路由原则，而不是每种产品增加一整章流程。技能/插件承担专项工作，连接器/API/CLI 和 UI 工具按实际可用能力选择；外部检索内容作为资料，不自动成为执行指令。[Skills & Plugins](https://learn.chatgpt.com/docs/skills-and-plugins)

- **Goal**：文档里的 Working Goal 与原生 Goal 状态不是同一件事。用户显式要求长期目标时使用当前客户端 Goal 能力；普通审计、修复不要自动创建 Goal，不虚构预算。用户中途补充要求时继续原目标，除非明确取消或替换。[长期任务](https://learn.chatgpt.com/docs/long-running-work)
- **自动化**：删除 AGENTS 第 266 行“每次运行结束必须报告”式通知要求。运行证据可以留存，但监控无变化时静默；有重要变化、完成、失败或需要用户行动时通知。当前工具优先同任务 heartbeat；独立运行需独立任务语义，不能仅凭“周期性”选择 cron。
- **客户端区别**：桌面本地定时工作需要电脑和应用运行；网页任务不能直接操作本机目录；CLI/IDE 没有 Scheduled 管理界面。网页/移动端的部分事件触发功能不应写成桌面已有能力。[Scheduled tasks](https://learn.chatgpt.com/docs/automations)
- **状态管理**：新任务创建、handoff、归档、自动化和通知设置使用当前工具返回的 ID 与状态，不把文档线程表当作实时事实源。保留关键交付记录即可。

### A16–A18：可进一步删除或放宽的条款

| 原规则 | 处置 | 理由 |
| --- | --- | --- |
| 主线程不做实际开发 | 删除默认硬约束 | 相关工作可在同任务完成 |
| 若只能顺序开发，说明抽象不足 | 删除 | 数据依赖、迁移、排障等存在合理串行步骤 |
| 先建立统一抽象层/统一执行管线 | 改为有证据再抽象 | 避免为并行而制造架构 |
| 主任务每轮注入完整前端规范 | 移到前端技能 | 减少无关约束 |
| 禁止通用居中、scale(0)、ease-in 等一切用法 | 改为偏好及适用条件 | 参考还原、离场动效等可能有合理用途 |
| DESIGN.md 永远是唯一 token 真源 | 依项目选择 | Figma variables、CSS/Tailwind token 可能已是权威来源；文档应引用或生成 |
| 每个阶段测试+lint+build+smoke | 按改动选择 | 文档、配置、服务端、UI 的证据不同 |
| 压缩后总是重新读 AGENTS/spec/plan | 仅恢复缺失或陈旧证据 | 避免重复加载与丢失当前进展 |
| 完成必须给出下一步 | 按需 | 目标已达成时不制造新任务 |
| 根目录 .DS_Store/日志存在就阻断提交 | 默认 warning | 未暂存且被忽略的本机文件不影响提交内容 |
| 所有项目注释/docstring/提交说明都中文 | 中文答复保留，仓库内容随项目 | 尊重开源仓库已有语言和贡献约定 |

11 个 agent 的摘要/规划/收尾职责可合并为 4–6 个按需角色；不必默认每阶段派全套。`worker` 会覆盖同名内置 agent，应明确这是个人选择。独立 agent TOML 的 `name`、`description`、`developer_instructions` 以及模型/沙箱字段仍受支持，不能按旧知识迁回过时结构。[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## 应保留的资产

- 不覆盖用户已有改动；范围清晰、最小正确改动；发布与外部动作的授权边界。
- 可恢复软连接、安装前备份、仓库专用 override，不静默信任 hooks。
- 真实验证证据、诚实说明未验证项、发现问题优先的审查格式。
- Git 暂存内容和待推送历史扫描的总体方向，但必须修复 A01/A02。
- 子代理的明确边界、主任务复核结论、共享文件避免冲突。
- 项目实际需要时的 worktree、计划和架构记录。
- 前端渲染验收、响应式、可访问性、reduced motion、真实资源检查和模板来源记录。
- `.codex/config.toml` 的最小权限思路。当前官方仍有 `default_permissions` 配置；应校验目标版本和管理策略，不应凭“看起来陌生”删除。[配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)

## 落地次序与验收

1. **先修缺陷**：A01/A02/A03 补失败用例再修复；撤掉 A04 的自然语言阻断。验收：误报样例放行、实际违规样例阻断、合并及多远程历史检出，原有有效测试继续通过。
2. **再精简规则**：按候选总纲更新 AGENTS；同步删除 prompt、skill、项目模板和 docs 中冲突条款，调整 guard。不能只改一处让旧 hook 又注入回来。
3. **再适配安装**：doctor、选择性安装、路径兼容、精确回滚清单；在临时目录完成自定义配置根、外来 agent/hook、迁移与恢复验证。
4. **最后做模型与产品实测**：用小修复、跨文件实现、研究报告、前端参考还原、权限受阻、长期纠偏六类任务做 A/B；记录完成质量、追问次数、无效工具调用、重复检查、耗时和可获得的实际用量。不要把减少行数当成效果已经提升。

建议先测“原模型+精简规范”，再测“候选模型+同一精简规范”，以免把规则和模型两个变量混在一起。

## 已运行验证与限制

`bash scripts/codex-config-guard.sh`：退出码 0。包含敏感信息扫描、lifecycle hook 策略测试、模板资产检查、恢复回环、secret scan 用例、工作区清洁检查。

新增边界复现见 [reproduce.py](reproduce.py)，运行 `python3 audit/2026-09-05/reproduce.py`。测试仅在临时仓库执行 Git 操作，hook 危险字符串只作为函数输入，不执行危险命令。结果保存于 [reproduction-results.json](reproduction-results.json)。

“原有测试通过”与“配置不存在缺陷”不是同义词。本次没有实际加载安装后的 hooks、调用全部自定义 agent、验证账号级模型权限、运行网页/桌面自动化，也没有证明候选规范已经改善模型指标。上述属于实施后的验收事项。
