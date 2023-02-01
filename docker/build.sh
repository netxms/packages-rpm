#!/bin/bash

set -e

cat > /etc/mock/site-defaults.cfg <<__END
config_opts['plugin_conf']['tmpfs_enable'] = True
config_opts['plugin_conf']['tmpfs_opts'] = {}
config_opts['plugin_conf']['tmpfs_opts']['required_ram_mb'] = 1024
config_opts['plugin_conf']['tmpfs_opts']['max_fs_size'] = '5g'
config_opts['plugin_conf']['tmpfs_opts']['mode'] = '0755'
config_opts['plugin_conf']['tmpfs_opts']['keep_mounted'] = False

config_opts['plugin_conf']['bind_mount_enable'] = True
config_opts['plugin_conf']['bind_mount_opts']['dirs'].append(('/var/cache/mock/m2-repo', '/m2-repo' ))
__END

mkdir -p /var/cache/mock/m2-repo

for V in 8 9; do
   mock --enable-network -r rocky+epel-$V-$(arch) --spec SPECS/*.spec --sources SOURCES \
      --addrepo https://packages.netxms.org/devel/epel/$V/$(arch)/stable \
      --addrepo https://packages.netxms.org/epel/$V/$(arch)/stable
done

for V in 36 37; do
   mock --enable-network -r fedora-$V-$(arch) --spec SPECS/*.spec --sources SOURCES \
      --addrepo https://packages.netxms.org/devel/fedora/$V/$(arch)/stable \
      --addrepo https://packages.netxms.org/fedora/$V/$(arch)/stable
done

cp /var/lib/mock/*/result/*.rpm /dist/
