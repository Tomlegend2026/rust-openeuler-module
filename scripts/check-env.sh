#!/usr/bin/env bash
# Validate the pinned native openEuler build environment. Never installs anything.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source "$repo/environment/baseline.env"
die() { echo "FAIL: $*" >&2; exit 1; }
[[ $# == 1 ]] || die "Usage: bash scripts/check-env.sh /absolute/kernel/source-and-build"
[[ $(uname -s) == Linux ]] || die "Run inside an openEuler Linux VM."
[[ -r /etc/os-release ]] || die "Cannot read /etc/os-release."
source /etc/os-release
[[ ${ID,,} == openeuler ]] || die "This is ${ID:-unknown}, not openEuler. Host tests are separate."
[[ $(uname -m) == x86_64 ]] || die "This draft targets native x86_64; other architectures need review."
kdir=$(cd -- "$1" && pwd)
[[ $kdir != *[[:space:]]* && $repo != *[[:space:]]* ]] || die "Use paths without whitespace for Kbuild."
for tool in git make rustc clang ld.lld llvm-ar bindgen python3 modinfo; do
    command -v "$tool" >/dev/null || die "Missing tool: $tool"
done
actual_commit=$(git -C "$kdir" rev-parse HEAD)
[[ $actual_commit == "$KERNEL_COMMIT" ]] || die "Kernel source commit differs: $actual_commit"
git -C "$kdir" diff --quiet HEAD -- || die "Tracked kernel source has local modifications."
[[ -f "$kdir/.config" ]] || die "Missing kernel .config."
for flag in CONFIG_RUST CONFIG_MODULES CONFIG_MODULE_UNLOAD; do
    grep -qx "$flag=y" "$kdir/.config" || die "$flag must be y."
done
for flag in CONFIG_MODVERSIONS CONFIG_CFI_CLANG CONFIG_GCC_PLUGINS CONFIG_RANDSTRUCT; do
    if grep -qx "$flag=y" "$kdir/.config"; then die "$flag conflicts with this Rust baseline."; fi
done
[[ $(rustc --version | awk '{print $2}') == "$BASELINE_RUST" ]] || die "Use Rust $BASELINE_RUST (including rust-src)."
[[ $(bindgen --version | awk '{print $2}') == "$BASELINE_BINDGEN" ]] || die "Use bindgen $BASELINE_BINDGEN."
for file in include/generated/autoconf.h include/config/kernel.release Module.symvers rust/kernel.o rust/libmacros.so; do
    [[ -s "$kdir/$file" ]] || die "Missing prepared build artifact: $file; build the full kernel first."
done
echo "Kernel source: $actual_commit"
echo "Build release: $(cat "$kdir/include/config/kernel.release")"
echo "Running release: $(uname -r)"
echo "Checking Rust requirements..."
make -C "$kdir" LLVM=1 rustavailable
echo "PASS: source/build prerequisites. This does not prove runtime loadability."
