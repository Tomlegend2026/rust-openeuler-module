#!/usr/bin/env bash
# Install only the verified experiment build; retain the stock kernel.
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run with sudo inside the experiment VM.' >&2; exit 1; }
source /etc/os-release
[[ ${ID,,} == openeuler ]] || exit 1
[[ $# == 1 ]] || { echo 'Usage: sudo bash scripts/install-kernel-vm.sh /home/team2/os-lab/kernel'; exit 1; }
kdir=$(realpath "$1")
[[ $kdir == /home/team2/os-lab/kernel ]] || { echo 'Unexpected kernel path.' >&2; exit 1; }
[[ $(cat /home/team2/os-lab/kernel-build.exit) == 0 ]] || exit 1
[[ $(git -c safe.directory="$kdir" -C "$kdir" rev-parse HEAD) == 6e0c18da64fd9919a51f8f2216a371503a5e2763 ]] || exit 1
git -c safe.directory="$kdir" -C "$kdir" diff --quiet HEAD --
release=$(cat "$kdir/include/config/kernel.release")
[[ $release == 6.6.0-team2-rust+ ]] || { echo "Unexpected release: $release" >&2; exit 1; }
grep -qx CONFIG_RUST=y "$kdir/.config"
for file in arch/x86/boot/bzImage System.map Module.symvers rust/kernel.o; do
    test -s "$kdir/$file"
done
[[ ! -e /boot/vmlinuz-$release && ! -e /lib/modules/$release ]] || { echo 'Kernel already installed; inspect before repeating.' >&2; exit 1; }
export PATH="/home/team2/.cargo/bin:$PATH"
export RUSTUP_HOME=/home/team2/.rustup CARGO_HOME=/home/team2/.cargo RUSTUP_TOOLCHAIN=1.73.0
stock=$(uname -r)
test -s "/boot/vmlinuz-$stock"
make -C "$kdir" LLVM=1 modules_install
install -m 644 "$kdir/arch/x86/boot/bzImage" "/boot/vmlinuz-$release"
install -m 644 "$kdir/System.map" "/boot/System.map-$release"
install -m 644 "$kdir/.config" "/boot/config-$release"
depmod "$release"
dracut --kver "$release" "/boot/initramfs-$release.img"
test -s "/boot/initramfs-$release.img"
grubby --add-kernel="/boot/vmlinuz-$release" --initrd="/boot/initramfs-$release.img" --title="openEuler Rust experiment ($release)" --copy-default
grubby --info="/boot/vmlinuz-$release"
test -s "/boot/vmlinuz-$stock"
grubby --set-default="/boot/vmlinuz-$release"
[[ $(grubby --default-kernel) == "/boot/vmlinuz-$release" ]]
echo "INSTALL_COMPLETE=$release"
echo 'Stock kernel retained. Next boot defaults to the Rust experiment entry.'
