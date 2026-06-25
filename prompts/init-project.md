---
description: 基于全局 AGENTS 规则初始化一个新项目
argument-hint: PROJECT_NAME="" STACK="" GOAL="" EXCLUDES=""
---

基于我的全局 `AGENTS.md` 规则初始化这个新项目。

要求：

1. 先不要直接写业务代码。
2. 先展开项目级文档体系。
3. 把全局规则转化为项目内具体、可执行、简洁的规则。
4. 默认采用 goal-first、少打扰、可无人值守推进的方式。

项目输入信息如下：

- 项目名称：$PROJECT_NAME
- 技术栈偏好：$STACK
- 当前目标：$GOAL
- 当前明确不做的范围：$EXCLUDES

请按以下顺序工作：

1. 生成项目级 `AGENTS.md`
2. 生成 `README.md`
3. 生成 `docs/spec.md`
4. 生成 `docs/plan.md`
5. 生成 `CHANGELOG.md`
6. 如有必要，初始化 `.codex/` 目录

请确保：

- 不要整份照抄全局总纲
- 项目级文档必须具体、贴近仓库现实
- 明确 Mission、Constraints、Working Goal、Stage Objective
- 明确运行、测试、验证、升级打断规则
- 在项目文档完成前，不进入大规模业务实现
