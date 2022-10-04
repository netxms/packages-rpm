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

mock --enable-network -r rocky+epel-8-$(arch) --spec SPECS/*.spec --sources SOURCES --addrepo https://packages.netxms.org/devel/epel/8/$(arch)/stable --addrepo https://packages.netxms.org/epel/8/$(arch)/stable
mock --enable-network -r rocky+epel-9-$(arch) --spec SPECS/*.spec --sources SOURCES --addrepo https://packages.netxms.org/devel/epel/9/$(arch)/stable --addrepo https://packages.netxms.org/epel/9/$(arch)/stable

cp /var/lib/mock/*/result/*.rpm /result/
