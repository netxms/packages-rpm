# Migrate Drone Pipeline from Mock-Based to Direct RPM Builds

## Overview

Replace the mock-based RPM builder container (ghcr.io/netxms/builder-rpm) with direct rpmbuild in native distro containers (oraclelinux:8-10, fedora:42-43). Each distro/version builds in parallel within per-architecture pipelines, eliminating mock and privileged mode.

## Context

- Files involved:
  - Modify: `.drone.yml`
  - Create: `scripts/build-rpm.sh`
- Current builder: ghcr.io/netxms/builder-rpm:latest (mock-based, from https://github.com/netxms/builder-rpm/)
- Build targets: epel8, epel9, epel10, fedora42, fedora43 (across amd64 and arm64)
- Custom NetXMS package repos required: packages.netxms.org/devel/{epel,fedora}/VERSION and packages.netxms.org/{epel,fedora}/VERSION
- Maven 3.9.12 currently bundled in builder-rpm image, needed for Java components
- Spec file uses %{?rhel} and %{?fedora} conditionals for distro-specific deps

## Development Approach

- Complete each task fully before moving to the next
- No tests applicable (CI pipeline configuration)
- Validate by reviewing generated YAML and script logic

## Implementation Steps

### Task 1: Create build-rpm.sh script

**Files:**
- Create: `scripts/build-rpm.sh`

Build script that handles the full RPM build workflow in a native distro container. Accepts distro type (epel/fedora) and version as arguments.

- [x] Script skeleton with argument parsing (distro type + version)
- [x] EPEL/repo setup for OracleLinux:
  - OL8/9: install oracle-epel-release, enable codeready_builder repo
  - OL10: install oracle-epel-release, enable codeready_builder repo
- [x] Add NetXMS custom repos (devel + release) for build dependencies (libosip2-devel, libnxmodbus-devel, isotree-devel, etc.)
- [x] Run `dnf update -y` to update base image packages
- [x] Install rpm-build and run `dnf builddep -y SPECS/netxms.spec` for build dependencies
- [x] Download and install Apache Maven 3.9.12 (matching current builder-rpm setup), set up PATH and m2 cache at /m2-repo if available
- [x] Create rpmbuild directory structure (BUILD, RPMS, SRPMS) and run `rpmbuild --define "_topdir $(pwd)" -ba SPECS/netxms.spec`
- [x] Copy resulting RPMs from RPMS/*/ to /result/

### Task 2: Rewrite .drone.yml with parallel distro builds

**Files:**
- Modify: `.drone.yml`

Replace mock-based build steps with 5 parallel native-image build steps per architecture.

- [ ] Rewrite build-amd64 pipeline:
  - Keep make-dist step unchanged (ghcr.io/alkk/netxms-make-dist:latest)
  - Replace build-epel and build-fedora with 5 parallel build steps:
    - build-ol8: image oraclelinux:8, runs `scripts/build-rpm.sh epel 8`
    - build-ol9: image oraclelinux:9, runs `scripts/build-rpm.sh epel 9`
    - build-ol10: image oraclelinux:10, runs `scripts/build-rpm.sh epel 10`
    - build-fedora42: image fedora:42, runs `scripts/build-rpm.sh fedora 42`
    - build-fedora43: image fedora:43, runs `scripts/build-rpm.sh fedora 43`
  - All build steps depend on make-dist, no privileged mode
  - Keep result temp volume, replace mock cache volume with m2-repo host volume (/cache/m2-repo)
  - Update upload step to depend on all 5 build steps
- [ ] Rewrite build-arm64 pipeline with identical structure (different platform arch)
- [ ] Keep notify pipeline and telegram notification unchanged
- [ ] Remove signature block (will need re-signing after changes)

### Task 3: Validate

- [ ] Verify .drone.yml syntax with `drone lint` or manual review
- [ ] Verify all Docker image names exist (oraclelinux:8, oraclelinux:9, oraclelinux:10, fedora:42, fedora:43)
- [ ] Verify NetXMS repo URLs for all distro/version/arch combinations
- [ ] Review spec file conditionals work correctly with direct rpmbuild on each distro
