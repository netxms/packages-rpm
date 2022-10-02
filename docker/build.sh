#!/bin/bash

set -e

mock --enable-network -r rocky+epel-8-$(arch) --spec SPECS/*.spec --sources SOURCES --addrepo https://packages.netxms.org/devel/epel/8/$(arch)/stable --addrepo https://packages.netxms.org/epel/8/$(arch)/stable
mock --enable-network -r rocky+epel-9-$(arch) --spec SPECS/*.spec --sources SOURCES --addrepo https://packages.netxms.org/devel/epel/9/$(arch)/stable --addrepo https://packages.netxms.org/epel/9/$(arch)/stable
cp /var/lib/mock/*/result/*.rpm /result/
