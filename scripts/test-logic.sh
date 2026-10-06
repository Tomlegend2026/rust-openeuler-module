#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
command -v rustc >/dev/null || { echo "rustc is required" >&2; exit 1; }
mkdir -p "$repo/build" "$repo/evidence/logs"
log="$repo/evidence/logs/host-logic-$(date -u +%Y%m%dT%H%M%SZ)-$$.log"
{
    echo "HOST LOGIC ONLY: this does not build or load the kernel module."
    date -u
    rustc --version
    sha256sum "$repo/module/statistics.rs"
    rustc --edition=2021 --test "$repo/module/statistics.rs" -o "$repo/build/statistics-tests"
    "$repo/build/statistics-tests" --nocapture
    rustc --edition=2021 --crate-type lib --crate-name statistics \
        "$repo/module/statistics.rs" -o "$repo/build/libstatistics.rlib"
} 2>&1 | tee "$log"
echo "Saved: $log"
