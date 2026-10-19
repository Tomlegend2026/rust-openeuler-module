# Rust 内核模块在 openEuler 中的动态装卸

本项目使用 Rust 实现可动态加载与卸载的 Linux 内核模块 `rust_team2`，在 openEuler 中完成构建和运行验证。仓库包含模块源码、构建配置、测试脚本、Rust 学习示例、实验报告与演示材料。

模块加载时创建并保存数据 `[3, 1, 4, 1, 5, 9]`，计算元素数量、总和、最小值和最大值，并写入内核日志。卸载时执行 `Drop`，随后析构模块字段。通过这个实例可以观察初始化、所有权转移、只读借用、错误处理与资源清理的完整过程。

## 功能与验证结果

| 项目 | 验证结果 |
|---|---|
| 目标系统 | openEuler 24.03 LTS，x86_64 |
| 实验内核 | `6.6.0-team2-rust+` |
| 模块构建 | 使用目标内核 Kbuild 生成 `rust_team2.ko` |
| 统计结果 | `count=6 sum=23 min=1 max=9` |
| 动态加载与卸载 | 连续10轮通过 |
| 负向测试 | 重复加载、卸载不存在的模块均按预期拒绝，模块状态正确 |
| 逻辑与工具测试 | Rust统计逻辑6项、Python辅助工具13项通过 |

2026-10-19通过 Windows PowerShell SSH 完成再次复现，八个阶段全部通过，最终退出码为0，模块已卸载。详见 [本次复现记录与原始日志](tests/复现记录-20261019.md)；此前实测见 [2026-10-18测试结果](tests/测试结果-20261018.md)。

## 复现指南

以下流程覆盖软件下载、虚拟机安装、内核构建、模块装卸与结果核验。已有配套环境可直接使用快捷入口。实验环境使用官方 openEuler 镜像安装，所需软件与镜像均提供官方下载链接。

### 命令执行位置

| 位置 | 做什么 |
|---|---|
| Windows浏览器 | 下载VMware和ISO，查看GitHub |
| Windows PowerShell | 可选：核验ISO的SHA256 |
| VMware窗口 | 创建和启动虚拟机、安装openEuler、选择启动内核 |
| **VMware里的openEuler终端** | **安装Linux依赖、获取源码、编译内核和模块、执行装卸与测试** |

除明确标记为Windows PowerShell的代码块外，所有命令均在**openEuler终端的Bash中执行**。Windows用于下载与运行VMware，openEuler用于构建和运行内核模块。

- `$HOME`表示当前Linux用户的家目录，文中的命令适用于各自创建的普通管理员账号。
- `sudo`使用当前openEuler账号的密码。输入时终端不显示字符，完成后按Enter。
- 按阶段执行并检查输出。命令失败时保留错误信息，解决后继续下一阶段。
- 通过Windows SSH登录openEuler后也可以操作；登录后的命令在远端Linux执行。

### 复现路线

| 当前情况 | 阅读顺序 |
|---|---|
| 没有openEuler虚拟机 | A下载 → B完整搭建 → C模块装卸 → D测试 |
| 已有openEuler，但没有Rust实验内核 | B安装依赖及源码 → B构建、安装和启动 → C → D |
| 已有配套实验内核和完整内核构建目录 | 直接C模块构建与装卸，再执行D测试 |
| 学习Rust机制或阅读源码 | D节的逻辑测试及文末源码、原理文档 |

### 已有配套环境：快捷入口

前提：正在运行x86_64 openEuler Rust实验内核，项目已存在，且`$HOME/os-lab/kernel`是对应的**完整源码及构建目录**，只有普通内核头文件包不够。

也可在 SSH 登录后的 openEuler Bash 中执行交互式完整验证：

```bash
cd "$HOME/os-lab/rust-openeuler-module"
bash scripts/reproduce-session.sh
```

