# 恢复 Codex 官方原版状态

如果你想撤销这次为你增加的全局自定义入口，并尽量恢复到修改前的 `~/.codex` 状态，优先使用下面这条命令：

```bash
bash ~/.codex/restore-official-state.sh --apply
```

如果 `~/.codex/restore-official-state.sh` 入口暂时不可用，也可以直接在仓库目录执行：

```bash
bash /path/to/codex-config/scripts/restore-codex-official-state.sh --apply
```

如果你想先看它会做什么，不立即修改：

```bash
bash ~/.codex/restore-official-state.sh --dry-run
```

这个恢复脚本只处理当前仍指向本仓库的入口。它会删除本仓库软连接，并优先恢复安装时保存的 `.codex-config-backup.<timestamp>`；旧版 `.bak` 与 `.bak.<timestamp>` 也会兼容恢复。

覆盖范围：

- `~/.codex/AGENTS.md`
- 以下全局入口：
  - `~/.codex/agents`
  - `~/.codex/prompts`
  - `~/.codex/docs`
  - `~/.codex/hooks.json`
  - `~/.codex/hooks`
  - `~/.codex/restore-global-setup.sh`
  - `~/.codex/restore-official-state.sh`
- 删除以下挂到 `~/.codex/skills/` 的个人 skill 软连接：
  - `project-bootstrap`
  - `autonomous-project-execution`
  - `feature-thread-launch`
  - `refero-design-system`

它不会做的事：

- 不会删除 `~/.codex` 下官方自带目录
- 不会删除你的 `config.toml`、`rules/`、`auth.json`、`plugins/` 等原有内容
- 不会删除当前仓库真源目录里的源文件

恢复后如果你还想重新挂回这套自定义体系，可以执行：

```bash
bash /path/to/codex-config/scripts/restore-codex-global-links.sh
```
