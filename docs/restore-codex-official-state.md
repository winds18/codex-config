# 卸载本配置并恢复安装前状态

统一入口按清单撤销本配置，恢复安装前文件；可能恢复用户原有自定义设置，不等于官方出厂状态。默认只预览，`--apply` 才执行。

```bash
bash install.sh uninstall
bash install.sh uninstall --apply
```

非默认配置根指定 `--codex-home DIR`，或运行 `bash /path/to/config/codex-config.sh uninstall`，后者自动绑定入口所在根。技能目录沿用清单，无需重新填写。旧 `scripts/restore-codex-official-state.sh` 保留相同行为。

## 恢复原则

- 仅撤销清单拥有的入口，恢复精确记录的原文件、软连接与权限。
- 保留外来 agent/hook，包括安装后新增的外来 hook 条目。
- 发现用户改动或冲突时报告，不猜测覆盖；无清单旧安装按 [迁移说明](restore-codex-setup.md) 处理。
- 不手动删除 `.codex-config-state` 跳过冲突，其中包含恢复需要的清单、备份和事务记录。
- 写入前验证完整备份，格式错误或新清单摘要不符时保留现场并停止；旧清单缺少摘要的能力边界见 [安装说明](restore-codex-setup.md)。

## 中断恢复

安装或卸载事务中断后，先预览恢复，回到该事务开始前的文件状态，再继续安装或卸载：

```bash
bash install.sh recover --codex-home /path/to/config
bash install.sh recover --codex-home /path/to/config --apply
```

`uninstall`、`recover` 不执行安装源码预检，规则文本或引用损坏不会阻断恢复；仍需可运行的管理脚本和原状态记录。仓库被搬走或入口断链时，从可用的完整源码目录运行命令并显式指定原配置根。不可用的脚本或损坏的备份不能靠跳过检查恢复。

实体目录先完整暂存再替换，操作中被终止时仍按原事务恢复并清理其暂存资源。恢复前核对正式入口和事务持有的原内容；如果期间出现外来改动，则保留冲突和事务记录，不覆盖它们。

Git hooks 的卸载和事务独立处理，在对应工作树执行：

```bash
bash scripts/install-git-hooks.sh --repo /path/to/worktree --uninstall
bash scripts/install-git-hooks.sh --repo /path/to/worktree --uninstall --apply
```

Git hooks 操作中断时将 `--uninstall` 换为 `--recover`，先预览再执行。脚本检查锁所属进程并保留外部冲突；配置卸载不会替你卸载仓库 Git hooks。

完成后开启新任务核对实际状态。仓库自测只操作临时目录，不改变真实用户配置。
