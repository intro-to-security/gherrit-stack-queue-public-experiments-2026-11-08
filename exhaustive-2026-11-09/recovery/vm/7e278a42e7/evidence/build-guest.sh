#!/bin/sh
set -eu
cd /lab
apt-get -y --no-install-recommends install python3 > python-runtime-install.log 2>&1
apt-get clean
python3 -c 'import json, pathlib, hashlib, select, shutil, subprocess'
unsquashfs -processors 1 -d extracted boot/modloop-virt \
  modules/6.12.115-0-virt/kernel/fs/ext4/ext4.ko \
  modules/6.12.115-0-virt/kernel/fs/jbd2/jbd2.ko \
  modules/6.12.115-0-virt/kernel/fs/mbcache.ko \
  modules/6.12.115-0-virt/kernel/lib/crc16.ko \
  modules/6.12.115-0-virt/modules.dep > module-extract.log
cp -a extracted/modules/6.12.115-0-virt/. initramfs/lib/modules/6.12.115-0-virt/
cp /bin/busybox initramfs/bin/busybox
cp initramfs/init original-init
cp init initramfs/init
chmod 755 initramfs/init
gcc -static -O2 -Wall -Wextra -Werror probe.c -o initramfs/probe
cd initramfs
find . -print0 | cpio --null -o -H newc 2> /lab/cpio.log | gzip -1 > /lab/test-initramfs.gz
cd /lab
dpkg-query -W > installed-versions-final.txt
sha256sum boot/vmlinuz-virt boot/config-6.12.115-0-virt boot/modloop-virt \
  boot/initramfs-virt test-initramfs.gz initramfs/probe probe.c init controller.py > guest-inputs.sha256
du -sh /lab
