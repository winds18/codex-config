# 配置体系总览

本仓库提供全局行为约定、按需技能、可选代理和确定性检查。目标是在授权范围内自主完成交付，并让独立工作包有效并行。

| 层 | 维护内容 | 加载方式 |
| --- | --- | --- |
| AGENTS.md | 授权、并行、范围、证据交付 | 全局入口 |
| 项目 AGENTS/override | 真实命令、局部约束、协作接口 | 当前项目范围 |
| skills | 初始化、自主推进与跨项目统筹、显式新任务交接、前端方法 | 按任务触发 |
| agents | 可选职责、模型与沙箱 | 需要该角色时 |
| prompts | 人工选用的简短提示 | 不由 hook 全局注入 |
| hooks | 受支持工具路径上的有限确定性检查 | 用户信任后 |
| guard/Git hooks | 配置结构、脚本行为、提交与历史检查 | 验证/提交边界 |
| 统一安装入口与清单 | 源码预检、入口归属、备份、事务恢复和诊断 | `install.sh` 默认预览，`--apply` 执行 |

## 工作流

相关工作默认在当前任务进行；主任务实现关键路径，子代理负责独立文件组，共享契约由单一负责人维护。已有相关任务时先读取成果和实际状态，在已有授权内续接，避免重复派发。是否分 worktree 取决于隔离需求，是否新建用户任务取决于用户要求。

软件工程和协作流程由 [自主执行技能](../skills/autonomous-project-execution/SKILL.md) 维护，[流程导航](thread-governance-policy.md) 只链接相应入口；当前产品与模型适配见 [client-compatibility.md](client-compatibility.md)。项目规则只补项目事实和例外，角色只补职责差异，不复制全局约定。

## 维护入口

- [README](../README.md)：使用和验证。
- [安装说明](restore-codex-setup.md)：一条命令预检、安装、自检；更新与信任。
- [卸载说明](restore-codex-official-state.md)：恢复安装前状态。
- [Hooks 边界](hook-enforcement-policy.md)：硬检查与权限职责。
- [Git 工作流](git-workflow-policy.md)：提交和推送的实际内容验证。

仓库真源与运行时用户状态分开：本仓库不管理 auth、会话、个人偏好或账号可用模型。无需因维护规则而覆盖整个用户目录。
