#!/usr/bin/env bash
# Interactive reproduction in the existing openEuler VM; never uploads results.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
self="$repo/scripts/reproduce-session.sh"
module="$repo/module/rust_team2.ko"
die() { echo "FAIL: $*" >&2; exit 1; }
pause() { printf '\n%s [按 Enter 继续] ' "$1"; read -r </dev/tty; }
loaded() { grep -q '^rust_team2 ' /proc/modules; }

# Privileged single-cycle helper, invoked only by the normal-user coordinator.
if [[ ${1:-} == --demo ]]; then
    [[ $EUID == 0 && $# == 2 ]] || die 'Internal demo requires sudo and one evidence directory.'
    source /etc/os-release
    [[ ${ID,,} == openeuler ]] || die 'This demo requires openEuler.'
    run=$(realpath -- "$2")
    [[ -d $run && $run == "$repo/evidence/logs/reproduction-"* ]] || die 'Unexpected evidence path.'
    [[ $(modinfo -F name "$module") == rust_team2 ]] || die 'Unexpected module.'
    vm=$(modinfo -F vermagic "$module")
    [[ ${vm%% *} == "$(uname -r)" ]] || die 'Kernel/module release mismatch.'
    exec 9>/run/lock/rust_team2-test.lock
    flock -n 9 || die 'Another module test is running.'
    if loaded; then die 'Module already loaded; inspect it before continuing.'; fi
    owned=0
    finish_demo() {
        status=$?
        trap - EXIT
        if (( owned )); then
            echo 'Cleaning up the module loaded by this demo...'
            rmmod rust_team2 || status=1
        fi
        dmesg --raw > "$run/manual-final.log" || status=1
        printf 'EXIT_STATUS=%s\n' "$status" > "$run/manual-result.txt"
        if [[ ${SUDO_UID:-0} =~ ^[0-9]+$ && ${SUDO_GID:-0} =~ ^[0-9]+$ ]]; then
            chown -- "$SUDO_UID:$SUDO_GID" "$run"/manual-* || status=1
        fi
        exit "$status"
    }
    trap finish_demo EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    dmesg --raw > "$run/manual-before.log"
    pause '接下来加载模块，并检查模块列表和统计日志。'
    printf '+ sudo insmod module/rust_team2.ko\n'
    insmod "$module"
    owned=1
    printf '+ lsmod | grep rust_team2\n'
    lsmod | grep '^rust_team2 '
    dmesg --raw > "$run/manual-loaded.log"
    python3 "$repo/scripts/extract-new-log.py" "$run/manual-before.log" "$run/manual-loaded.log" "$run/manual-load-new.log"
    grep -F '[rust_team2] event=loaded count=6 sum=23 min=1 max=9' "$run/manual-load-new.log"
    grep -F '[rust_team2] event=stats_detail average=3 range=8' "$run/manual-load-new.log"
    pause '模块现已加载，可在此截图。接下来卸载模块。'
    printf '+ sudo rmmod rust_team2\n'
    rmmod rust_team2
    owned=0
    if loaded; then die 'Module is still present after unload.'; fi
    printf '模块列表查询无匹配：模块已卸载。\n'
    dmesg --raw > "$run/manual-after.log"
    python3 "$repo/scripts/extract-new-log.py" "$run/manual-before.log" "$run/manual-after.log" "$run/manual-new.log"
    [[ $(grep -Fc '[rust_team2] event=loaded count=6 sum=23 min=1 max=9' "$run/manual-new.log") == 1 ]] || die 'Unexpected load count.'
    [[ $(grep -Fc '[rust_team2] event=stats_detail average=3 range=8' "$run/manual-new.log") == 1 ]] || die 'Unexpected detail count.'
    [[ $(grep -Fc '[rust_team2] event=unload_begin retained=6 sum=23' "$run/manual-new.log") == 1 ]] || die 'Unexpected unload count.'
    grep -F '[rust_team2] event=stats_detail average=3 range=8' "$run/manual-new.log"
    grep -F '[rust_team2] event=unload_begin retained=6 sum=23' "$run/manual-new.log"
    if grep -Ei 'BUG:|Oops:|WARNING:|kernel panic' "$run/manual-new.log"; then die 'Review new kernel warnings.'; fi
    echo 'PASS: single load/unload demonstration.'
    exit 0
fi

[[ $# == 0 ]] || die 'Usage: bash scripts/reproduce-session.sh'
[[ $EUID != 0 ]] || die 'Run as the ordinary SSH user, without sudo before bash.'
[[ -t 0 ]] || die 'Run interactively in your SSH terminal.'
source /etc/os-release
[[ ${ID,,} == openeuler && $(uname -m) == x86_64 ]] || die 'Requires the x86_64 openEuler VM.'
for tool in python3 sudo flock tee make sha256sum; do command -v "$tool" >/dev/null || die "Missing tool: $tool"; done
mkdir -p "$repo/build" "$repo/evidence/logs"
exec 8>"$repo/build/reproduction-session.lock"
flock -n 8 || die 'Another reproduction session is running.'
run=$(mktemp -d "$repo/evidence/logs/reproduction-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
exec > >(tee "$run/session.log") 2>&1
finish() {
    status=$?
    trap - EXIT
    printf 'EXIT_STATUS=%s\n' "$status" > "$run/result.txt"
    date -u +%FT%TZ > "$run/finished-at.txt"
    echo
    if (( status == 0 )); then
        echo 'REPRODUCTION_PASS'
    else
        echo 'REPRODUCTION_FAILED: outputs are preserved for diagnosis.'
    fi
    echo "Evidence: $run"
    echo "EXIT_STATUS=$status"
    exit "$status"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
cd "$repo"
printf 'step\tstatus\n' > "$run/steps.tsv"
step() { printf '\n========== %s ==========\n' "$1"; }
passed() { printf '%s\tPASS\n' "$1" >> "$run/steps.tsv"; }

step '1/8 检查系统与工具链'
source "$HOME/.cargo/env"
export RUSTUP_TOOLCHAIN=1.73.0
{
    date -u +%FT%TZ
    id -un
    uname -a
    cat /etc/os-release
    rustc --version
    clang --version
    bindgen --version
    git -C "$HOME/os-lab/kernel" rev-parse HEAD
} | tee "$run/environment.log"
sha256sum module/rust_team2.rs module/statistics.rs scripts/reproduce-session.sh scripts/build-module.sh scripts/test-lifecycle.sh scripts/test-negative.sh scripts/test-stress.sh scripts/summarize-log.py > "$run/sources.sha256"
bash scripts/check-env.sh "$HOME/os-lab/kernel" | tee "$run/environment-check.log"
[[ $(cat "$HOME/os-lab/kernel/include/config/kernel.release") == "$(uname -r)" ]] || die 'Running kernel differs from the build directory.'
if loaded; then die 'Module already loaded. Inspect and unload your instance before repeating.'; fi
passed environment

step '2/8 重新构建模块'
pause '将清理本项目的模块构建产物并重新编译，不重建整个内核。'
make -C module KDIR="$HOME/os-lab/kernel" LLVM=1 clean
bash scripts/build-module.sh "$HOME/os-lab/kernel" | tee "$run/build.log"
modinfo "$module" | tee "$run/modinfo.log"
sha256sum "$module" > "$run/module.sha256"
passed build

step '3/8 Rust逻辑与Python工具测试'
bash scripts/test-logic.sh | tee "$run/rust-tests.log"
python3 -m unittest discover -s tests -p 'test_*.py' -v 2>&1 | tee "$run/python-tests.log"
passed host-tests

step '4/8 单次加载、查看结果、卸载'
echo 'sudo要求密码时，在当前终端输入你的openEuler密码；输入不显示字符。'
sudo bash "$self" --demo "$run"
passed manual-demo

step '5/8 十轮动态装卸'
pause '接下来执行十轮装卸并记录每轮状态。'
sudo bash scripts/test-lifecycle.sh "$module" 10 | tee "$run/lifecycle-console.log"
life=$(sed -n 's/^Evidence: //p' "$run/lifecycle-console.log")
[[ -n $life && -d $life && $life == "$repo/evidence/logs/lifecycle-"* ]] || die 'Lifecycle evidence path missing.'
printf '%s\n' "$life" > "$run/lifecycle-path.txt"
passed lifecycle

step '6/8 负向用例'
sudo bash scripts/test-negative.sh "$module" | tee "$run/negative-console.log"
negative=$(sed -n 's/^Evidence: //p' "$run/negative-console.log")
[[ -n $negative && -d $negative && $negative == "$repo/evidence/logs/negative-"* ]] || die 'Negative evidence path missing.'
printf '%s\n' "$negative" > "$run/negative-path.txt"
passed negative

step '7/8 离线核验本次证据'
python3 scripts/verify-evidence.py "$life" --rounds 10 | tee "$run/lifecycle-audit.json"
[[ $(cat "$negative/result.txt") == EXIT_STATUS=0 ]] || die 'Negative test result is not successful.'
[[ $(cat "$run/manual-result.txt") == EXIT_STATUS=0 ]] || die 'Single-cycle result is not successful.'
if loaded; then die 'Module remains loaded after tests.'; fi
echo 'Final module state: absent' | tee "$run/final-state.txt"
passed audit

step '8/8 展示本次结果'
passed completed
cat "$run/steps.tsv"
cat "$negative/cases.tsv"
echo '所有原始输出已保存。本脚本不会上传GitHub。'
echo '本次证据可在核验后发布，目录见末尾Evidence路径。'
