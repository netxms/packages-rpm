# RPM spec for NetXMS packages

This repository contains scripts for creating rpm packages (netxms-server/netxms-agent).

Packages are built by NetXMS team and published on https://packages.netxms.org/.

## Build

```sh
# Build RPMs
docker run --cap-add=SYS_ADMIN -it --rm -v $(pwd):/build -v $(pwd)/result:/result ghcr.io/netxms/builder-rpm:latest

# Same, but cache dependencies between builds
docker run --cap-add=SYS_ADMIN -it --rm -v $(pwd)/cache:/var/cache/mock -v $(pwd):/build -v $(pwd)/result:/result ghcr.io/netxms/builder-rpm:latest
```
