# rust_team2 内核模块

目标 openEuler 提交为 `6e0c18da64fd9919a51f8f2216a371503a5e2763`。2026-10-06 已在 6.6.0-team2-rust+ 内核编译成功并完成 10 轮装卸，证据见 ../evidence/logs/lifecycle-20261006T033800Z-RYZrtF/。

| 文件 | 用途 |
|---|---|
| rust_team2.rs | module! 元数据、初始化、持有 Vec 与统计状态、Drop 日志 |
| statistics.rs | 不依赖内核的借用式统计函数及6项测试 |
| Kbuild | 将 rust_team2.o 构建为可加载模块 |
| Makefile | 调用目标内核 Kbuild，产物 rust_team2.ko |
| LICENSE | 与源码 SPDX 对应的 GPL-2.0 文本及内核许可元信息 |

完整操作见 [复现流程](../docs/03-环境与复现流程.md)。`bash scripts/test-logic.sh` 只验证 statistics.rs；它不是编译 rust_team2.rs 的替代品。

模块不提供用户输入接口，无设备节点，不注册定时器或线程。它的教学目标是展示动态装卸、Rust 可失败分配、借用、所有权和清理路径。未来增加接口时再补资源注销、并发和失败回滚测试。

初始化预期日志：`[rust_team2] event=loaded count=6 sum=23 min=1 max=9`。
卸载开始预期日志：`[rust_team2] event=unload_begin retained=6 sum=23`。

内核 API 来源与代码许可见 [来源说明](../THIRD_PARTY_NOTICES.md)。
