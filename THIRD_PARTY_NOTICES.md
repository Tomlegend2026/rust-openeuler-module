# 代码来源与许可

本初稿由 AI 辅助生成，供小组检查、修改与实际验证。最终报告按课程要求说明工具使用，不把未亲自进行的实验写成个人贡献。

Rust 模块入口结构参考 openEuler 源码中的官方 Rust 最小示例：

- 作者归属：Rust for Linux Contributors。
- 固定源码：https://github.com/openeuler-mirror/kernel/blob/6e0c18da64fd9919a51f8f2216a371503a5e2763/samples/rust/rust_minimal.rs
- 原文件 SPDX：GPL-2.0。
- 本项目 kernel::Module / module! / Vec::try_push 用法按该提交核对。

本项目新增的 Rust 源码及标有 GPL-2.0-only 的构建文件按 GPL-2.0-only 提供；同许可文本见 module/LICENSE。其余文档暂不声明统一开源许可，组内确认后再决定公开发布方式。本文件不改变上游代码许可。

统计函数、测试数据、日志格式与辅助流程是本初稿为课程任务新增的内容，框架借鉴已注明。source-verification.json 保存所核对上游文件的链接与校验值，不包含整份内核。