脚本依次检查环境、重新编译模块、运行逻辑测试、演示装卸、运行10轮测试与负向测试、核验日志并检查最终状态。按提示输入 sudo 密码和 Enter；完成时应显示 `REPRODUCTION_PASS` 与 `EXIT_STATUS=0`。每次运行的独立记录保存在 `evidence/logs/reproduction-*`，脚本不会自动上传。

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
| openEuler 24.03 LTS x86_64标准DVD镜像 | [ISO直链，约3.9 GiB](https://repo.openeuler.org/openEuler-24.03-LTS/ISO/x86_64/openEuler-24.03-LTS-x86_64-dvd.iso) | 这是系统安装盘，不是预装虚拟机。使用与实验基线一致的x86_64标准DVD镜像。 |
| ISO校验文件 / 备用目录 | [SHA256](https://repo.openeuler.org/openEuler-24.03-LTS/ISO/x86_64/openEuler-24.03-LTS-x86_64-dvd.iso.sha256sum)、[目录](https://repo.openeuler.org/openEuler-24.03-LTS/ISO/x86_64/) | 直链不可用时从目录选同名文件。 |

镜像SHA256：

```text
786b9683659512e71c978c34aea806a97ed6cacf04e1b0a22017a50eec582cbe
```

**仅下面这条在Windows PowerShell执行**。先换成你实际保存ISO的位置，再核对Hash：

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'D:\Downloads\openEuler-24.03-LTS-x86_64-dvd.iso'
```

在VMware新建虚拟机，选择这个ISO，按照向导安装openEuler。开启可联网的网络配置，例如NAT；创建自己的普通管理员用户并记好密码。安装完成后从虚拟硬盘启动，若仍进入安装程序，在VMware设置里断开ISO的“启动时连接”。

实测虚拟机配置为4 vCPU、6 GiB内存、60 GiB动态磁盘，使用裁剪过的VMware实验内核配置；完整发行版配置需要更多资源，编译耗时和占用因配置而异。具体软件版本及其官方入口另见[下载链接与安装位置](environment/下载链接与安装位置.md)。

## B. 从零搭建openEuler实验内核

**从这里开始，所有命令均在VMware里的openEuler终端执行。** 若系统启动后只有文字命令行，该界面本身就是终端。

本节按操作系统、依赖、固定源码、Rust、配置、构建、安装的顺序执行。先获取项目源码，后续步骤将使用仓库中的配置与脚本：

```bash
sudo dnf install git
mkdir -p "$HOME/os-lab"
cd "$HOME/os-lab"
git clone https://github.com/Tomlegend2026/rust-openeuler-module.git
cd rust-openeuler-module
pwd
```

项目路径为`/home/你的用户名/os-lab/rust-openeuler-module`。已有项目可直接进入目录，后续配置与脚本均从该目录引用。

实验配置与构建过程见[环境记录](environment/2026-10-06实际搭建记录.md)。以下给出完整搭建步骤；已有系统或已有构建目录时，可跳过对应阶段。

### 1 安装操作系统

具体软件下载入口、标准 DVD 镜像直链、SHA256 及 Windows/openEuler 操作位置见 [下载链接与安装位置](environment/下载链接与安装位置.md)。本仓库不提供已安装好的虚拟机。

从 [openEuler 官方下载入口](https://www.openeuler.org/zh/download/) 选择 x86_64 的 openEuler 24.03 LTS 系列安装镜像，核对镜像提供的校验值，按虚拟机软件向导安装。有现成 openEuler 先检查，避免重复安装。记录完整发行版、架构、镜像来源与校验值。

安装开发工具前保存快照。镜像与虚拟机磁盘放仓库外；日常用普通用户，只有软件包安装、内核安装和模块装卸需要 sudo。

```sh
cat /etc/os-release
uname -m
uname -r
```

本项目基于openEuler内核源码构建启用Rust的实验内核。新安装系统的原始内核可以先用于环境准备，随后切换到实验内核完成装卸验证。

### 2 安装构建依赖

以下包名作为该系列的候选清单，仓库变体可能不同。若 dnf 报某包不存在，保存错误，使用 `dnf search` / `dnf provides` 查实际包名，不忽略错误继续。

```sh
sudo dnf install git make gcc gcc-c++ clang llvm llvm-devel clang-devel lld   bc bison flex elfutils-libelf-devel openssl-devel ncurses-devel   perl python3 cpio rsync curl tar xz kmod dracut grubby
clang --version
ld.lld --version
llvm-config --version
```

实测LLVM、Clang与LLD版本为17.0.6。内核与外部模块使用同一套工具链；如软件源提供的版本不同，结合版本记录及`rustavailable`检查其兼容性。

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

固定提交号与`environment/baseline.env`保持一致。已有内核仓库可核对当前提交及origin后继续；使用其他镜像源时也应获取相同提交。内核源码保存在项目仓库之外。

### 4 配置 Rust 工具链

**执行位置：openEuler终端，普通用户，不加sudo。** 首次安装rustup时使用[官方Linux安装入口](https://rustup.rs/)提供的安装器，并选择固定工具链：

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

`RUSTUP_TOOLCHAIN=1.73.0`在内核和模块编译会话中保持一致。新终端需要重新加载`$HOME/.cargo/env`并设置该变量。所需Rust构建特性由内核构建系统处理。

如果找不到 libclang，定位实际库并设置 LIBCLANG_PATH（例如通过 llvm-config --libdir 查候选），以实际 `rustavailable` 输出为准。

### 5 配置实验内核

**路线一：使用仓库中已验证的VMware实验配置。**

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

该路线采用源码目录内构建，以当前系统配置为基础，保留磁盘、根文件系统和虚拟机驱动。

```sh
cd "$HOME/os-lab/kernel"
cp "/boot/config-$(uname -r)" .config
make LLVM=1 olddefconfig
scripts/config --enable MODULES --enable MODULE_UNLOAD   --disable MODVERSIONS --disable CFI_CLANG --disable GCC_PLUGINS   --disable RANDSTRUCT --enable RANDSTRUCT_NONE --disable DEBUG_INFO_BTF   --enable RUST --enable SAMPLES --enable SAMPLES_RUST --module SAMPLE_RUST_MINIMAL   --set-str LOCALVERSION '-team2-rust' --disable LOCALVERSION_AUTO
make LLVM=1 olddefconfig
make LLVM=1 menuconfig
```

在菜单中确认Rust support和模块支持。固定源码中的Rust依赖`!MODVERSIONS`等条件；若RUST未能启用，先检查该版本的Kconfig依赖和工具链。

```sh
grep -E '^(CONFIG_RUST|CONFIG_MODULES|CONFIG_MODULE_UNLOAD|CONFIG_LOCALVERSION)=' .config
```

前三项应为y。若/boot没有配置文件，可检查`/proc/config.gz`或发行版提供的配置文件。若构建提示附加证书文件缺失，按实际配置处理证书路径，模块签名与信任要求以当前环境为准。

### 6 完整编译、安装并启动

**执行位置：openEuler终端。** 先完成内核编译，成功后再进行安装：

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

实测版本是`6.6.0-team2-rust+`，末尾`+`也是版本的一部分。以你本次构建输出为准，后面模块必须与实际运行版本匹配。普通头文件包或仅运行modules_prepare不能替代完整Rust内核构建。

首次安装前在VMware保存快照，保留原内核作为回退。下面的安装命令使用当前用户的路径；已有配套实验内核时可直接进入C节。

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

### 7 回到项目目录

回到B节开始时已克隆的项目目录：

```bash
cd "$HOME/os-lab/rust-openeuler-module"
```

继续C节构建和装卸模块。项目路径应位于openEuler文件系统中，并避免使用空格。

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

脚本核对系统、架构、源码提交、关键配置、工具链及完整构建产物，并运行Rust可用性检查。检查通过后进行模块构建与运行验证。

### 2 编译模块

```sh
bash scripts/build-module.sh "$HOME/os-lab/kernel"
modinfo module/rust_team2.ko
```

底层使用 Kbuild：`make -C module KDIR=内核绝对路径 LLVM=1`。不使用 cargo build 构建内核模块。日志自动进入 evidence/logs/，记录源码和 .ko 校验值。

### 3 人工验证一次

先在openEuler终端执行`lsmod | grep '^rust_team2 '`，无输出表示尚未加载。共享环境中，每次只运行一组装卸测试。

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

最后一个 grep 没有输出且返回1是正常结果。输出示例：

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

重复加载应返回非零且仍为`still_loaded`；卸载不存在模块应返回非零且仍为`still_absent`。实测两个用例的退出码均为1，这是预期行为。测试脚本整体应显示PASS，并在新建的`evidence/logs/negative-.../result.txt`记录`EXIT_STATUS=0`。

用例的非零返回值属于测试结果，脚本整体的PASS与EXIT_STATUS=0表示验证通过。

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

版本变更时，同步更新baseline.env、source-verification.json、构建配置及相应测试记录，保持源码、环境与验证结果一致。

## D. 结果核验与实验记录

**执行位置：openEuler终端，项目根目录。** 自动测试会打印`Evidence:`路径，每次运行生成独立目录，便于区分不同时间和环境的结果。

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
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Rust统计逻辑包含6项测试，Python辅助工具包含13项测试。统计逻辑、模块入口和原理文档分别说明所有权、借用、Result和Drop。单独编译纯计算库时，未调用的函数可能产生dead_code警告，需与编译错误区分。

### 实验记录内容

| 材料 | 应包含什么 |
|---|---|
| 环境记录 | 日期、系统版本、运行内核、Rust与LLVM版本、源码提交 |
| 构建结果 | 本次构建日志、modinfo、模块SHA256 |
| 实际运行 | 本次10轮及负向测试新生成的证据目录 |
| 演示素材 | 模块加载、统计日志、卸载后消失的真实截图或连续录屏 |
| 排障记录 | 错误信息、定位过程和解决方法 |

示例日志只表示预期结果。`dmesg`会保留历史内容，旧日志不能单独证明本次成功；应结合命令退出码、模块列表和自动提取的新日志判断。

模块中的`unload_begin`先于Vec字段析构输出；有限轮次和关键字检查不能排除所有内存泄漏、并发或内核缺陷。本模块没有设备I/O、后台线程或外部输入，结论只覆盖已实现的统计和生命周期。

### 常见问题

| 现象 | 处理方向 |
|---|---|
| Windows不认识dnf/insmod | 换到VMware里的openEuler终端 |
| sudo输入密码没有星号 | 正常，直接输入并按Enter |
| GitHub提示仓库不存在 | 确认账号具有该私有仓库的访问权限 |
| 包不存在或下载失败 | 先检查虚拟机联网和对应发行版软件源，保存完整错误 |
| 刚重启后找不到rustc | 重新source ~/.cargo/env并设置RUSTUP_TOOLCHAIN |
| lsmod查不到模块 | 加载前、卸载后正常；加载后查不到则需排障 |
| 循环测试提示模块已加载 | 确认是否为自己手工测试留下的实例，正常卸载后再跑 |
| 新内核无法启动 | 在VMware启动菜单选原内核，或回到安装前快照检查驱动和initramfs |

## E. 项目文档与演示材料

| 内容 | 入口 |
|---|---|
| Rust源码与原理 | [内核入口](module/rust_team2.rs)、[统计逻辑](module/statistics.rs)、[原理讲解](docs/05-模块原理.md) |
| 本组实际环境 | [版本记录](environment/版本记录.md)、[搭建记录](environment/2026-10-06实际搭建记录.md) |
| 历史实测结果 | [2026-10-18结果](tests/测试结果-20261018.md) |
| 正式报告与正文 | [Word报告](deliverables/任务2%20Rust内核模块实验报告.docx)、[报告正文](report/实验报告.md) |
| 22页源码走读详细版 | [PowerPoint](deliverables/源码走读详细版/任务2%20Rust内核模块-源码走读详细版.pptx)、[离线HTML](deliverables/源码走读详细版/Rust内核模块-源码走读.html) |
| 现场汇报 | [讲稿和演示顺序](presentation/汇报与演示.md) |
| 协作和来源 | [GitHub协作](CONTRIBUTING.md)、[来源与许可](THIRD_PARTY_NOTICES.md) |

在项目根目录执行`python3 scripts/package-submission.py`，可生成`build/rust-openeuler-module-submission.zip`，包含源码、文档和保存的证据，不包含虚拟机及编译产物。
