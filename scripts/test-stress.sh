#!/usr/bin/env bash
# Run a larger lifecycle sample after the normal 10-round acceptance test.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $EUID == 0 ]] || { echo "Run with sudo in the experimental VM." >&2; exit 1; }
source /etc/os-release
[[ ${ID,,} == openeuler ]] || { echo "Refusing to run outside openEuler." >&2; exit 1; }
module=${1:-"$repo/module/rust_team2.ko"}
rounds=${2:-100}
[[ $rounds =~ ^[1-9][0-9]{0,2}$ ]] || { echo "Rounds must be an integer between 1 and 999." >&2; exit 1; }
echo "Stress lifecycle: $rounds rounds"
bash "$repo/scripts/test-lifecycle.sh" "$module" "$rounds"
bash "$repo/scripts/test-negative.sh" "$module"
