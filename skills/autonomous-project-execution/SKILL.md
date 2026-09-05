---
name: autonomous-project-execution
description: 持续交付已授权的跨模块或跨阶段软件开发，按架构与契约组织并行实现、测试和交接；局部修复复用已有边界。
---

# Autonomous Project Execution

按需求与验收 → 架构及模块边界 → 接口契约 → 并行实现 → 集成验证交付推进。先检查已有实现，足够的架构/契约直接复用，不要求固定名称的 spec/plan。

- 架构决定职责与依赖，契约确定模块如何协作；主任务先稳定共享基础，再主动委派有收益的独立实现，自己推进关键路径。
- 工作包给出目标、写入归属、接口、已有授权及限制、验收。共享范围只有一个活跃负责人；改派先确认停止写入并交接差异，授权不能随委派扩大。
- 对当前集成产物验证用户要求与失败路径；保留验收强度，相关变更后重跑受影响检查。交付前清理自有临时文件及无关进程。

按当前阶段读取：[软件工程流程](references/software-engineering-workflow.md) 用于架构/契约、算法与性能、代码质量、测试及目录；[并行执行与交接](references/autonomous-execution-workflow.md) 用于依赖、共享资源或接管；[角色矩阵](references/agent-role-matrix.md) 用于选角色。不要默认加载全部参考。
