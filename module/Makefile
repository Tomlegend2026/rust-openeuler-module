# SPDX-License-Identifier: GPL-2.0-only
KDIR ?= /lib/modules/$(shell uname -r)/build
LLVM ?= 1

.PHONY: all clean
all:
	$(MAKE) -C "$(KDIR)" M="$(CURDIR)" LLVM=$(LLVM) modules

clean:
	$(MAKE) -C "$(KDIR)" M="$(CURDIR)" LLVM=$(LLVM) clean
