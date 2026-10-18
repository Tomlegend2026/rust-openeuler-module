# 演示记录

本项目已经完成真实 openEuler 技术验收，演示时按以下顺序操作并录屏：

1. 展示 `uname -r` 和模块 `modinfo`，说明 vermagic 与运行内核一致。
2. 运行一次 `insmod`，展示 `lsmod` 和 `journalctl -k -n 20` 中的 `event=loaded`。
3. 运行 `rmmod`，展示 `event=unload_begin` 和模块从 `/proc/modules` 消失。
4. 展示 `lifecycle-20261018T112424Z-NBTnuw` 的 `result.txt`。
5. 展示 `negative-20261018T112425Z-NFqiar` 的 `result.txt`，解释两个命令返回 1 是预期错误。

当前仓库保留原始文本证据，没有冒充录制过不存在的录像。组员完成录屏后，将文件保存到本目录，并在下表补填：

| 文件 | 操作者 | 日期 | 内容 |
|---|---|---|---|
| 待填 | 待填 | 待填 | 构建与 modinfo |
| 待填 | 待填 | 待填 | 生命周期与负向测试 |
