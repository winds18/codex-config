# Git 工作流策略

这份文档定义全局配置仓库默认采用的 Git 工作流边界。

目标是吸收可靠的提交治理经验，而不是照搬团队后端仓库的全部流程。

---

## 1. 分层原则

规则默认分三层：

- `skills`：提示 agent 使用可复用工作流，不承担硬阻断。
- `codex hooks`：在 agent 执行工具或回合结束时做运行时提醒、弱校验和高风险阻断。
- `git hooks`：在 commit / push 边界做确定性硬校验。

判断规则放哪一层时：

- 需要方法论、上下文、提示词复用，放 `skills` 或 `docs/`。
- 需要在 agent 运行过程中提醒或拦截，放 `codex hooks`。
- 需要提交边界上的确定性校验，放 `git hooks` 或 guard 脚本。

不要把需要人类语义判断的规则下沉成硬阻断。

---

## 2. Git Hooks 安装策略

本仓库使用 worktree-local `core.hooksPath` 激活 Git hooks。

安装命令：

```bash
bash scripts/install-git-hooks.sh
```

规则：

- 每个新 clone 需要安装一次。
- 每个新 worktree 也需要在该 worktree 内安装一次。
- 安装脚本只负责激活本仓库的 `git-hooks/` 目录。
- 不依赖手动复制 `.git/hooks` 中的单个文件。
- `pre-push` 除运行仓库 guard 外，还扫描全部待推送提交历史中的高置信 secret。

这种方式便于后续增加 `commit-msg`、`prepare-commit-msg` 等 hook，而不需要改安装逻辑。

---

## 3. 分支管理

默认采用轻量 trunk-based 模型。

### 主线

- `main` 是稳定主线。
- `main` 只接收已验证、可解释、可回退的检查点。
- 不在 `main` 上长期堆积未完成开发。

### 工作分支

具体功能、修复、重构默认使用短命分支：

```text
feature/<short-name>
fix/<short-name>
refactor/<short-name>
docs/<short-name>
chore/<short-name>
experiment/<short-name>
release/<version>
hotfix/<short-name>
```

规则：

- 一个功能线程默认对应一个工作分支或 worktree。
- 一个分支只服务一个清晰目标。
- 分支名应短、可读、能表达意图。
- `experiment/*` 可以失败，但不能直接合并；有价值的结果应整理到正式分支后再合并。
- 合并前必须有验证证据。
- 合并后应归档功能线程，并清理临时分支或 worktree。

---

## 4. 提交前整理顺序

每次提交前默认按下面顺序整理：

1. 查看 `git status` 和相关 diff，确认本次提交边界。
2. 只暂存同一目的下的相关改动，避免把无关变化混进一个提交。
3. 运行离改动最近的验证命令。
4. 运行项目或仓库 guard。
5. 确认关键文档已同步。
6. 编写清晰提交信息。

提交应是稳定检查点，不是随手保存点。

推送前必须检查待推送历史，而不只是当前工作树；否则“先提交 secret、后续再删除”的历史仍会进入远程。

---

## 5. 提交信息默认规则

全局默认采用轻量提交格式：

```text
type: 中文简短说明
```

常用类型：

- `init`
- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `build`
- `ci`
- `chore`
- `revert`

`type` 可以保留英文约定，标题和 body 默认使用中文。

是否使用 emoji、版本号、详细 body，由项目级规则决定，但自然语言说明仍默认中文。

---

## 6. 版本发布

版本发布是明确动作，不是每次普通提交都自动发生的动作。

默认发布流程：

1. 确认 `main` 或发布分支处于可发布状态。
2. 运行完整验证命令。
3. 更新版本事实源。
4. 更新 `CHANGELOG.md` 或 release notes。
5. 创建发布 tag。
6. 构建发布产物。
7. 校验发布产物。
8. 推送 tag 或发布到目标平台。

推荐版本规则：

- 有发布节奏的项目优先使用 SemVer：`MAJOR.MINOR.PATCH`。
- 预发布版本使用 `X.Y.Z-alpha.N`、`X.Y.Z-beta.N`、`X.Y.Z-rc.N` 或项目级约定。
- tag 默认使用 `vX.Y.Z`。
- 版本事实源只能有一个，例如 `VERSION`、`package.json`、`pyproject.toml` 或语言生态的项目配置。
- 运行时 `/version`、UI 显示、构建元数据都应从版本事实源派生，不要维护第二份事实。

默认不允许：

- 未验证就发布。
- 发布后静默改 tag。
- 多个文件各自维护互相独立的版本号。
- 把本地临时构建结果当成已发布结果。

回滚优先使用新提交或新发布版本修正问题。

除非我明确批准，不要默认改写已推送 tag。

---

## 7. 构建产物管理

构建产物默认不进入源码仓库。

推荐规则：

- 源码仓库存放源代码、配置、脚本、文档和必要锁文件。
- `dist/`、`build/`、`target/`、`.next/`、`coverage/`、临时压缩包等默认加入 `.gitignore`。
- 必须长期保存的产物应进入 release、对象存储、包仓库、镜像仓库或其他明确产物仓库。
- 发布产物应能从某个 commit 或 tag 可重复构建。
- 构建产物需要记录来源 commit、版本号、构建时间或构建环境摘要。

可以提交构建产物的例外：

- 静态站点仓库明确以构建结果作为发布源。
- 客户端 SDK、schema、锁文件或生成文件是项目约定的源码输入。
- 项目级 `AGENTS.md` 明确说明提交原因、生成命令和验证方式。

如果提交生成物，必须同时写清：

- 生成命令
- 是否可重复生成
- 何时需要更新
- 如何验证生成物未过期

---

## 8. 不全局强制的规则

以下规则不适合写成全局硬约束：

- 每次提交必须提升 `VERSION`
- 提交标题必须携带 `{version}`
- `main` 和非 `main` 分支必须采用固定 prerelease 版本格式
- 所有项目都必须维护同一种 `progress.md`
- 所有项目都必须使用 release 分支
- 所有项目都必须提交构建产物

这些规则适合有明确发布节奏的团队仓库。

个人全局配置只保留为项目级可选项，由项目级 `AGENTS.md` 或 guard 决定是否启用。

---

## 9. 维护要求

修改 `git-hooks/`、`hooks/`、`scripts/*guard*` 或 Git 工作流规则时，应同步检查：

- `AGENTS.md`
- `README.md`
- `docs/hook-enforcement-policy.md`
- `docs/project-AGENTS-template.md`
- `docs/project-expansion-workflow.md`

如果规则已经能被机器稳定判断，优先放进 guard 或 Git hook。

如果规则需要语义判断，保留在文档和主编排验收中。
