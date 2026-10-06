#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $# == 1 ]] || { echo "Usage: bash scripts/build-module.sh /absolute/kernel/source-and-build" >&2; exit 1; }
kdir=$(cd -- "$1" && pwd)
mkdir -p "$repo/evidence/logs"
log="$repo/evidence/logs/build-$(date -u +%Y%m%dT%H%M%SZ)-$$.log"
{
    date -u
    bash "$repo/scripts/check-env.sh" "$kdir"
    sha256sum "$repo/module/rust_team2.rs" "$repo/module/statistics.rs"
    make -C "$repo/module" KDIR="$kdir" LLVM=1
    test -s "$repo/module/rust_team2.ko"
    modinfo "$repo/module/rust_team2.ko"
    sha256sum "$repo/module/rust_team2.ko"
    echo "PASS: build completed. Loading is a separate step."
} 2>&1 | tee "$log"
echo "Saved: $log"
