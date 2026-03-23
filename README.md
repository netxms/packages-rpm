# RPM spec for NetXMS packages

This repository contains scripts for creating rpm packages (netxms-server/netxms-agent).

Packages are built by NetXMS team and published on https://packages.netxms.org/.

## Build

RPMs are built using `rpmbuild` inside native distro containers.

```sh
# Build RPMs for OracleLinux 9
docker run --rm -v $(pwd):/build -w /build -v /tmp/result:/result oraclelinux:9 \
  scripts/build-rpm.sh epel 9

# Build RPMs for Fedora 43
docker run --rm -v $(pwd):/build -w /build -v /tmp/result:/result fedora:43 \
  scripts/build-rpm.sh fedora 43

# Cache Maven repository between builds
docker run --rm -v $(pwd):/build -w /build -v /tmp/result:/result \
  -v $(pwd)/m2-cache:/m2-repo oraclelinux:9 \
  scripts/build-rpm.sh epel 9
```

Supported targets: `epel 8`, `epel 9`, `epel 10`, `fedora 42`, `fedora 43`.
