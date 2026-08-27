# codex-config 项目规则

本仓库是真源目录，负责维护 Codex 全局配置。

## 范围

- 只修改本仓库真源文件。
- 不直接编辑 `~/.codex` 中已挂载入口。
- 需要刷新 live 入口时，运行 `scripts/restore-codex-global-links.sh`。
- 本文件只写本仓库规则；不要复制全局 `AGENTS.md`。

## 必查边界

修改以下内容时，必须同步检查 README、恢复脚本、官方还原脚本和 guard：

- `AGENTS.md`
- `AGENTS.override.md`
- `agents/`
- `skills/`
- `hooks/`
- `git-hooks/`
- `prompts/agent-work-habits.md`
- `scripts/`
- `docs/restore-*`
- `docs/hook-enforcement-policy.md`
- `docs/git-workflow-policy.md`
- `docs/codex-global-setup-overview.md`

## 验证

仓库一致性校验：

```bash
bash scripts/codex-config-guard.sh
```

修改 Git hooks 后检查：

```bash
bash scripts/install-git-hooks.sh
git config --worktree --get core.hooksPath
```

修改全局挂载入口后检查：

```bash
bash scripts/restore-codex-global-links.sh
ls -l ~/.codex/AGENTS.md ~/.codex/agents ~/.codex/docs ~/.codex/prompts
ls -l ~/.codex/hooks.json ~/.codex/hooks
ls -l ~/.codex/restore-global-setup.sh ~/.codex/restore-official-state.sh
ls -l ~/.codex/skills/project-bootstrap ~/.codex/skills/autonomous-project-execution ~/.codex/skills/feature-thread-launch ~/.codex/skills/refero-design-prompts
```

新设备或 hooks 变更后，只提醒用户打开 `/hooks` 审查并信任；不要替用户静默信任 hook。

## 维护规则

- 全局 `AGENTS.md` 保持精炼；流程细节下沉到 skill、docs、hooks 或 guard。
- Agent 工作习惯写入 `prompts/agent-work-habits.md`，由 hook 注入。
- 子代理工作习惯写入 `prompts/subagent-work-habits.md`，保持轻量、边界清晰。
- `AGENTS.override.md` 不挂载到 `~/.codex`，否则会替代全局规则。
- 新增 skill 时，同步恢复脚本、官方还原脚本、README 和 guard。
- 修改模板时，保持 `docs/` 真源与 skill 引用路径一致。
- 提交前不得包含临时目录、日志、备份文件或真实 secret。
