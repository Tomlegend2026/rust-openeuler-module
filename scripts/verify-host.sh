#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo"
for script in scripts/*.sh; do
    bash -n "$script"
    echo "Syntax OK: $script"
done
python3 -m unittest discover -s tests -p 'test_*.py' -v
cargo run --offline --manifest-path learning/rust-basics/Cargo.toml
# This check must reject Ubuntu before attempting any kernel build.
set +e
output=$(bash scripts/check-env.sh /nonexistent 2>&1)
status=$?
set -e
printf '%s\n' "$output"
if [[ $status == 0 || $output != *"not openEuler"* ]]; then
    echo 'Unexpected environment-check success' >&2
    exit 1
fi
echo 'Host validation completed; no module loaded.'
