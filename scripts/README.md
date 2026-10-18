# 脚本使用说明

从项目根目录用 `bash scripts/文件名.sh` 执行，无需先 chmod。所有 shell 文件使用 LF 换行。

| 脚本 | 输入与用途 | 权限 |
|---|---|---|
| test-logic.sh | 无参数；编译运行纯统计逻辑测试，保存主机测试日志 | 普通用户，需 rustc |
| install-build-deps.sh | 安装内核编译依赖并打印 LLVM 版本 | sudo，仅实验 openEuler |
| build-kernel-vm.sh | 在 ~/os-lab/kernel 编译已配置内核；保存 kernel-build.log 和退出状态 | 普通用户，需先完成工具链和内核配置 |
| finish-build-vm.sh | 等待完整内核成功后构建本组模块；失败则停止 | 普通用户，仅当前 team2 实验目录 |
| install-kernel-vm.sh | 固定源码与成功编译检查后安装内核、模块、initramfs 和启动项；保留旧内核 | sudo，仅 team2 实验虚拟机 |
| check-env.sh | 内核源码/构建目录；核对固定版本与必要产物 | 普通用户，openEuler |
| build-module.sh | 内核目录；环境检查后构建 .ko，保存日志与校验值 | 普通用户，openEuler |
| test-lifecycle.sh | 可选 .ko 路径和轮数，默认10；检查并装卸，记录证据 | sudo，仅实验 openEuler |
| extract-new-log.py | before、after、输出路径；提取新增内核日志，边界丢失即报错 | 由循环脚本调用 |
| test-negative.sh | 重复加载、卸载不存在模块；核对预期失败、模块状态与新增日志 | sudo，仅实验 openEuler |
| verify-evidence.py | 装卸证据目录；核对逐轮结果、原始日志增量及计数 | 普通用户，Python 3 |
| package-submission.py | 打包源码、文档和证据，内含逐文件SHA256清单 | 普通用户，Python 3 与 Git |

Ubuntu/WSL 上统一检查：`bash scripts/verify-host.sh`。该命令包含6项Rust逻辑测试、Python测试、历史装卸证据核验与学习示例；不会加载模块。它有一项专门验证Ubuntu会被内核构建脚本拒绝，因此不要在openEuler直接运行这份主机检查脚本。

证据复核：`python3 scripts/verify-evidence.py evidence/logs/lifecycle-20261006T033800Z-RYZrtF`。
提交打包：`python3 scripts/package-submission.py`。压缩包位于build，故不提交到Git；每次修改文档后可重新生成。

构建脚本不会自动安装软件、升级内核或加载模块。循环脚本拒绝已加载的同名模块，不使用强制卸载、不清空日志；失败时尽力移除自己加载的模块，失败清理也会明确报错。不要与其他人的手工装卸同时执行。

源码基线配置在 environment/baseline.env；修改它意味着重新核对 API 和完整构建，不是解决兼容性报错的万能开关。
