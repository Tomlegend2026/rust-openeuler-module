# 用本项目学习 Rust

## 1 结构体与 impl

Statistics 把元素数、总和、最小值、最大值放在一起。RustTeam2 保存模块运行期间的状态。`impl kernel::Module for RustTeam2` 表示该类型实现了目标内核规定的初始化接口。

## 2 所有权

Vec 负责自己分配的内存。初始化函数里 values 是局部变量；`Ok(Self { values, summary })` 把它移动到模块字段。移动后不能再把旧局部变量当作另一个仍拥有数据的对象。模块实例最终被析构时，字段也被析构。

## 3 借用

`summarize(&values)` 只是把数据借给统计函数。参数 `&[u64]` 是只读切片，函数不拿走 Vec，也不复制整组数据。本项目的借用测试会确认输入保持不变。

## 4 Result 与问号

Result 表达成功或失败。`values.try_push(value)?` 的问号表示：成功继续；失败把错误向上传递，提前退出初始化。已创建的局部资源仍会正常析构。统计函数使用 checked_add，使超出 u64 范围成为可报告的错误。

注意：用户态普通 Vec 的示例写法与旧版内核 Vec 的可失败 API 不一样；不要直接把 std 示例粘进内核。

## 5 Drop

Drop 是资源清理的钩子。先运行类型自己的 drop 方法，再析构其字段。因此本模块在 Drop 中输出“卸载开始”，随后 Vec 自动释放内存。打印一句“释放成功”并不能代替真正的释放逻辑。

## 6 实际运行练习

有 Rust 的 Linux 环境中，在项目根目录运行：

```sh
cargo run --manifest-path learning/rust-basics/Cargo.toml
bash scripts/test-logic.sh
```

第一条是用户态教学程序，输出借用统计结果与作用域结束时的 Drop 信息；第二条验证真实共享统计函数的6个边界用例。两者都不加载内核模块。

## 7 六人各做一个解释或小改动

A：解释 values 为什么不能在移动后继续用。B：解释为什么本练习能用 std 而内核代码不行。C：解释 Cargo 与 Kbuild 各负责哪部分。D：把练习数据改成另一组，手算并验证。E：解释 u64::MAX 与再加1的区别。F：用自己的话说明 Drop 日志和完成释放之间的先后关系。

把实际练习与结论记入自己的目录，不提交编译产物。参考 [Rust Book](https://doc.rust-lang.org/book/) 的所有权、错误处理和 Drop 章节。
