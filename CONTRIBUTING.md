# GitHub 协作指南

本目录是独立仓库根目录。小组仓库为 https://github.com/Tomlegend2026/rust-openeuler-module ，本地已初始化 main 并配置 origin。组长在 GitHub 仓库 Settings → Collaborators 邀请另外五位成员。下面的首次上传说明仅供新环境参考，已初始化的目录不要重复操作。

## 首次上传

在 GitHub 新建空仓库（不要预先生成 README），邀请五位成员为协作者。在本目录打开终端，先用 `git rev-parse --show-toplevel` 检查是否已处于其他仓库中；若显示上级课程仓库，先确定仓库边界，不重复初始化嵌套仓库。

确认本目录为拟建的独立仓库后执行：

```sh
git init -b main
git add .
git status
git commit -m "docs: initialize task2 project structure"
git remote add origin https://github.com/Tomlegend2026/rust-openeuler-module.git
git push -u origin main
```

先把地址占位符换成真实仓库地址。检查暂存列表没有隐私、镜像或构建产物。不要把账号密码或令牌写进仓库地址。

## 日常协作

每项任务建立 Issue，写负责人、验收标准、依赖和交付目录。一人一个功能分支，一个 PR 聚焦一项任务。

```sh
git clone https://github.com/Tomlegend2026/rust-openeuler-module.git
cd rust-openeuler-module
git switch main
git pull --ff-only
git switch -c docs/a-learning-notes
# 编辑自己负责的文件后，按实际路径暂存
git add learning/A/
git commit -m "docs: add ownership learning notes"
git push -u origin docs/a-learning-notes
```

然后在 GitHub 发起 PR，按模板填写，由分工表中的验收人评审。分支示例：env/b-openeuler、build/c-kbuild、feat/d-module、test/e-lifecycle、docs/f-report。

组长可在 GitHub 设置 main 保护和至少一次评审（取决于账号/仓库支持），这些设置不会由本地模板自动启用。通过评审后合并，其他人回 main 拉取。未提交修改先提交或妥善暂存，发生冲突时找相关维护人共同处理，不强推覆盖他人工作。

## 提交与评审约定

- 标题可用 docs:、feat:、fix:、test:、build:；清楚描述实际改变。
- 修改接口、路径、日志或构建步骤时，同步更新说明和测试。
- 环境与模块相关 PR 写明版本及实测情况；未测试就写未测试。
- 首次模板搭建只检查结构和链接，不声称已完成 Linux 编译运行。
- 不提交完整内核、虚拟机磁盘、ISO、工具链、`.ko`、Cargo target、密钥或大视频。
- 截图与日志使用稳定命名；Word/PPT 最终文件由 F 汇总，避免多人同时修改二进制文件。
- 完成并验收后再创建 v1.0-demo 等标签，记录可复现提交。
