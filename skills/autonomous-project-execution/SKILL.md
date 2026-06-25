---
name: autonomous-project-execution
description: 自主项目执行 skill，用于在项目已有基础文档后，让 Codex 以 goal 驱动、低打扰、阶段验证和可控纠偏的方式持续推进。
---

# Autonomous Project Execution

## 概览

这个 skill 用于项目初始化之后，让 Codex 从“搭建结构”进入“持续实现”。

它适合低打扰、goal 驱动、跨阶段推进的执行场景。

## 适用场景

适合使用：

- 仓库已经有项目级 `AGENTS.md`
- 项目至少已有 `docs/spec.md` 和 `docs/plan.md`
- 用户希望 Codex 持续推动实现
- 工作流需要支持无人值守或轻监督执行

不适合使用：

- 项目尚未完成初始化
- 用户仍在定义项目核心形态
- 当前只是一次性小修复，不需要持续编排

## 前置条件

使用该 skill 前，项目应已经具备：

- 仓库级操作规则
- 项目 Mission 和范围
- 当前工作计划
- 已知验证路径

如果这些内容缺失，应先使用 `project-bootstrap`。

## 执行模型

主线程应作为主编排者。

主线程需要：

1. 读取 Mission 和 Constraints
2. 读取或细化当前 Working Goal
3. 一次推进一个阶段
4. 先验证，再进入下一步
5. 当现实变化时纠偏 Working Goal
6. 只在真实风险或边界变化时打断用户

## 基本规则

- 不要把代码生成当作完成。
- 不要在缺少验证时无限推进。
- 不要静默弱化 Mission、范围或质量底线。
- 每个阶段优先保持一个主要写入路径。
- 使用子代理是为了降噪，不是制造失控并行编辑。
- 有意义的 goal 变化必须记录到项目文档或执行总结中。

## 参考资料

仅在需要时读取：

- `references/autonomous-execution-workflow.md`
  用于查看阶段循环、打断规则和 goal 纠偏策略。
- `references/agent-role-matrix.md`
  用于查看主编排者、主执行者和子代理的角色边界。

## 预期结果

使用该 skill 后，Codex 应能够：

- 按阶段持续推进项目
- 在宣称完成前先验证
- 在不偏离 Mission 的前提下调整短期目标
- 有意图地使用子代理
- 尽量减少不必要打扰

如果这些行为缺失，说明自主执行设置还不完整。
