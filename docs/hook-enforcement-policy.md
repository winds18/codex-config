# Hook 守门点设计

这份文档定义如何把全局开发规范从“提醒”升级为“可检查的守门点”。

目标是增强可靠性，不是增加流程负担。

---

## 1. 设计原则

- 文档定义意图
- Hook 卡住高风险动作
- Guard 脚本检查稳定事实
- Git hook 保证提交和推送前的最低一致性
- 不能自动判断的内容，保留为主编排者验收清单

不要试图把所有规范都做成硬阻断。

只有高置信、低误伤、后果明确的节点才应强制阻断。

---

## 2. 三层守门模型

### Codex lifecycle hooks

用于运行时守门。

适合：

- 阻断明显危险命令
- 阻断明显泄露 secrets 的 prompt
- 在完成声明前提醒验证
- 在 push 前提醒运行 guard

不适合：

- 复杂阶段编排
- 判断某个功能线程是否真正完成
- 替代主线程验收

### Repository guard script

用于检查仓库确定性事实。

当前脚本：

```bash
bash scripts/codex-config-guard.sh
```

它检查：

- 必要入口文件存在
- shell 脚本语法正确
- hooks JSON 合法
- Python hook 可编译
- `docs/` 模板和 skill 引用副本一致
- 便携入口没有写死本机绝对路径

### Git hooks

用于提交和推送前守门。

当前模板：

- `git-hooks/pre-commit`
- `git-hooks/pre-push`

它们都调用：

```bash
bash scripts/codex-config-guard.sh
```

安装脚本通过 worktree-local `core.hooksPath` 激活 `git-hooks/` 目录，而不是手动复制单个 hook 文件：

```bash
bash scripts/install-git-hooks.sh
```

每个新 clone 和新 worktree 都应在当前 worktree 内各自执行一次安装脚本。

---

## 3. 当前强制节点

### Prompt 提交前

高置信 secret 会被阻断，例如：

- API key
- GitHub token
- 私钥块

### 工具执行前

明显危险动作会被阻断，例如：

- `git reset --hard`
- `git clean -fd`
- `git push --force`
- `rm -rf /`
- `sudo rm`
- `chmod -R 777`
- `--dangerously-bypass` / `danger-full-access`

如确实需要执行破坏性动作，应先停下来获得明确人类批准。

### 直接修改 live `~/.codex` 入口

默认阻断直接改：

- `~/.codex/AGENTS.md`
- `~/.codex/agents`
- `~/.codex/docs`
- `~/.codex/prompts`
- `~/.codex/skills`
- `~/.codex/hooks`
- `~/.codex/hooks.json`

正确做法是：

1. 修改当前仓库真源文件
2. 运行 `scripts/restore-codex-global-links.sh`

### 完成声明前

如果回复中出现完成/修复类表述，但没有任何验证证据，Stop hook 会要求继续补充验证或说明未验证原因。

---

## 4. 不做硬阻断的节点

以下规则非常重要，但不适合用 hook 强制：

- 主线程是否真的保持为控制面
- 功能线程是否真的完成了合理拆解
- goal delta 是否语义正确
- 验收是否符合产品意图
- 是否过早陷入局部细节

这些应由主编排者结合 `docs/plan.md` 和功能线程回传摘要进行判断。

---

## 5. 安装与信任

首次部署或更新后执行：

```bash
bash scripts/restore-codex-global-links.sh
```

该脚本会挂载：

- `~/.codex/hooks.json`
- `~/.codex/hooks`

Codex 对非托管 command hook 需要信任确认。新设备或 hook 改动后，应在 Codex 中打开 `/hooks`，检查并信任这些 hook。

如果当前仓库已经是 git 仓库，可安装 Git hooks：

```bash
bash scripts/install-git-hooks.sh
```

确认方式：

```bash
git config --worktree --get core.hooksPath
```

---

## 6. 维护规则

新增强制规则前先判断：

- 是否高置信
- 是否低误伤
- 是否有明确恢复路径
- 是否不会明显拖慢主体开发

如果答案不满足，不要做硬阻断，改成文档清单或 guard warning。
