#!/usr/bin/env bash
# Expected failure cases in the dedicated VM. Never force-remove a module.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
die() { echo "FAIL: $*" >&2; exit 1; }
[[ $EUID == 0 ]] || die "Run with sudo in the experimental VM."
source /etc/os-release
[[ ${ID,,} == openeuler ]] || die "Refusing to run outside openEuler."
module=${1:-"$repo/module/rust_team2.ko"}
[[ $# -le 1 && -s $module ]] || die "Usage: sudo bash scripts/test-negative.sh [module.ko]"
for tool in insmod rmmod modinfo dmesg flock python3 sha256sum; do
    command -v "$tool" >/dev/null || die "Missing tool: $tool"
done
[[ $(modinfo -F name "$module") == rust_team2 ]] || die "Unexpected module name."
vermagic=$(modinfo -F vermagic "$module")
[[ ${vermagic%% *} == "$(uname -r)" ]] || die "Kernel/module release mismatch."
exec 9>/run/lock/rust_team2-test.lock
flock -n 9 || die "Another project module test is running."
loaded() { grep -q '^rust_team2 ' /proc/modules; }
if loaded; then die "Module already loaded; refusing to remove another run's module."; fi
mkdir -p "$repo/evidence/logs"
run=$(mktemp -d "$repo/evidence/logs/negative-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
echo "Evidence: $run"
exec > >(tee "$run/commands.log") 2>&1
owned=0
finish() {
    status=$?
    trap - EXIT
    if (( owned )); then
        rmmod rust_team2 || status=1
    fi
    dmesg --raw > "$run/final.log" || status=1
    echo "EXIT_STATUS=$status" > "$run/result.txt"
    if [[ ${SUDO_UID:-0} =~ ^[0-9]+$ && ${SUDO_GID:-0} =~ ^[0-9]+$ ]] && (( ${SUDO_UID:-0} != 0 )); then
        chown -R -- "$SUDO_UID:$SUDO_GID" "$run" || status=1
    fi
    exit "$status"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
date -u
uname -a
modinfo "$module"
sha256sum "$module"
dmesg --raw > "$run/before.log"
printf 'case\texit_status\tstate_check\n' > "$run/cases.tsv"
insmod "$module"
owned=1
loaded || die "Module absent after first load."
duplicate=0
insmod "$module" > "$run/duplicate-load.log" 2>&1 || duplicate=$?
[[ $duplicate != 0 ]] || die "Duplicate load unexpectedly succeeded."
loaded || die "Duplicate load changed the existing module state."
printf 'duplicate_load\t%s\tstill_loaded\n' "$duplicate" >> "$run/cases.tsv"
rmmod rust_team2
owned=0
if loaded; then die "Module still loaded after unload."; fi
absent=0
rmmod rust_team2 > "$run/absent-unload.log" 2>&1 || absent=$?
[[ $absent != 0 ]] || die "Unloading an absent module unexpectedly succeeded."
if loaded; then die "Unexpected module state after absent unload."; fi
printf 'absent_unload\t%s\tstill_absent\n' "$absent" >> "$run/cases.tsv"
dmesg --raw > "$run/after.log"
python3 "$repo/scripts/extract-new-log.py" "$run/before.log" "$run/after.log" "$run/new.log"
[[ $(grep -Fc '[rust_team2] event=loaded count=6 sum=23 min=1 max=9' "$run/new.log" || true) == 1 ]] || die "Expected exactly one initialization."
[[ $(grep -Fc '[rust_team2] event=unload_begin retained=6 sum=23' "$run/new.log" || true) == 1 ]] || die "Expected exactly one cleanup entry."
if grep -Ei 'BUG:|Oops:|WARNING:|kernel panic' "$run/new.log"; then
    die "New kernel warning/error needs manual review."
fi
cat "$run/cases.tsv"
echo 'PASS: duplicate load and absent unload rejected; module state preserved.'
