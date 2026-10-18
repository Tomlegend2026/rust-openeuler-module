# 真实终端截图索引

技术证据已经以原始文本日志保存到 `evidence/logs/`，包括构建、10 轮生命周期和两个负向用例。当前目录不放伪造图片；提交前由小组成员在真实 openEuler SSH 终端中补充至少两张截图：

1. `01-build-and-modinfo.png`：显示 `uname -r`、`modinfo module/rust_team2.ko` 和 vermagic 匹配。
2. `02-lifecycle-and-negative.png`：显示生命周期脚本退出码 0，以及负向脚本的 `still_loaded` 和 `still_absent`。

截图文件名固定后，在报告和演示稿中引用相同名称。截图只用于展示，结论以同目录下的原始日志、`audit.json` 和校验值为准。
