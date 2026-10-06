#!/usr/bin/env bash
# Run as the normal experiment user; logs survive an SSH disconnect.
set -uo pipefail
source "$HOME/.cargo/env"
export RUSTUP_TOOLCHAIN=1.73.0
cd "$HOME/os-lab/kernel" || exit 1
make LLVM=1 -j3 > "$HOME/os-lab/kernel-build.log" 2>&1
result=$?
echo "$result" > "$HOME/os-lab/kernel-build.exit"
exit "$result"
