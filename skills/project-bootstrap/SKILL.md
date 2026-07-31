---
name: project-bootstrap
description: 新项目初始化 skill，用于在正式写业务代码前生成项目级 AGENTS、README、spec、plan 和 changelog，并建立 goal-first 执行结构。
---

# Project Bootstrap

## 概览

这个 skill 用于把全局 Codex 工作规则展开成具体项目的初始化结构。

它适用于新项目启动，不适用于已经结构化仓库里的普通功能开发。

## 适用场景

适合使用：

- 新项目从空目录或接近空目录开始
- 用户希望 Codex 在正式编码前先初始化仓库结构
- 项目需要采用 goal-first 执行方式
- 项目需要支持自主推进或低打扰开发

不适合使用：

- 仓库已经有成熟的项目级 `AGENTS.md`
- 当前任务只是给已有项目增加一个功能
- 用户只想讨论想法，而不是实际初始化项目

## 必要产物

最小项目初始化产物包括：

- `AGENTS.md`
- `README.md`
- `docs/spec.md`
- `docs/plan.md`
- `CHANGELOG.md`

只有在确实能减少歧义或提升自动化时，才补充 `.codex/` 文件。

## 工作流程

1. 读取 `~/.codex/AGENTS.md` 中的全局工作规则。
2. 理解项目 Mission、Constraints、技术栈和明确不做的范围。
3. 创建或更新最小项目文档集合。
4. 把全局理念转化为仓库内具体、可执行的规则。
5. 保持项目文档具体、简洁、贴近仓库现实。
6. 在项目文档层建立前，不进入大规模业务实现。

## 基本规则

- 不要把整份全局 `AGENTS.md` 复制进项目仓库。
- 项目级 `AGENTS.md` 必须贴近真实命令、真实风险和本地约束。
- Mission 和范围写入 `docs/spec.md`。
- Working Goal 和阶段顺序写入 `docs/plan.md`。
- 必须明确无人值守执行边界。
- 如果项目面向无人值守开发，必须写清 Codex 何时必须暂停并询问用户。

## 参考资料

仅在需要时读取：

- `../../docs/project-expansion-workflow.md`
  用于查看详细初始化流程和文件职责。
- `../../docs/project-AGENTS-template.md`
  用于起草项目级 `AGENTS.md`。
- `../../docs/project-codex-config-template.md`
  仅在项目需要 `.codex/config.toml`、权限 glob 或敏感路径 deny 规则时读取。

## 预期结果

使用该 skill 后，仓库应具备：

- 清晰的项目入口文档
- 项目级操作契约
- goal-first 计划文档
- 最小 changelog
- 明确的下一阶段实现目标

如果这些内容缺失，说明项目初始化还不完整。
