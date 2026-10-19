#!/usr/bin/env bash
# Run only in the dedicated openEuler VM. No force unload or log clearing.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
die() { echo "FAIL: $*" >&2; exit 1; }
[[ $# -le 2 ]] || die "Usage: sudo bash scripts/test-lifecycle.sh [module.ko] [rounds=10]"
[[ $EUID == 0 ]] || die "Run with sudo inside the experimental VM."
[[ $(uname -s) == Linux && -r /etc/os-release ]] || die "Linux is required."
source /etc/os-release
[[ ${ID,,} == openeuler ]] || die "Refusing to load a module outside openEuler."
for tool in insmod rmmod modinfo dmesg python3 flock sha256sum; do
    command -v "$tool" >/dev/null || die "Missing tool: $tool"
done
module=${1:-"$repo/module/rust_team2.ko"}
rounds=${2:-10}
[[ $rounds =~ ^[1-9][0-9]{0,2}$ ]] || die "Rounds must be an integer between 1 and 999."
[[ -s $module ]] || die "Module file is missing: $module"
[[ $(modinfo -F name "$module") == rust_team2 ]] || die "Unexpected module name."
vermagic=$(modinfo -F vermagic "$module")
[[ ${vermagic%% *} == "$(uname -r)" ]] || die "Module and running kernel releases differ."
exec 9>/run/lock/rust_team2-test.lock
flock -n 9 || die "Another project lifecycle test is running."
loaded() { grep -q '^rust_team2 ' /proc/modules; }
if loaded; then die "rust_team2 is already loaded. This script will not remove it."; fi
mkdir -p "$repo/evidence/logs"
run=$(mktemp -d "$repo/evidence/logs/lifecycle-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
echo "Evidence: $run"
exec > >(tee "$run/commands.log") 2>&1
owned=0
finish() {
    status=$?
    trap - EXIT
    if (( owned )); then
        echo "Cleaning up the module loaded by this run..."
        if rmmod rust_team2; then
            owned=0
        else
            echo "Cleanup failed. Keep the VM for inspection; do not force unload."
            status=1
        fi
    fi
    dmesg --raw > "$run/final.log" || status=1
    # mktemp creates a root-only directory under sudo. Return this run's
    # evidence to the invoking user so it can be reviewed and shared.
    if [[ ${SUDO_UID:-0} =~ ^[0-9]+$ && ${SUDO_GID:-0} =~ ^[0-9]+$ ]] && (( ${SUDO_UID:-0} != 0 )); then
        chown -R -- "$SUDO_UID:$SUDO_GID" "$run" || status=1
    fi
    echo "EXIT_STATUS=$status" | tee "$run/result.txt"
    if [[ ${SUDO_UID:-0} =~ ^[0-9]+$ && ${SUDO_GID:-0} =~ ^[0-9]+$ ]] && (( ${SUDO_UID:-0} != 0 )); then
        chown -- "$SUDO_UID:$SUDO_GID" "$run/result.txt" || status=1
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
git -C "$repo" rev-parse HEAD 2>/dev/null || echo "Project not committed yet."
dmesg --raw > "$run/before.log"
printf 'round\tload\tlisted_after_load\tunload\tabsent_after_unload\n' > "$run/rounds.tsv"
for (( i=1; i<=rounds; i++ )); do
    echo "Round $i/$rounds: loading"
    insmod "$module"
    owned=1
    loaded || die "Module absent after successful insmod."
    echo "Round $i/$rounds: unloading"
    rmmod rust_team2
    owned=0
    if loaded; then die "Module remains listed after unload."; fi
    printf '%s\t0\tyes\t0\tyes\n' "$i" >> "$run/rounds.tsv"
done
dmesg --raw > "$run/after.log"
python3 "$repo/scripts/extract-new-log.py" "$run/before.log" "$run/after.log" "$run/new.log"
loads=$(grep -Fc '[rust_team2] event=loaded count=6 sum=23 min=1 max=9' "$run/new.log" || true)
unloads=$(grep -Fc '[rust_team2] event=unload_begin retained=6 sum=23' "$run/new.log" || true)
details=$(grep -Fc '[rust_team2] event=stats_detail average=3 range=8' "$run/new.log" || true)
[[ $loads == "$rounds" && $unloads == "$rounds" && $details == "$rounds" ]] ||
    die "Unexpected lifecycle log counts: loaded=$loads details=$details unload=$unloads"
if grep -Ei 'BUG:|Oops:|WARNING:|kernel panic' "$run/new.log"; then
    die "New kernel warning/error needs manual review (possibly unrelated)."
fi
echo "PASS: $rounds lifecycle rounds and expected log counts; no matched warnings."
echo "This is not proof of absence of all memory leaks. Review new.log as well."
