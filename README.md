# Rust 内核模块在 openEuler 中的动态装卸

操作系统课程任务2：学习 Rust，编写可动态加载、卸载的内核模块，并在 openEuler 实测。

`rust_team2` 加载时保存 `[3, 1, 4, 1, 5, 9]`，计算 `count=6 sum=23 min=1 max=9` 并写入内核日志；卸载时进入 `Drop`，随后模块字段析构。项目没有图形界面，演示通过终端观察模块列表与日志。

**已完成：**2026-10-18在openEuler重新构建成功，10轮动态装卸、两个负向用例通过。Rust统计逻辑6项、Python工具测试13项通过，原始证据已保存。2026-10-19更新本指南，没有因此重新执行内核实测。

**最新交付位于 [`codex/rust-module-delivery-20261018` 分支](https://github.com/Tomlegend2026/rust-openeuler-module/tree/codex/rust-module-delivery-20261018)。** 未合入main前，请切换该分支查看；首次下载使用下面指定分支的clone命令。私有仓库需组长邀请，组员使用自己的账号认证。

本README包含从下载到测试的完整流程。本仓库**不提供现成虚拟机下载**，下载ISO后还要安装openEuler并构建实验内核。

## 先分清命令在哪里执行

| 位置 | 做什么 |
|---|---|
| Windows浏览器 | 下载VMware和ISO，查看GitHub |
| Windows PowerShell | 可选：核验ISO的SHA256 |
| VMware窗口 | 创建和启动虚拟机、安装openEuler、选择启动内核 |
| **VMware里的openEuler终端** | **安装Linux依赖、获取源码、编译内核和模块、执行装卸与测试** |

除明确标记为Windows PowerShell的代码块外，下面的命令都在**openEuler终端的Bash中执行**。不要在Windows PowerShell中输入dnf、insmod或rmmod。

- `$HOME`是当前Linux账号的家目录，不必替换；账号不需要叫team2。自己的账号对应自己的项目目录。
- sudo要求输入自己的openEuler密码，输入时不显示字符或星号，输完按Enter。不要在仓库中填写密码。
- 按阶段执行，检查结果后再继续。某条命令失败，先保存错误并处理，不要直接跳到后面的安装或重启。
- 通过Windows SSH登录openEuler后也可以操作；登录后的命令在远端Linux执行。

## 选择复现路线

| 当前情况 | 阅读顺序 |
|---|---|
| 没有openEuler虚拟机 | A下载 → B完整搭建 → C模块装卸 → D测试 |
| 已有openEuler，但没有Rust实验内核 | B安装依赖及源码 → B构建、安装和启动 → C → D |
| 已有本组配套实验内核和完整内核构建目录 | 直接C模块构建与装卸，再执行D测试 |
| 只负责Rust学习、源码讲解或材料审核 | D的逻辑测试、文末学习材料；不必每人重新编译整个内核 |

### 已有配套环境：快捷入口

前提：正在运行x86_64 openEuler Rust实验内核，项目已存在，且`$HOME/os-lab/kernel`是对应的**完整源码及构建目录**，只有普通内核头文件包不够。

**执行位置：openEuler终端。**

```bash
cd "$HOME/os-lab/rust-openeuler-module"
source "$HOME/.cargo/env"
export RUSTUP_TOOLCHAIN=1.73.0
uname -r
bash scripts/check-env.sh "$HOME/os-lab/kernel"
bash scripts/build-module.sh "$HOME/os-lab/kernel"
```

检查与构建通过后，按C节人工装卸，再运行D节的10轮和负向测试。

## A. 在Windows下载并准备安装软件

**以下链接在Windows浏览器打开：**

| 内容 | 官方链接 | 说明 |
|---|---|---|
| VMware Workstation Pro | [下载入口](https://support.broadcom.com/group/ecx/productdownloads?freeDownloads=true&subfamily=VMware+Workstation+Pro)、[官方下载说明](https://knowledge.broadcom.com/external/article/368667/download-and-license-vmware-desktop-hyper.html) | 下载Windows安装程序并安装，官方要求Broadcom账号登录；已有可用版本可以继续使用。 |
| openEuler 24.03 LTS x86_64标准DVD镜像 | [ISO直链，约3.9 GiB](https://repo.openeuler.org/openEuler-24.03-LTS/ISO/x86_64/openEuler-24.03-LTS-x86_64-dvd.iso) | 这是系统安装盘，不是预装虚拟机。不要误选ARM、everything、debug或netinst版。 |
| ISO校验文件 / 备用目录 | [SHA256](https://repo.openeuler.org/openEuler-24.03-LTS/ISO/x86_64/openEuler-24.03-LTS-x86_64-dvd.iso.sha256sum)、[目录](https://repo.openeuler.org/openEuler-24.03-LTS/ISO/x86_64/) | 直链不可用时从目录选同名文件。 |

本组镜像的SHA256已与官方核对：

```text
786b9683659512e71c978c34aea806a97ed6cacf04e1b0a22017a50eec582cbe
```

**仅下面这条在Windows PowerShell执行**。先换成你实际保存ISO的位置，再核对Hash：

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'D:\Downloads\openEuler-24.03-LTS-x86_64-dvd.iso'
```

在VMware新建虚拟机，选择这个ISO，按照向导安装openEuler。开启可联网的网络配置，例如NAT；创建自己的普通管理员用户并记好密码。安装完成后从虚拟硬盘启动，若仍进入安装程序，在VMware设置里断开ISO的“启动时连接”。

本组实测为4 vCPU、6 GiB内存、60 GiB动态磁盘，使用裁剪过的VMware实验内核配置；完整发行版配置需要更多资源，编译耗时和占用因配置而异。具体软件版本及其官方入口另见[下载链接与安装位置](environment/下载链接与安装位置.md)。

## B. 从零搭建openEuler实验内核

**从这里开始，所有命令均在VMware里的openEuler终端执行。** 若系统启动后只有文字命令行，该界面本身就是终端。

本节按操作系统、依赖、固定源码、Rust、配置、构建、安装的顺序执行。先获取本组仓库，方便后面引用配置与脚本：

```bash
sudo dnf install git
mkdir -p "$HOME/os-lab"
cd "$HOME/os-lab"
git clone --branch codex/rust-module-delivery-20261018 https://github.com/Tomlegend2026/rust-openeuler-module.git
cd rust-openeuler-module
pwd
```

输出应为`/home/你的用户名/os-lab/rust-openeuler-module`。已有项目时不要重复克隆或覆盖改动。下面配置用到的本组文件均来自这个目录。

2026-10-06 已在独立 x86_64 openEuler 虚拟机完成构建、启动及模块装卸。下面保留通用搭建流程；本机采用 4 vCPU、6GB 内存、60GiB 动态磁盘，并裁剪可选驱动、关闭调试信息，实际过程和最终配置见 [实测记录](environment/2026-10-06实际搭建记录.md)。若编译完整发行版驱动集合，建议准备更多内存与磁盘。六人可共享版本一致的实验环境，并由第二名成员独立复现。

### 1 安装操作系统

具体软件下载入口、标准 DVD 镜像直链、SHA256 及 Windows/openEuler 操作位置见 [下载链接与安装位置](environment/下载链接与安装位置.md)。本仓库不提供已安装好的虚拟机。

从 [openEuler 官方下载入口](https://www.openeuler.org/zh/download/) 选择 x86_64 的 openEuler 24.03 LTS 系列安装镜像，核对镜像提供的校验值，按虚拟机软件向导安装。有现成 openEuler 先检查，避免重复安装。记录完整发行版、架构、镜像来源与校验值。

安装开发工具前保存快照。镜像与虚拟机磁盘放仓库外；日常用普通用户，只有软件包安装、内核安装和模块装卸需要 sudo。

```sh
cat /etc/os-release
uname -m
uname -r
```

本项目选择 openEuler 自有内核源码构建 Rust 实验内核，不把 Ubuntu/WSL 内核当 openEuler 内核。不要求系统最初自带内核已经支持 Rust。

### 2 安装构建依赖

以下包名作为该系列的候选清单，仓库变体可能不同。若 dnf 报某包不存在，保存错误，使用 `dnf search` / `dnf provides` 查实际包名，不忽略错误继续。

```sh
sudo dnf install git make gcc gcc-c++ clang llvm llvm-devel clang-devel lld   bc bison flex elfutils-libelf-devel openssl-devel ncurses-devel   perl python3 cpio rsync curl tar xz kmod dracut grubby
clang --version
ld.lld --version
llvm-config --version
```

如使用额外 LLVM 安装，整个内核和外部模块必须使用同一套 PATH、Clang 和 libclang；记录实际版本。内核检查目标会进一步验证兼容性。不要只根据最低版本猜测一定可编译。

### 3 获取固定的内核源码

仓库内 environment/baseline.env 固定了源码提交。GitHub 镜像分支名是 `openEuler-24.03_LTS`，它不是拼写为连字符的同名分支。以下直接获取提交，避免分支变化。

```sh
mkdir -p "$HOME/os-lab"
git init "$HOME/os-lab/kernel"
cd "$HOME/os-lab/kernel"
git remote add origin https://github.com/openeuler-mirror/kernel.git
git fetch --depth=1 origin 6e0c18da64fd9919a51f8f2216a371503a5e2763
git checkout --detach FETCH_HEAD
git rev-parse HEAD
```

首次执行上述初始化；已有仓库不要重复添加 origin。若使用 Gitee 下载来源，须确认获取到同一提交；不能把不同分支源码直接替换后仍声称采用固定版本。内核本身可能很大，不要加入作业仓库。

### 4 配置 Rust 工具链

**执行位置：openEuler终端，普通用户，不加sudo。** 首次安装rustup时使用[官方Linux安装入口](https://rustup.rs/)提供的安装器，并选择本组固定工具链：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain 1.73.0
source "$HOME/.cargo/env"
```

已有rustup时不必重复执行安装器。随后安装固定版本与组件：

```sh
rustup toolchain install 1.73.0 --profile minimal --component rust-src --component rustfmt
export RUSTUP_TOOLCHAIN=1.73.0
rustc --version
cargo install --locked --version 0.65.1 bindgen-cli
bindgen --version
cd "$HOME/os-lab/kernel"
make LLVM=1 rustavailable
```

`RUSTUP_TOOLCHAIN` 应在整个编译会话设置，之后编译外部模块时仍设置；仅在内核目录 rustup override 不一定作用于从作业目录发起的构建。新终端需要重新 export。内核通过自身构建系统启用所需 Rust 特性，不要自行添加 RUSTC_BOOTSTRAP 绕过构建步骤。

如果找不到 libclang，定位实际库并设置 LIBCLANG_PATH（例如通过 llvm-config --libdir 查候选），以实际 `rustavailable` 输出为准。

### 5 配置实验内核

**与本组原VMware硬件配置匹配时，可选择使用已实测的裁剪配置：**

```bash
cd "$HOME/os-lab/kernel"
cp "/boot/config-$(uname -r)" "$HOME/os-lab/stock-kernel.config"
cp "$HOME/os-lab/rust-openeuler-module/environment/experiment-kernel.config" .config
make LLVM=1 olddefconfig
make LLVM=1 rustavailable
grep -E '^(CONFIG_RUST|CONFIG_MODULES|CONFIG_MODULE_UNLOAD|CONFIG_LOCALVERSION)=' .config
```

确认RUST、MODULES、MODULE_UNLOAD均为y。此配置只针对原VMware环境，必须确认磁盘、根文件系统及网卡驱动适配；换控制器、文件系统或虚拟化软件时不能视为通用配置。选择此路线并检查通过后，跳到第6部分，不要再用下面的通用配置命令覆盖它。

**需要保留自己系统完整硬件支持时，使用下面的通用配置路线：**

本初稿采用源码目录内构建。复制当前系统配置作为硬件支持基础，保留磁盘、根文件系统和虚拟机驱动；不要用过度裁剪配置导致新内核无法启动。

```sh
cd "$HOME/os-lab/kernel"
cp "/boot/config-$(uname -r)" .config
make LLVM=1 olddefconfig
scripts/config --enable MODULES --enable MODULE_UNLOAD   --disable MODVERSIONS --disable CFI_CLANG --disable GCC_PLUGINS   --disable RANDSTRUCT --enable RANDSTRUCT_NONE --disable DEBUG_INFO_BTF   --enable RUST --enable SAMPLES --enable SAMPLES_RUST --module SAMPLE_RUST_MINIMAL   --set-str LOCALVERSION '-team2-rust' --disable LOCALVERSION_AUTO
make LLVM=1 olddefconfig
make LLVM=1 menuconfig
```

以上是不改变宿主系统的实验内核配置调整。菜单中再次确认 Rust support 和模块支持；若 RUST 消失，先查依赖，不能当作已经启用。固定源码中的 Rust 依赖 `!MODVERSIONS` 等条件，因此不能照搬最新上游文档的兼容结论。

```sh
grep -E '^(CONFIG_RUST|CONFIG_MODULES|CONFIG_MODULE_UNLOAD|CONFIG_LOCALVERSION)=' .config
```

前三项必须为 y。若 /boot 没有配置文件，检查 `/proc/config.gz` 或安装镜像对应的内核配置来源，不能编造配置。如构建报发行版证书文件缺失，应处理实际证书路径并遵守当前签名策略；本流程不提供默认关闭签名的捷径。

### 6 完整编译、安装并启动

**执行位置：openEuler终端。** 内核编译比本组模块编译耗时更长。先构建，不要直接安装：

```bash
source "$HOME/.cargo/env"
export RUSTUP_TOOLCHAIN=1.73.0
cd "$HOME/os-lab/kernel"
set -o pipefail
make LLVM=1 -j2 2>&1 | tee "$HOME/os-lab/kernel-build.log"
```

看到错误时先处理，不继续安装。成功后检查产物：

```bash
make -s LLVM=1 kernelrelease
ls -lh arch/x86/boot/bzImage System.map Module.symvers rust/kernel.o rust/libmacros.so
```

本组实测版本是`6.6.0-team2-rust+`，末尾`+`也是版本的一部分。以你本次构建输出为准，后面模块必须与实际运行版本匹配。普通头文件包或仅运行modules_prepare不能替代完整Rust内核构建。

首次安装前在VMware保存快照，保留原内核作为回退。下面命令使用当前用户的路径。**不要直接套用原机器维护脚本`install-kernel-vm.sh`，它写死了team2账号路径和原构建状态文件。** 已装好配套内核的成员跳过安装。

下面整个代码块在openEuler终端执行，会安装实验内核并新增启动项；任一步失败会停止这个代码块。若提示目标版本已存在，先检查已有安装，不要覆盖：

```bash
(
  set -e
  cd "$HOME/os-lab/kernel"
  release=$(make -s LLVM=1 kernelrelease)
  test -n "$release"
  printf '准备安装版本：%s\n' "$release"
  test ! -e "/boot/vmlinuz-$release"
  test ! -e "/lib/modules/$release"
  test -s arch/x86/boot/bzImage
  sudo env "PATH=$PATH" "RUSTUP_HOME=$HOME/.rustup" \
    "CARGO_HOME=$HOME/.cargo" RUSTUP_TOOLCHAIN=1.73.0 \
    make LLVM=1 modules_install
  sudo install -m 644 arch/x86/boot/bzImage "/boot/vmlinuz-$release"
  sudo install -m 644 System.map "/boot/System.map-$release"
  sudo install -m 644 .config "/boot/config-$release"
  sudo depmod "$release"
  sudo dracut --kver "$release" "/boot/initramfs-$release.img"
  sudo grubby --add-kernel="/boot/vmlinuz-$release" \
    --initrd="/boot/initramfs-$release.img" \
    --title="openEuler Rust experiment ($release)" --copy-default
  sudo grubby --info="/boot/vmlinuz-$release"
  echo '安装完成。保留原内核，重启后选择实验内核启动项。'
)
```

确认无错误、对应内核和initramfs已生成，再执行：

```bash
sudo reboot
```

虚拟机会重启，SSH会断开。**在VMware控制台启动菜单中选`openEuler Rust experiment (...)`实验内核**，不要继续启动原内核。若启动失败，选择原内核或回到快照排障。

重新登录openEuler并打开终端：

```bash
uname -r
cat "$HOME/os-lab/kernel/include/config/kernel.release"
```

两个输出必须相同。仅完成编译、却没有启动实验内核，不算具备模块装卸条件。

### 7 转到作业仓库

回到B节开始时已克隆的小组仓库，不要重复clone：

```bash
cd "$HOME/os-lab/rust-openeuler-module"
```

继续下面的C节构建和装卸本组模块。项目应位于Linux文件系统的无空格路径，不能将Windows的`D:\...`作为虚拟机内的项目路径。

将所有实际版本填入 [版本记录](environment/版本记录.md)，保存安装/构建日志。先完成一次人工装卸再跑循环，遇到失败保存原始错误后排障。

## C. 编译模块并验证动态装卸

### 1 检查环境

**执行位置：openEuler终端。** 先回到项目根目录并恢复工具链环境：

```bash
cd "$HOME/os-lab/rust-openeuler-module"
source "$HOME/.cargo/env"
export RUSTUP_TOOLCHAIN=1.73.0
```

然后执行：

```sh
export RUSTUP_TOOLCHAIN=1.73.0
bash scripts/check-env.sh "$HOME/os-lab/kernel"
```

脚本核对系统、架构、源码提交、关键配置、Rust/bindgen 版本和完整构建产物，再运行内核 Rust 可用性检查。任何失败都应先处理。此检查通过仅代表构建前提满足，不代表模块已经加载成功。

### 2 编译本组模块

```sh
bash scripts/build-module.sh "$HOME/os-lab/kernel"
modinfo module/rust_team2.ko
```

底层使用 Kbuild：`make -C module KDIR=内核绝对路径 LLVM=1`。不使用 cargo build 构建内核模块。日志自动进入 evidence/logs/，记录源码和 .ko 校验值。

### 3 人工验证一次

先在openEuler终端执行`lsmod | grep '^rust_team2 '`，无输出表示尚未加载；若有输出，先确认实例归属，不要并发操作别人的测试。

开两个openEuler终端，第二个也先执行`cd "$HOME/os-lab/rust-openeuler-module"`。第一个观察实时日志（按Ctrl+C停止观察，不会因此卸载模块）：

```sh
sudo dmesg -w
```

第二个执行：

```sh
sudo insmod module/rust_team2.ko
lsmod | grep '^rust_team2 '
sudo rmmod rust_team2
lsmod | grep '^rust_team2 '
```

最后一个 grep 没有输出且返回1是正常结果。日志应包含以下片段（仅预期，不是实测记录）：

```text
[rust_team2] event=loaded count=6 sum=23 min=1 max=9
[rust_team2] event=unload_begin retained=6 sum=23
```

内核可能添加时间戳、等级和模块前缀。`unload_begin` 在字段析构前输出，不能把这行文字当成已经完成内存释放的证明。

### 4 自动验证10轮

人工装卸成功且当前模块不在系统中，再运行：

```sh
sudo bash scripts/test-lifecycle.sh module/rust_team2.ko 10
```

脚本拒绝非 openEuler、版本不匹配、已加载的同名模块或另一个本项目测试进程。每轮检查模块存在与消失；只清理本轮脚本自己成功加载的模块；遇错停止，不强制卸载。

每次生成单独目录：commands.log（命令过程）、rounds.tsv（成功轮次）、before/after/new/final.log（日志快照与本次增量）、result.txt（最终返回码）。发生中途失败时某些后续文件可能尚未生成，不能把缺失文件当成测试通过。

脚本对新增日志检查预期加载与卸载次数，并查找 BUG/Oops/WARNING/kernel panic 关键词。环形日志覆盖导致边界不明确时直接报告失败。通过后仍需人工看 new.log；有限循环和关键词筛查不是完整的内存泄漏检测。

### 5 自动负向测试

**执行位置：openEuler终端的项目根目录，确认刚才的模块已经正常卸载。**

```bash
sudo bash scripts/test-negative.sh module/rust_team2.ko
```

重复加载应返回非零且仍为`still_loaded`；卸载不存在模块应返回非零且仍为`still_absent`。本组已记录的两个用例退出码均为1，这是预期行为。测试脚本整体应显示PASS，并在新建的`evidence/logs/negative-.../result.txt`记录`EXIT_STATUS=0`。

不要删除用例的错误输出，也不要把预期非零当成整个实验失败。

### 6 复现与排障

| 问题 | 处理方向 |
|---|---|
| 检查提示 Ubuntu/WSL | 这是主机逻辑测试环境；转到 openEuler VM |
| Rust 或 bindgen 不匹配 | 设置 RUSTUP_TOOLCHAIN=1.73.0，检查 PATH 及 bindgen 0.65.1 |
| .config 中没有 CONFIG_RUST | 检查 rustavailable 与固定内核 Kconfig 依赖 |
| 缺 rust/kernel.o、rust/libmacros.so 等 | 完整构建内核；普通头文件包不能替代 Rust 构建产物 |
| Module::init、Vec API 报错 | 确认是否使用固定提交；不要与最新版 KVec 接口混用 |
| invalid module format | 对照 uname、kernelrelease、vermagic、架构和配置，重新编译 |
| Unknown symbol | 核对目标构建目录、Module.symvers 和依赖 |
| 签名校验失败 | 按当前启动和模块签名策略签名，不默认关闭保护 |
| 卸载失败 | 保留错误与模块状态，检查引用，禁止强制卸载 |

非作者按照本页独立操作，把真实结果填入 tests/测试结果模板.md。若需要修改源码基线，统一更新 baseline.env、source-verification.json、配置、构建说明和测试记录；不能只绕过检查。

## D. 核验、截图和独立复现记录

**执行位置：openEuler终端，项目根目录。** 自动测试会打印`Evidence:`路径，每次生成新目录。保存本次实际目录，不要将仓库已有的历史日志当成自己的结果。

正向目录中应有commands.log、rounds.tsv、before.log、after.log、new.log、final.log和result.txt。离线复核时，先将下面示例路径换成**本次测试实际生成的目录**：

```bash
python3 scripts/verify-evidence.py evidence/logs/lifecycle-实际日期与随机后缀 --rounds 10
```

核验成功只是说明保存的证据一致，不会重新运行内核模块。

### 不需要管理员权限的学习与工具测试

以下命令在openEuler项目根目录执行，不加sudo、不加载模块：

```bash
source "$HOME/.cargo/env"
export RUSTUP_TOOLCHAIN=1.73.0
bash scripts/test-logic.sh
cargo run --manifest-path learning/rust-basics/Cargo.toml
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Rust统计逻辑当前为6项测试，Python辅助工具为13项。用户态示例演示所有权、借用和Drop。独立编译纯计算库可能出现dead_code警告，因为该步骤未调用其中函数；这不代表内核编译失败，也不要通过关闭检查掩盖真实错误。

### 每位复现者交什么

| 材料 | 应包含什么 |
|---|---|
| 操作记录 | 本人、日期、系统版本、运行内核、Rust与LLVM版本、源码提交 |
| 构建结果 | 本次构建日志、modinfo、模块SHA256 |
| 实际运行 | 本次10轮及负向测试新生成的证据目录 |
| 演示素材 | 模块加载、统计日志、卸载后消失的真实截图或连续录屏 |
| 问题记录 | 完整错误和解决过程，不能只写“成功” |

示例日志只表示预期结果。`dmesg`会保留历史内容，旧日志不能单独证明本次成功；应结合命令退出码、模块列表和自动提取的新日志判断。

模块中的`unload_begin`先于Vec字段析构输出；有限轮次和关键字检查不能排除所有内存泄漏、并发或内核缺陷。本模块没有设备I/O、后台线程或外部输入，结论只覆盖已实现的统计和生命周期。

### 初学者常见问题

| 现象 | 处理方向 |
|---|---|
| Windows不认识dnf/insmod | 换到VMware里的openEuler终端 |
| sudo输入密码没有星号 | 正常，直接输入并按Enter |
| GitHub提示仓库不存在 | 确认已接受组长邀请，用自己的账号认证 |
| 包不存在或下载失败 | 先检查虚拟机联网和对应发行版软件源，保存完整错误 |
| 刚重启后找不到rustc | 重新source ~/.cargo/env并设置RUSTUP_TOOLCHAIN |
| lsmod查不到模块 | 加载前、卸载后正常；加载后查不到则需排障 |
| 循环测试提示模块已加载 | 确认是否为自己手工测试留下的实例，正常卸载后再跑 |
| 新内核无法启动 | 在VMware启动菜单选原内核，或回到安装前快照检查驱动和initramfs |

## E. 项目材料与小组收尾

| 内容 | 入口 |
|---|---|
| 已完成内容和组员待办 | [交付状态](docs/08-交付状态与组员待办.md) |
| 六人建议分工和接手 | [分工](docs/01-任务分工.md)、[接手指南](docs/07-组员接手指南.md) |
| Rust学习及源码 | [基础讲义](learning/Rust基础与练习.md)、[内核入口](module/rust_team2.rs)、[统计逻辑](module/statistics.rs)、[原理讲解](docs/05-模块原理.md) |
| 本组实际环境 | [版本记录](environment/版本记录.md)、[搭建记录](environment/2026-10-06实际搭建记录.md) |
| 历史实测结果 | [2026-10-18结果](tests/测试结果-20261018.md) |
| 正式报告与正文 | [Word报告](deliverables/任务2%20Rust内核模块实验报告.docx)、[报告正文](report/实验报告.md) |
| 22页源码走读详细版 | [PowerPoint](deliverables/源码走读详细版/任务2%20Rust内核模块-源码走读详细版.pptx)、[离线HTML](deliverables/源码走读详细版/Rust内核模块-源码走读.html) |
| 现场汇报 | [讲稿和演示顺序](presentation/汇报与演示.md) |
| 协作和来源 | [GitHub协作](CONTRIBUTING.md)、[来源与许可](THIRD_PARTY_NOTICES.md) |

共同技术基线已完成，组员仍需如实填写姓名学号、个人学习和贡献，完成独立复现、真实演示素材、报告审核和计时彩排。A～F只是角色占位。

在项目根目录执行`python3 scripts/package-submission.py`，可生成`build/rust-openeuler-module-submission.zip`，包含源码、文档和保存的证据，不包含虚拟机及编译产物。
