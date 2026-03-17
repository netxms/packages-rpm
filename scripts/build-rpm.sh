#!/bin/bash
set -euo pipefail

if [ $# -ne 2 ]; then
   echo "Usage: $0 <epel|fedora> <version>"
   exit 1
fi

DISTRO_TYPE="$1"
DISTRO_VERSION="$2"

case "$DISTRO_TYPE" in
   epel|fedora) ;;
   *) echo "Unknown distro type: $DISTRO_TYPE (expected epel or fedora)"; exit 1 ;;
esac

if [ "$DISTRO_TYPE" = "epel" ]; then
   if [ "$DISTRO_VERSION" -lt 10 ]; then
      dnf install -y dnf-plugins-core
   else
      dnf install -y dnf5-plugins
   fi
   dnf install -y oracle-epel-release-el${DISTRO_VERSION}
   if [ "$DISTRO_VERSION" -ge 10 ]; then
      dnf config-manager setopt "ol${DISTRO_VERSION}_codeready_builder.enabled=1"
   else
      dnf config-manager --enable ol${DISTRO_VERSION}_codeready_builder
   fi
elif [ "$DISTRO_TYPE" = "fedora" ]; then
   dnf install -y dnf5-plugins
fi

cat > /etc/yum.repos.d/netxms.repo <<EOF
[netxms-devel]
name=NetXMS Development Packages
baseurl=https://packages.netxms.org/devel/${DISTRO_TYPE}/${DISTRO_VERSION}/\$basearch/
gpgcheck=0
enabled=1

[netxms-release]
name=NetXMS Release Packages
baseurl=https://packages.netxms.org/${DISTRO_TYPE}/${DISTRO_VERSION}/\$basearch/
gpgcheck=0
enabled=1
EOF

dnf update -y

dnf install -y rpm-build
dnf builddep -y SPECS/netxms.spec

MAVEN_VERSION=3.9.12
MAVEN_SHA512="0a1be79f02466533fc1a80abbef8796e4f737c46c6574ede5658b110899942a94db634477dfd3745501c80aef9aac0d4f841d38574373f7e2d24cce89d694f70"
MAVEN_TGZ="/tmp/apache-maven-${MAVEN_VERSION}-bin.tar.gz"
curl -fsSL "https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" \
   -o "$MAVEN_TGZ"
echo "$MAVEN_SHA512  $MAVEN_TGZ" | sha512sum -c -
tar xzf "$MAVEN_TGZ" -C /opt
rm -f "$MAVEN_TGZ"
export PATH="/opt/apache-maven-${MAVEN_VERSION}/bin:$PATH"

RPMBUILD_DIR="$(pwd)/rpmbuild-${DISTRO_TYPE}-${DISTRO_VERSION}"
mkdir -p "$RPMBUILD_DIR"/{BUILD,RPMS,SRPMS}
rpmbuild --define "_topdir $RPMBUILD_DIR" \
   --define "_sourcedir $(pwd)/SOURCES" \
   --define "_specdir $(pwd)/SPECS" \
   -ba SPECS/netxms.spec

rpm_count=$(find "$RPMBUILD_DIR/RPMS/" -name '*.rpm' | wc -l)
if [ "$rpm_count" -eq 0 ]; then
   echo "ERROR: rpmbuild produced no RPMs"
   exit 1
fi

mkdir -p /result
find "$RPMBUILD_DIR/RPMS/" -name '*.rpm' -exec cp {} /result/ \;
