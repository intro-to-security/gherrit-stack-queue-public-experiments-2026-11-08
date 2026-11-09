#!/bin/bash
set -euo pipefail
cd /lab/extension
test ! -e initramfs-copy
test ! -e test-initramfs.gz
cp -a /lab/initramfs initramfs-copy
gcc -static -O2 -Wall -Wextra -Werror probe.c -o initramfs-copy/probe
cp init initramfs-copy/init
chmod 755 initramfs-copy/init
cd initramfs-copy
find . -print0 | cpio --null -o -H newc 2> /lab/extension/cpio.log | gzip -1 > /lab/extension/test-initramfs.gz
cd /lab/extension
sha256sum probe.c expected.h oracle.py controller.py init build-extension.sh \
  initramfs-copy/probe test-initramfs.gz /lab/boot/Image-virt > build-inputs.sha256
gcc --version > compiler-version.txt
du -sh /lab/extension > build-size.txt
