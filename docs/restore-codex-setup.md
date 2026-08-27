# 一键恢复 Codex 全局入口

如果 `~/.codex` 下的软连接丢失、损坏，或你迁移到了新环境，需要重新挂载全局入口：

首次安装或新设备首次接管时，直接在仓库目录执行：

```bash
bash /path/to/codex-config/scripts/restore-codex-global-links.sh
```

如果这套入口已经挂载过，也可以直接执行：

```bash
bash ~/.codex/restore-global-setup.sh
```

这个脚本会恢复以下入口：

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
- `~/.codex/skills/refero-design-prompts`

注意：

- 仓库根目录的 `AGENTS.override.md` 只服务本仓库。
- 不要把 `AGENTS.override.md` 挂载到 `~/.codex`，否则会替代全局规则。

恢复策略：

- 如果目标路径不存在，直接创建软连接
- 如果目标路径是普通文件、目录或非本仓库软连接，会先备份为 `.codex-config-backup.<timestamp>`
- 如果目标路径已经指向本仓库，会直接刷新为最新链接
- 脚本默认会根据自身所在位置自动推导仓库根目录；只有在特殊场景下才需要手动传 `BASE_DIR`
- 官方恢复脚本会优先恢复新格式备份，并兼容旧版 `.bak` 与 `.bak.<timestamp>` 备份

建议：

- 执行恢复后，重新打开 Codex 或开启新会话
- 如果技能或 prompt 没立即显示，优先用新会话验证
- 如果 hooks 是首次挂载或刚更新，在 Codex 中打开 `/hooks` 检查并信任
