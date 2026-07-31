# Codex 全局体系总览

这份文档用于说明当前这套 Codex 全局配置体系的结构、用途、恢复方式和日常使用方式。

目标：

- 让整个系统有一个清晰总览
- 让后续维护只需要改少数几个真源文件
- 让恢复、回滚、继续扩展都有明确入口

---

## 1. 总体设计思路

当前采用的是：

- `单一真源目录`
- `~/.codex` 软连接入口
- `全局总纲 + skill + agent + prompt + docs + hooks` 分层结构

也就是说：

- 真正维护的源文件统一放在一个稳定目录里
- `~/.codex` 只作为 Codex 读取入口
- 后续只需要修改真源文件，不直接手改一堆入口副本

---

## 2. 真源目录

默认真源目录就是当前仓库根目录。

路径示例：

`/path/to/codex-config`

两个恢复脚本默认会根据自身所在位置自动推导这个目录，因此仓库 clone 到其他路径也可以直接工作。

这是整套体系的唯一主维护目录。

只要这里的内容更新，重新挂载或新会话后，Codex 入口就会随之反映更新。

---

## 3. `~/.codex` 生效入口

当前已挂载的入口包括：

- `~/.codex/AGENTS.md`
- `~/.codex/agents`
- `~/.codex/prompts`
- `~/.codex/docs`
- `~/.codex/hooks.json`
- `~/.codex/hooks`
- `~/.codex/restore-global-setup.sh`
- `~/.codex/restore-official-state.sh`
- `~/.codex/skills/project-bootstrap`
- `~/.codex/skills/autonomous-project-execution`
- `~/.codex/skills/feature-thread-launch`
- `~/.codex/skills/refero-design-system`

这些入口大多是软连接，指向真源目录。

目的不是为了复制内容，而是为了让：

- 日常维护只改一处
- 入口始终一致
- 需要恢复时可以一键重建

---

## 4. 当前目录结构

真源目录中当前包含：

| 路径 | 职责 |
| --- | --- |
| `README.md` | 仓库级入口，负责新设备部署、恢复和最短校验路径。 |
| `AGENTS.md` | 全局总纲，定义 goal-first、少打扰、线程治理、验证和提交边界。 |
| `agents/` | 全局代理角色，负责主编排、执行、审查、测试、总结等分工。 |
| `skills/` | 全局可复用工作流，包括项目初始化、无人值守执行和功能线程启动。 |
| `prompts/` | 轻量 prompt 入口，长期优先级低于 skill。 |
| `docs/` | 模板、展开流程、线程治理、hook 策略、Git 策略和恢复说明。 |
| `hooks/` | Codex lifecycle hooks 与运行时策略脚本。 |
| `git-hooks/` | Git hook 模板，通过 `core.hooksPath` 激活。 |
| `scripts/` | 恢复、官方还原、guard 和 Git hooks 安装脚本。 |

详细职责以各目录内文档和脚本为准；本节只保留总览索引，避免同一规则在多处重复维护。

---

## 5. Hook 守门层

这套体系把关键规范分成三层落实：

- Codex lifecycle hooks：运行时阻断高风险动作
- 仓库 guard：检查确定性文件、脚本、模板同步状态
- Git hooks：在 commit / push 前自动运行 guard
- Git 工作流策略：定义分支、提交、hook 安装、版本发布与构建产物边界

当前仓库 guard 命令：

```bash
bash scripts/codex-config-guard.sh
```

设计边界：

- 高置信、低误伤、后果明确的节点才硬阻断
- 语义判断仍由主编排者和验收流程负责
- 不用 hook 把整个开发流程变成重型审批系统

---

## 6. 两条恢复线

这是整套体系里最重要的运维设计之一。

你现在有两条完全独立的恢复路径：

### 路径 A：恢复这套自定义全局体系

首次安装或新设备首次接管：

```bash
bash /path/to/codex-config/scripts/restore-codex-global-links.sh
```

已挂载后的一键恢复命令：

```bash
bash ~/.codex/restore-global-setup.sh
```

用途：

- 软连接丢失
- 更换机器或环境
- 入口损坏
- 需要重新挂载整套自定义结构

它会恢复：

- `~/.codex/AGENTS.md`
- `~/.codex/agents`
- `~/.codex/prompts`
- `~/.codex/docs`
- `~/.codex/hooks.json`
- `~/.codex/hooks`
- `~/.codex/skills/project-bootstrap`
- `~/.codex/skills/autonomous-project-execution`
- `~/.codex/skills/feature-thread-launch`
- `~/.codex/skills/refero-design-system`

---

### 路径 B：恢复官方原版 / 修改前状态

预览：

```bash
bash ~/.codex/restore-official-state.sh --dry-run
```

执行：

```bash
bash ~/.codex/restore-official-state.sh --apply
```

用途：

- 不想继续使用这套自定义全局体系
- 希望撤销我加进去的 `.codex` 全局入口
- 希望回到尽量接近修改前的 `~/.codex` 状态

