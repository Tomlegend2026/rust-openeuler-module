#!/usr/bin/env bash
# Continue with the module only after a successful full kernel build.
set -euo pipefail
source "$HOME/.cargo/env"
export RUSTUP_TOOLCHAIN=1.73.0
while [[ ! -f "$HOME/os-lab/kernel-build.exit" ]]; do
    if ! pgrep -u "$(id -u)" -f '^bash /home/team2/os-lab/build-kernel.sh$' >/dev/null; then
        echo 'Kernel builder stopped without an exit status.' >&2
        exit 1
    fi
    sleep 10
done
[[ $(cat "$HOME/os-lab/kernel-build.exit") == 0 ]] || {
    echo 'Kernel build failed. Inspect kernel-build.log.' >&2
    exit 1
}
cd "$HOME/os-lab/rust-openeuler-module"
bash scripts/build-module.sh "$HOME/os-lab/kernel"
echo MODULE_BUILD_COMPLETE
