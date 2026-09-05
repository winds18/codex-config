# 安装与更新

仓库根目录运行 `bash install.sh --apply`，依次执行离线源码预检、事务安装、安装后诊断。不带参数或加 `--dry-run` 只预览，不写目标配置。需要 Bash、Python 3.9+；不会自动下载依赖或更新源码。

| 命令 | 行为 |
| --- | --- |
| `bash install.sh` | 预检并预览安装，给出可复制的执行命令 |
| `bash install.sh --apply` | 安装；重复执行应用当前仓库版本 |
| `bash install.sh check` | 只检查来源完整性、配置与引用、脚本语法和模板本地依赖 |
| `bash install.sh doctor` | 只检查路径、已安装文件、备份和环境 |
| `bash install.sh uninstall` | 预览卸载；加 `--apply` 执行 |
| `bash install.sh recover` | 预览中断事务恢复；加 `--apply` 执行 |

`check`、`doctor` 始终只读，不接受 `--apply`。完整维护回归另用 `bash scripts/codex-config-guard.sh`，需要 Git 和 rg；安装预检不执行回归测试、hooks 或上游模板代码。

## 路径与安装内容

`--codex-home DIR` 选择配置根，缺省为 `$CODEX_HOME` 或 `~/.codex`；`--skills-dir DIR` 选择唯一技能目录，缺省沿用安装清单或配置根下的 skills；`--repo DIR` 选择完整源码来源，缺省为入口所在仓库。源码位置须在安装后保留，安装内容通过软连接引用它。

```bash
bash install.sh --codex-home /path/to/config --skills-dir /path/to/skills --apply
bash /path/to/config/codex-config.sh doctor
```

安装后的 `codex-config.sh` 自动绑定所在配置根，即使环境中的 `CODEX_HOME` 不同也不会写到另一个根；显式 `--codex-home` 可覆盖。目标宿主需要 `.agents/skills` 时选择该路径，不重复安装同名技能。

安装内容为全局 AGENTS、agents/docs/prompts/hooks 的逐文件入口、四个技能的逐技能入口和管理脚本。hooks.json 合并本仓库拥有的组并保留外来条目；清单及精确备份保存在配置根的 `.codex-config-state`。不安装仓库 AGENTS.override，不修改 auth、config.toml、账号、模型权限或 hook 信任。

## 更新与诊断

获取并审查源码新版本后，重复安装命令即可更新清单和 hooks 合并内容；脚本不执行 git pull、checkout 或 reset。普通规则软连接会立即读取真源变化，预览不是源码版本隔离。安装来源搬迁也先预览；已有入口或备份冲突时拒绝覆盖。

doctor 的文件错误返回非零，包括入口漂移、断链、损坏备份和待恢复事务；CLI 不在 PATH、全局 override 可能替代规则、重复技能入口等是环境/发现提示，文件正确时仍返回 0。未安装时会明确显示无清单；诊断通过不代表规则已在客户端激活。

新清单记录备份摘要，诊断、更新和卸载会检查备份格式与摘要。旧清单没有摘要时会明确提示，只能检查格式；更新可为当前备份建立摘要，不能追溯证明旧备份未被改动。发现备份残留但清单缺失时停止安装，避免把原备份覆盖为当前入口；先按恢复说明处理。

若安装后诊断失败，命令返回非零并明确配置已经写入。根据诊断处理冲突，或先预览卸载；不会用自动回滚覆盖安装期间出现的外部改动。中断处理见 [恢复说明](restore-codex-official-state.md)。

安装后开启新任务核对规则和技能；用户在 `/hooks` 审查信任。Git hooks 独立选装：`bash scripts/install-git-hooks.sh` 预览，追加 `--apply` 执行；支持 `--repo`、`--hooks-dir`、`--uninstall`、`--recover`。配置安装不隐式更改 Git 设置。

## 旧入口与迁移

`scripts/restore-codex-global-links.sh`、`scripts/codex-config-doctor.sh`、`scripts/restore-codex-official-state.sh` 保留为兼容入口；新安装优先使用统一入口，取得完整的预检和安装后诊断。

有清单的安装可以幂等更新。旧版无清单的整目录软连接缺少所有权信息，须核对实际链接及对应原始备份后恢复原入口，再预览新安装；不能根据时间盲选备份，也不能删除整个配置目录来迁移。