它会：

- 删除我挂进去的相关软连接
- 恢复安装前保存的原文件、目录或非本仓库软连接
- 删除我挂到 `~/.codex/skills/` 的个人 skill 入口
- 删除我挂到 `~/.codex` 的 hooks 入口

它不会：

- 删除你的原有官方目录
- 删除你的 `config.toml`
- 删除你的 `rules/`
- 删除你的 `plugins/`
- 删除真源目录本身

---

## 7. 日常维护原则

后续维护时，优先遵守下面这些规则：

1. 不要直接手改 `~/.codex` 里的软连接入口内容
2. 优先修改真源目录中的文件
3. 如果入口损坏，优先用恢复脚本修复
4. 新增规则时，先判断属于：
   - 全局总纲
   - skill
   - agent
   - prompt
   - docs
   - hooks
5. 不要把所有内容都塞进 `AGENTS.md`

---

## 8. 如何判断内容该放哪里

### 放进 `AGENTS.md`

适合：

- 长期稳定的全局行为规则
- goal-first 规则
- 无人值守边界
- 少打扰策略
- 总体工作哲学

不适合：

- 项目特定命令
- 一次性执行步骤
- 太长的模板

---

### 放进 `skills/`

适合：

- 某一类可复用工作流
- 有明确触发条件的流程能力
- 想让 Codex 在新会话中主动发现和使用的能力

例如：

- 新项目初始化
- 无人值守执行阶段
- 功能线程轻量启动与交接

---

### 放进 `agents/`

适合：

- 角色边界清晰的代理
- 需要专门模型策略或职责边界的角色
- 想显式分工的子代理

---

### 放进 `prompts/`

适合：

- 临时或轻量的一键启动入口
- 你明确知道要手动调用的 prompt

注意：

- 官方当前更推荐 skill

---

### 放进 `docs/`

适合：

- 模板
- 流程说明
- 运维说明
- 参考手册

---

### 放进 `hooks/`

适合：

- 高置信 secret 阻断
- 明显危险命令阻断
- live `~/.codex` 入口写入阻断
- 完成声明前的验证提醒

不适合：

- 判断产品意图
- 判断功能线程是否语义完成
- 代替 goal 纠偏
- 代替主线程验收

---

## 9. 推荐使用方式

### 新项目开始

推荐顺序：

1. 让 Codex 读取全局 `AGENTS.md`
2. 使用 `project-bootstrap`
3. 生成项目级：
   - `AGENTS.md`
   - `README.md`
   - `docs/spec.md`
   - `docs/plan.md`
   - `CHANGELOG.md`
4. 补项目级 `.codex/` 配置
5. 再进入实际实现阶段

### 项目进入实现期

推荐顺序：

1. 主线程保持为项目控制面线程
2. 切到 `autonomous-project-execution`
3. 用 `orchestrator` 控方向
4. 用 `planner` 补计划与线程总表
5. 具体功能开发一律用 `feature-thread-launch` 下沉到新功能线程，优先放进 worktree
6. 用 `worker` 在功能线程中主实现
7. 功能线程内部尽量优先用 spark 子代理承担探索、总结、测试归因、轻量 review
8. 按“框架 / 主路径优先，细节 / 修饰后置”的顺序推进
9. 功能线程完成后回主线程验收
10. 验收通过后合并并归档功能线程

---

## 10. 推荐的模型分工

当前建议：

- `orchestrator`：强模型
- `planner`：强模型
- `worker`：中高能力模型
- `security-reviewer`：强模型
- `explorer-spark`：spark
- `reviewer-lite-spark`：spark
- `tester-lite-spark`：spark
- `security-lite-spark`：spark
- `summarizer-spark`：spark
- `refiner`：中等模型
- `pr-preparer`：中等模型

原则是：

- 符合条件的读多写少任务默认明确选择 `-spark` 角色，稳定消耗独立 spark 额度
- 功能线程主执行者选择足够完成任务的性价比模型
- 强模型优先保留给方向、复杂判断和高风险复核

---

## 11. 当前体系的边界

这套体系目前已经具备：

- 全局总纲
- 项目初始化 skill
- 执行期 skill
- 角色矩阵
- 主线程 / 功能线程治理规则
- 轻量功能线程启动 skill
- Hook 守门层
- 快速 prompt
- 文档模板
- 双恢复路径

它还没有完全覆盖的方向包括：

- 更细的项目级 `.codex/config.toml` 自动生成
- 针对特定技术栈的 agent 变体
- 更完整的自动 PR / 发布流水线
- 更细粒度的技能验证体系

这些后续都可以继续加，但当前已经足够作为长期主骨架使用。

---

## 12. 一句话总结

这套体系的本质是：

`用一个稳定的全局真源目录，驱动 ~/.codex 的可恢复入口，把 Codex 从普通对话助手升级为可编排、可恢复、可无人值守推进的软件开发系统。`
