# 任务2：Rust 内核模块在 openEuler 中的动态装卸

这是一份供六人小组检查、复现和修改的完整初稿。已经提供 Rust 模块、构建文件、测试脚本、学习示例、实验报告正文与汇报讲稿。

**状态：核心实验已实测通过：openEuler 实验内核成功启动，rust_team2.ko 编译成功，10 轮动态加载与卸载全部通过，原始日志已保存。组员独立复现、错误用例及个人贡献仍需补充。**

## 不知道从哪里开始时

先读 [从零开始](docs/00-从零开始.md)，再看 [六人检查分工](docs/01-任务分工.md)。组长只需先落实一件事：让 B、C 准备一台大家能复用的 openEuler 实验虚拟机。其他人同时读代码、练习和报告，不必各自搭一套不同环境。

## 本模块做什么

模块名为 `rust_team2`。加载时分配并持有 `[3, 1, 4, 1, 5, 9]`，计算元素数、总和、最小值、最大值，并写入内核日志。卸载时输出清理开始日志，随后 Rust 自动析构模块字段并释放向量内存。

这组数据预期得到 `count=6 sum=23 min=1 max=9`。这是算法预期，不是已经得到的 openEuler 实验输出。统计逻辑对空输入和总和溢出返回错误。

## 重要入口

| 内容 | 文件 |
|---|---|
| 零基础行动顺序 | [从零开始](docs/00-从零开始.md) |
| 组员如何检查 | [任务分工](docs/01-任务分工.md) |
| 完成实测后如何接手 | [组员接手指南](docs/07-组员接手指南.md) |
| 目标系统搭建 | [openEuler 环境搭建](environment/搭建步骤.md) |
| 本机实际搭建进展 | [2026-10-06 搭建记录](environment/2026-10-06实际搭建记录.md)、[实际版本](environment/版本记录.md) |
| 编译、装卸、排障 | [复现流程](docs/03-环境与复现流程.md) |
| 模块实现与原理 | [源码说明](module/README.md)、[原理讲解](docs/05-模块原理.md) |
| Rust 学习 | [基础讲义](learning/Rust基础与练习.md) |
| 当前真实验证情况 | [验证记录](tests/当前验证记录.md) |
| openEuler 实测结果表 | [2026-10-06 测试结果](tests/测试结果-20261006.md) |
| 可编辑报告正文 | [实验报告](report/实验报告.md) |
| 汇报讲稿与演示 | [汇报与演示](presentation/汇报与演示.md) |
| 上传与合并修改 | [GitHub 协作指南](CONTRIBUTING.md) |

## 目录

```text
module/        Rust 内核入口、统计逻辑、Kbuild 和 Makefile
scripts/       环境检查、构建、装卸循环和日志处理
learning/      公共教程、可运行练习和 A～F 个人笔记区
environment/   固定源码基线、安装步骤和待填写运行环境
tests/         逻辑/辅助工具测试、内核测试计划和结果记录
evidence/      实测日志、截图、录像索引
report/        报告初稿
presentation/  汇报讲稿及现场操作顺序
docs/          分工、检查清单、原理、引用
.github/       任务 Issue 与 PR 模板
```

## 运行入口

只学习统计逻辑，不需要管理员权限，也不加载内核：

```sh
bash scripts/test-logic.sh
cargo run --manifest-path learning/rust-basics/Cargo.toml
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

openEuler 内核实验需先完成搭建步骤，启动自己编译的匹配内核，再执行：

```sh
export RUSTUP_TOOLCHAIN=1.73.0
bash scripts/build-module.sh "$HOME/os-lab/kernel"
sudo bash scripts/test-lifecycle.sh module/rust_team2.ko 10
```

初稿面向 x86_64 openEuler，源码基线见 [baseline.env](environment/baseline.env)。不要在现有 Ubuntu/WSL 内核中加载本模块。不要把主机逻辑测试通过写成内核实验成功。只有完成实测并上传证据，才可把状态改成已完成。
