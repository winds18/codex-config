# 按需角色选择

按工作选择职责；此表不是固定团队或执行顺序。

| 角色 | 独立职责 | 默认配置 |
| --- | --- | --- |
| worker | 负责一个文件组的实现、修复和相关验证 | 继承主任务模型/推理 |
| explorer-lite | 有具体问题的只读代码定位 | Luna / low |
| reviewer-lite | 正确性与回归首轮复核 | Terra / medium，只读 |
| security-reviewer | 授权边界、敏感数据、高风险代码深度复核 | 继承模型/推理，只读 |
| tester-lite | 失败日志归因与最近验证路径 | Terra / medium，只读 |
| planner | 依赖关系或阶段确实不清时补短计划 | 继承模型/推理，只读 |
| summarizer-lite | 压缩已经提供的大量证据 | Luna / low，只读 |
| refiner | 指定范围的文档或机械整理 | Terra / medium |
| pr-preparer | 根据实际差异起草交付说明 | Terra / medium，只读 |
| security-lite | 范围明确的初筛，不能替代深度复核 | Terra / low，只读 |
| orchestrator | 用户要求分层大项目时协助统筹，不剥夺主任务实现职责 | 继承模型/推理 |

自定义 worker 会覆盖宿主内置同名角色。指定模型不可用时由主任务承担或选择用户可用配置；不擅自改机器设置。当前版本及可用性见 [适配说明](../../../docs/client-compatibility.md)。
