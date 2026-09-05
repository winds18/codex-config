# 项目级 Codex 配置最小模板

## 文档信息

| 项目 | 内容 |
| --- | --- |
| 状态 | 生效中 |
| 最后更新 | 2026-09-05 |
| 适用范围 | 需要项目级 `.codex/config.toml` 的仓库 |
| 关联入口 | `AGENTS.md`、`docs/project-expansion-workflow.md` |

只在项目确实需要固定权限边界时创建 `.codex/config.toml`。机器级模型、账号、插件和个人偏好仍保留在 `~/.codex/config.toml`，不要复制进项目。

推荐从最小权限配置开始：

```toml
default_permissions = "project-safe"

[permissions.project-safe]
description = "项目可写，但拒绝读取常见敏感文件。"
extends = ":workspace"

[permissions.project-safe.filesystem]
glob_scan_max_depth = 4

[permissions.project-safe.filesystem.":workspace_roots"]
".env" = "deny"
"**/.env" = "deny"
"**/.env.local" = "deny"
"**/.env.production" = "deny"
"**/.env.staging" = "deny"
"**/*.key" = "deny"
"**/*.p12" = "deny"
"**/*.pfx" = "deny"
```

使用规则：

- 只保留项目真实存在且需要保护的 glob。
- `.env.example`、`.env.sample`、`.env.template` 等无真实凭证的模板可以保留可读，不要用过宽的 `.env.*` 一并拒绝。
- `deny` 会同时阻断读取和写入；如果任务必须读取某类文件，不要机械照抄该规则。
- 使用无界 `**` 时设置合理的 `glob_scan_max_depth`，避免启动扫描无限扩张。
- 权限规则保护运行时读取；Git secret scan 负责提交与推送边界，两者不能互相替代。
- 项目需要网络、MCP 或更高权限时，单独按最小范围增加，不要直接切到全开放配置。


并发上限只在需要限制资源时设置，例如：

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 3
```

这是并发容量上限，不要求每轮派三个代理；主任务不计入该子代理上限。默认模型可保持宿主继承，不必项目锁定代际。不同客户端支持情况需按 [client-compatibility.md](client-compatibility.md) 核实；不在运行中的任务擅自修改机器设置。
