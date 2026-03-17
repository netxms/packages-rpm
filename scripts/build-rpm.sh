#!/bin/bash
set -euo pipefail

if [ $# -ne 2 ]; then
   echo "Usage: $0 <epel|fedora> <version>"
   exit 1
fi

DISTRO_TYPE="$1"
DISTRO_VERSION="$2"
ARCH=$(uname -m)

case "$DISTRO_TYPE" in
   epel|fedora) ;;
   *) echo "Unknown distro type: $DISTRO_TYPE (expected epel or fedora)"; exit 1 ;;
esac

if [ "$DISTRO_TYPE" = "epel" ]; then
   dnf install -y oracle-epel-release-el${DISTRO_VERSION}
   dnf config-manager --enable ol${DISTRO_VERSION}_codeready_builder
fi

cat > /etc/yum.repos.d/netxms-devel.repo <<EOF
[netxms-devel]
name=NetXMS Development Packages
baseurl=https://packages.netxms.org/devel/${DISTRO_TYPE}/${DISTRO_VERSION}/${ARCH}/
gpgcheck=0
enabled=1
EOF

cat > /etc/yum.repos.d/netxms-release.repo <<EOF
[netxms-release]
name=NetXMS Release Packages
baseurl=https://packages.netxms.org/${DISTRO_TYPE}/${DISTRO_VERSION}/${ARCH}/
gpgcheck=0
enabled=1
EOF

dnf update -y

dnf install -y rpm-build
dnf builddep -y SPECS/netxms.spec

MAVEN_VERSION=3.9.12
curl -fsSL "https://dlcdn.apache.org/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" \
   | tar xzf - -C /opt
export PATH="/opt/apache-maven-${MAVEN_VERSION}/bin:$PATH"
if [ -d /m2-repo ]; then
   export MAVEN_OPTS="-Dmaven.repo.local=/m2-repo"
fi

mkdir -p BUILD RPMS SRPMS
rpmbuild --define "_topdir $(pwd)" -ba SPECS/netxms.spec

mkdir -p /result
find RPMS/ -name '*.rpm' -exec cp {} /result/ \;
