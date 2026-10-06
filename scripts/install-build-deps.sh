#!/usr/bin/env bash
# Install build tools inside the openEuler guest; run with sudo.
set -euo pipefail
if [[ $(id -u) -ne 0 ]]; then
    echo 'Run with sudo: sudo bash install-build-deps.sh' >&2
    exit 1
fi
source /etc/os-release
if [[ ${ID,,} != openeuler ]]; then
    echo 'This script is intended for the openEuler experiment VM.' >&2
    exit 1
fi
dnf install -y git make gcc gcc-c++ clang llvm llvm-devel clang-devel lld \
    bc bison flex elfutils-libelf-devel openssl-devel ncurses-devel \
    perl python3 cpio rsync curl tar xz kmod dracut grubby
echo 'BUILD_DEPENDENCIES_INSTALLED'
clang --version
llvm-config --version
ld.lld --version
