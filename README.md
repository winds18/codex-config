# codex-config

一套以自主完成、有效并行和证据交付为目标的个人 Codex 配置。主任务直接推进关键路径，子代理负责独立模块，公共接口由明确负责人集成；专业流程按需加载。

## 使用入口

- [全局工作约定](AGENTS.md)：授权、并行、范围与交付。
- [并行开发流程](docs/thread-governance-policy.md)：任务拆分、既有任务统筹、逐仓归属、等待与联合验收。
- [软件工程流程](skills/autonomous-project-execution/references/software-engineering-workflow.md)：需求与验收 → 架构 → 接口契约 → 并行实现 → 集成测试；目录与临时文件清理。
- [客户端与模型适配](docs/client-compatibility.md)：模型继承、Goal、定时任务和技能发现。
- [体系总览](docs/codex-global-setup-overview.md)：各层职责和维护入口。

主任务先确定架构和共享契约，再分发独立模块并推进关键路径；局部修复复用现有设计。文件及运行资源明确归属，改派确认停止，证据对应当前集成状态，临时文件用完即删。默认在当前任务完成，跨项目协作按授权复用既有任务并核对参与版本；新用户任务只响应明确请求。

交付同时要求功能健壮、执行高效和代码清晰：按实际规模选择算法与数据结构，必要时研究比较，以测量验证性能，控制重复、耦合及抽象成本；详细要求统一维护在软件工程流程中。

多端项目可[按职责组织任务](skills/autonomous-project-execution/references/autonomous-execution-workflow.md#按职责组织多端任务)：前端、后端等保留各自上下文，各端围绕同一功能与契约并行交付，主任务负责集成；短期工作用子代理，不固定建立全套团队。

## 一键安装与维护

需要 Bash、Python 3.9+；克隆使用 Git。完整源码压缩包也可离线安装，无需 Git、rg 或 Codex CLI。入口面向 macOS/Linux/WSL，回归测试在 macOS 运行。

```bash
git clone https://github.com/winds18/codex-config.git
cd codex-config
bash install.sh --apply
```

这一条命令依次完成**源码预检 → 按清单事务安装 → 安装后诊断**。不带 `--apply` 默认只预览；重复执行应用当前本地仓库版本，不自动拉取远程或重置源码。

```bash
bash install.sh                  # 预检并预览安装，不写配置
bash install.sh check            # 只检查源码
bash install.sh doctor           # 只检查已安装文件和环境
bash install.sh uninstall        # 预览卸载；添加 --apply 执行
bash install.sh recover          # 预览中断事务恢复；添加 --apply 执行
```

安装后开启新任务验证规则和技能发现；自定义 hook 在客户端 `/hooks` 审查信任。安装器不修改账号、个人 config.toml 或信任状态。doctor 区分文件错误与环境提示；未发现 CLI 不等于桌面客户端不可用。

脚本按本仓库拥有的文件安装，保留外来 agent 和 hook，记录精确备份与事务清单。默认技能位置为配置根下的 skills；目标客户端使用 `.agents/skills` 时可显式选择 `--skills-dir`，不要双重安装同名技能。

```bash
bash install.sh --codex-home /path/to/config --skills-dir /path/to/skills --apply
bash /path/to/config/codex-config.sh doctor
bash /path/to/config/codex-config.sh uninstall
```

安装后的 `codex-config.sh` 自动绑定所在配置根；卸载沿用清单中的技能目录。旧 `scripts/restore-codex-global-links.sh`、`scripts/codex-config-doctor.sh`、`scripts/restore-codex-official-state.sh` 继续兼容；日常维护使用统一入口。卸载恢复安装前状态，不保证出厂默认状态。

旧版无清单的整目录软连接需先按已确认的原备份还原，脚本不会猜测最新备份覆盖用户状态。具体步骤与故障恢复见 [安装说明](docs/restore-codex-setup.md) 和 [卸载说明](docs/restore-codex-official-state.md)。

## 按需技能与角色

| 入口 | 用途 |
| --- | --- |
| `$project-bootstrap` | 建立真实运行和验证入口；不强制文档五件套 |
| `$autonomous-project-execution` | 跨模块/阶段的自主推进、并行实现和集成 |
| `$feature-thread-launch` | 用户明确要求独立任务时交接 |
| `$refero-design-prompts` | 视觉方向、现有设计系统适配、模板与渲染验证 |

保留 11 个兼容角色名，按需要选用；主执行与高难复核默认继承宿主模型，轻量角色保留有明确用途的配置。没有固定“每阶段派全套角色”的流程，也没有按模型代际硬封禁。

`prompts/` 是人工可选入口；hooks 不再全局注入架构、前端或工作习惯，不通过“完成/测试”等关键词阻断结束。

## 检查与 Git hooks

```bash
bash scripts/codex-config-guard.sh
bash scripts/install-git-hooks.sh
bash scripts/install-git-hooks.sh --apply
git config --worktree --get core.hooksPath
```

Git hooks 安装也先预览，保留已有配置以便卸载；新 worktree 确认其作用域。不要把本仓库 hooks 安装到缺少相应 scripts 的其他项目。

Guard 检查配置结构、引用、脚本语法、运行行为、敏感信息、安装恢复及模板资产。pre-push 扫描将发送的历史，覆盖合并提交和新远程分支。它不验证文档必须包含某些口号，也不把当前工作树安全等同于历史安全。

权限仍由宿主控制；自定义 hook 仅覆盖有限的直接工具操作。[Hooks 边界](docs/hook-enforcement-policy.md)、[Git 工作流](docs/git-workflow-policy.md)。

## 维护

修改真源后运行完整 guard；获取并审查新版本后，重复 `bash install.sh --apply` 应用变更。不直接编辑已安装软连接。hooks 合并内容和新入口需重新安装，规则文件软连接读取到的是当前真源；安装器不切换或下载源码。

项目模板保持短、具体；领域细节留在技能。第三方模板保留来源、许可与固定快照，不全量加载为上下文。查看 [一键安装优化与验证](audit/2026-09-05/INSTALLATION.md)、[工程流程与约束优化](audit/2026-09-05/REFINEMENT.md)、[首轮优化与验证](audit/2026-09-05/IMPLEMENTATION.md) 和 [首轮逐文件清单](audit/2026-09-05/file-review.md)。
