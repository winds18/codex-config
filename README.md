# codex-config

这是一套面向个人 AI 开发的 Codex 全局配置仓库。

核心目标只有三个：

- 让当前仓库目录成为唯一真源目录
- 让 `~/.codex` 只承担可恢复的软连接入口
- 让新设备能够被人类或 AI 快速接管，而不是重新手配一遍

---

## 1. 仓库定位

这套配置不是某个单项目的局部规则，而是跨项目复用的 Codex 全局工作流。

当前已经包含：

- 全局 `AGENTS.md`
- 全局 agents 角色
- 全局 skills
- 全局 docs 模板与治理文档
- 全局 Codex hooks 守门点
- 仓库 guard 与 Git hooks 模板
- Git 分支、提交、发布与构建产物策略
- 一键挂载脚本
- 一键恢复官方原版状态脚本

日常维护原则：

- 只改这个仓库里的真源文件
- 不直接手改 `~/.codex` 里的软连接内容
- 改完后通过恢复脚本重新挂载或开新会话验证

---

## 2. 目录结构

```text
AGENTS.md
README.md
agents/
docs/
git-hooks/
hooks/
prompts/
scripts/
skills/
```

目录职责：

- `AGENTS.md`：全局总纲
- `agents/`：全局角色分工
- `skills/`：可被 Codex 发现和调用的全局能力
- `docs/`：模板、治理规则、恢复说明
- `hooks/`：Codex lifecycle hooks 与策略脚本
- `git-hooks/`：提交和推送前的仓库守门模板，通过 `core.hooksPath` 激活
- `scripts/`：挂载与恢复脚本
- `prompts/`：保留的轻量 prompt 入口

Git 工作流策略包含：

- 分支管理
- 提交前整理
- 版本发布
- 构建产物管理

---

## 3. 新设备首次部署

前提：

- 目标机器已安装 Codex
- 目标机器已安装 Git，并可访问 `https://github.com/winds18/codex-config.git`

推荐流程：

```bash
git clone https://github.com/winds18/codex-config.git
cd codex-config
bash scripts/restore-codex-global-links.sh
```

说明：

- 脚本会自动根据自身位置识别仓库根目录
- 仓库不需要 clone 到固定绝对路径
- `~/.codex` 不存在时会自动创建必要目录

执行完成后：

- 重新打开 Codex，或至少开启一个新会话
- 在 Codex 中打开 `/hooks`，检查并信任本仓库挂载的 hooks

---

## 4. 挂载后常用入口

挂载完成后，优先使用这些入口：

```bash
bash ~/.codex/restore-global-setup.sh
bash ~/.codex/restore-official-state.sh --dry-run
bash ~/.codex/restore-official-state.sh --apply
```

用途：

- `restore-global-setup.sh`：重新挂回这套全局配置
- `restore-official-state.sh --dry-run`：预览回退动作
- `restore-official-state.sh --apply`：回退到尽量接近官方原版状态

---

## 5. 部署后校验

最小校验命令：

```bash
ls -l ~/.codex/AGENTS.md ~/.codex/agents ~/.codex/docs ~/.codex/prompts
ls -l ~/.codex/hooks.json ~/.codex/hooks
ls -l ~/.codex/restore-global-setup.sh ~/.codex/restore-official-state.sh
ls -l ~/.codex/skills/project-bootstrap ~/.codex/skills/autonomous-project-execution ~/.codex/skills/feature-thread-launch
```

校验目标：

- 这些入口应存在
- 它们应指向当前 clone 的仓库目录

如果入口缺失或目标不对，重新执行：

```bash
bash scripts/restore-codex-global-links.sh
```

仓库自身一致性校验：

```bash
bash scripts/codex-config-guard.sh
```

如果当前目录已经是 git 仓库，可以安装提交和推送前守门：

```bash
bash scripts/install-git-hooks.sh
git config --worktree --get core.hooksPath
```

每个新 worktree 都需要在该 worktree 内重新执行一次安装脚本。

---

## 6. 日常更新方式

当你在一台机器上更新了真源文件，另一台机器同步时按下面顺序：

```bash
cd /path/to/codex-config
git pull
bash ~/.codex/restore-global-setup.sh
```

原则：

- `git pull` 负责更新真源
- `restore-global-setup.sh` 负责刷新入口
- 新 skill 或新 prompt 如果没马上显示，直接开新会话验证
- hooks 发生变化后，打开 `/hooks` 重新检查信任状态

---

## 7. AI 自动部署说明

如果你要让 AI 在新设备自动完成接管，给它的目标可以直接写成：

```text
将 https://github.com/winds18/codex-config.git clone 到本机，
执行仓库内 scripts/restore-codex-global-links.sh，
确认 ~/.codex 下的 AGENTS、agents、docs、prompts、hooks、restore 脚本和 skills 入口均已正确挂载，
运行 scripts/codex-config-guard.sh，
提醒我在 Codex 中打开 /hooks 检查并信任 hook，
最后回报校验结果，但不要推送、不要改官方目录内容。
```

AI 执行时应遵守：

- 优先在仓库内改真源，不改 `~/.codex` 入口内容
- 优先用恢复脚本重建入口，而不是手动补单个软连接
- 在宣称完成前先做软连接校验
- 不替我静默信任 hook；只提醒我进入 `/hooks` 审查

---

## 8. 官方原版恢复

如果你要临时或长期撤销这套自定义体系：

```bash
bash ~/.codex/restore-official-state.sh --dry-run
bash ~/.codex/restore-official-state.sh --apply
```

恢复后如果还要重新挂回本仓库：

```bash
bash /path/to/codex-config/scripts/restore-codex-global-links.sh
```

---

## 9. 维护约定

为了避免前后不一：

- `docs/` 里的项目模板是主要维护版本
- `skills/project-bootstrap/references/` 中对应模板必须与 `docs/` 同步
- 任何会影响跨设备部署的改动，都必须同时检查：
  - `scripts/`
  - `hooks/`
  - `git-hooks/`
  - `docs/restore-*`
  - `docs/hook-enforcement-policy.md`
  - `docs/git-workflow-policy.md`
  - `docs/codex-global-setup-overview.md`
  - 本 README

这份 README 是人类和 AI 在仓库层面的单入口。
