# vim: ts=3 sw=3 expandtab
Summary:       NetXMS umbrella package
Name:          netxms
Version:       5.0.6
Release:       1%{?dist}
License:       GPL
URL:           https://netxms.org
Group:         Admin
Source0:       %{name}-%{version}.tar.gz

Source100:     netxms-server.service
Source101:     netxms-agent.service
Source102:     netxms-reporting.service

Source200:     netxmsd.conf
Source201:     nxagentd.conf

Requires:      systemd

BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: maven
BuildRequires: chrpath

BuildRequires: expat-devel
BuildRequires: jansson-devel
BuildRequires: (java-17-openjdk-devel or java-11-openjdk-devel)
BuildRequires: libcurl-devel
BuildRequires: libmicrohttpd-devel
BuildRequires: libssh-devel
BuildRequires: libvirt-devel
BuildRequires: lm_sensors-devel
BuildRequires: mosquitto-devel
BuildRequires: openldap-devel
BuildRequires: openssl-devel
BuildRequires: pcre-devel
BuildRequires: readline-devel
BuildRequires: systemd-devel
BuildRequires: zeromq-devel
BuildRequires: zlib-devel

BuildRequires: (oracle-instantclient-devel or oracle-instantclient19.10-devel)
BuildRequires: mariadb-connector-c-devel
BuildRequires: postgresql-devel
BuildRequires: sqlite-devel
BuildRequires: unixODBC-devel

%ifnarch aarch64
BuildRequires: jemalloc-devel = 5.3.0-1%{?dist}_netxms
%define configure_jemalloc --with-jemalloc
%endif
BuildRequires: libosip2-devel = 5.3.0-1%{?dist}_netxms libexosip2-devel = 5.3.0-1%{?dist}_netxms
BuildRequires: libnxmodbus-devel = 3.1.10-5%{?dist}
BuildRequires: isotree-devel >= 0.6.1-1%{?dist}

%description

%prep
%setup -q

%build
if [ -a /m2-repo ]; then
   rm -rf /m2-repo/org/netxms
   export MAVEN_OPTS='-Dmaven.repo.local=/m2-repo'
fi

[ -r /usr/include/oracle/19.10/client64 ] && export ORACLE_CPPFLAGS=-I/usr/include/oracle/19.10/client64 ORACLE_LDFLAGS=-L/usr/lib/oracle/19.10/client64/lib
[ -r /usr/include/oracle/19.16/client64 ] && export ORACLE_CPPFLAGS=-I/usr/include/oracle/19.16/client64 ORACLE_LDFLAGS=-L/usr/lib/oracle/19.16/client64/lib
[ -r /usr/include/oracle/21/client64 ] && export ORACLE_CPPFLAGS=-I/usr/include/oracle/21/client64 ORACLE_LDFLAGS=-L/usr/lib/oracle/21/client64/lib

%configure \
   --enable-release-build \
   --with-server \
   --with-agent \
   --with-client \
   --with-sqlite \
   --with-pgsql \
   --with-odbc \
   --enable-unicode \
   --with-jdk=/usr/lib/jvm/java \
   --without-gui-client \
   --with-vmgr \
   --with-libjq \
   --with-mariadb \
   --with-mariadb-compat-headers \
   --with-zeromq \
   --with-oracle \
   %{?configure_jemalloc} \
   --with-asterisk

#sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
#sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

[ -e /usr/lib/jvm/java-11 ] && export JAVA_HOME=/usr/lib/jvm/java-11
[ -e /usr/lib/jvm/java-17 ] && export JAVA_HOME=/usr/lib/jvm/java-17

cp build/netxms-build-tag.properties src/java-common/netxms-base/src/main/resources/
mvn --batch-mode -f src/pom.xml versions:set -DnewVersion=$(grep NETXMS_VERSION= build/netxms-build-tag.properties | cut -d = -f 2) -DprocessAllModules=true
mvn --batch-mode -f src/client/nxmc/java/pom.xml versions:set -DnewVersion=$(grep NETXMS_VERSION= build/netxms-build-tag.properties | cut -d = -f 2)
mvn --batch-mode -f src/pom.xml install -Dmaven.test.skip=true -Dmaven.javadoc.skip=true

make %{?_smp_mflags}

%install
[ -a /m2-repo ] && export MAVEN_OPTS='-Dmaven.repo.local=/m2-repo'

rm -rf %{buildroot}

%make_install

install -m755 -d %{buildroot}%{_unitdir}
install -m755 -d %{buildroot}%{_sysconfdir}

install -m644 %{SOURCE100} %{buildroot}%{_unitdir}/netxms-server.service
install -m644 %{SOURCE101} %{buildroot}%{_unitdir}/netxms-agent.service
install -m644 %{SOURCE102} %{buildroot}%{_unitdir}/netxms-reporting.service

install -p -m644 %{SOURCE200} %{buildroot}%{_sysconfdir}/netxmsd.conf
install -p -m644 %{SOURCE201} %{buildroot}%{_sysconfdir}/nxagentd.conf

pushd %{buildroot}%{_libdir}/netxms
   ln -s mysql.nsm mariadb.nsm
popd

#rm -f %{buildroot}%{_libdir}/*.la

# remove rpath from binaries
chrpath --delete %{buildroot}%{_bindir}/nddload
chrpath --delete %{buildroot}%{_bindir}/netxmsd
chrpath --delete %{buildroot}%{_bindir}/nxaction
chrpath --delete %{buildroot}%{_bindir}/nxadm
chrpath --delete %{buildroot}%{_bindir}/nxaevent
chrpath --delete %{buildroot}%{_bindir}/nxagentd
chrpath --delete %{buildroot}%{_bindir}/nxalarm
chrpath --delete %{buildroot}%{_bindir}/nxap
chrpath --delete %{buildroot}%{_bindir}/nxappget
chrpath --delete %{buildroot}%{_bindir}/nxapush
chrpath --delete %{buildroot}%{_bindir}/nxcsum
chrpath --delete %{buildroot}%{_bindir}/nxdbmgr
chrpath --delete %{buildroot}%{_bindir}/nxdevcfg
chrpath --delete %{buildroot}%{_bindir}/nxdownload
chrpath --delete %{buildroot}%{_bindir}/nxencpasswd
chrpath --delete %{buildroot}%{_bindir}/nxethernetip
chrpath --delete %{buildroot}%{_bindir}/nxevent
chrpath --delete %{buildroot}%{_bindir}/nxgenguid
chrpath --delete %{buildroot}%{_bindir}/nxget
chrpath --delete %{buildroot}%{_bindir}/nxhwid
chrpath --delete %{buildroot}%{_bindir}/nxlptest
chrpath --delete %{buildroot}%{_bindir}/nxmibc
chrpath --delete %{buildroot}%{_bindir}/nxminfo
chrpath --delete %{buildroot}%{_bindir}/nxnotify
chrpath --delete %{buildroot}%{_bindir}/nxping
chrpath --delete %{buildroot}%{_bindir}/nxpush
chrpath --delete %{buildroot}%{_bindir}/nxscript
chrpath --delete %{buildroot}%{_bindir}/nxshell
chrpath --delete %{buildroot}%{_bindir}/nxsnmpget
chrpath --delete %{buildroot}%{_bindir}/nxsnmpset
chrpath --delete %{buildroot}%{_bindir}/nxsnmpwalk
chrpath --delete %{buildroot}%{_bindir}/nxtftp
chrpath --delete %{buildroot}%{_bindir}/nxupload
chrpath --delete %{buildroot}%{_bindir}/nxwsget

# remove rpath from libs
chrpath --delete %{buildroot}%{_libdir}/lib*.so*
chrpath --delete %{buildroot}%{_libdir}/netxms/*.nxm %{buildroot}%{_libdir}/netxms/*.nsm %{buildroot}%{_libdir}/netxms/*.hdlink
chrpath --delete %{buildroot}%{_libdir}/netxms/dbdrv/*.ddr
chrpath --delete %{buildroot}%{_libdir}/netxms/ncdrv/*.ncd
chrpath --delete %{buildroot}%{_libdir}/netxms/ndd/*.ndd
chrpath --delete %{buildroot}%{_libdir}/netxms/pdsdrv/*.pdsd

%files

%exclude %{_bindir}/*-asan
%exclude %{_bindir}/nddload
%exclude %{_bindir}/nx-run-asan-binary
%exclude %{_bindir}/nxdevcfg
%exclude %{_bindir}/nxdevcfg
%exclude %{_datadir}/netxms/lsan-suppressions.txt
%exclude %{_includedir}/netxms-build-tag.h
%exclude %{_libdir}/*.la
%exclude %{_libdir}/*.so
%exclude %{_libdir}/*.so
%exclude %{_libdir}/netxms/ncdrv/mqtt.ncd
%exclude %{_libdir}/netxms/spe.nxm

%doc

### netxms-base
%package base
Summary: Common NetXMS libraries and tools

%description base
This package provides various netxms libraries and tools which are
shared between other packages.

%files base
%{_bindir}/nx-collect-server-diag
%{_bindir}/nxcsum
%{_bindir}/nxencpasswd
%{_bindir}/nxgenguid
%{_bindir}/nxping
%{_libdir}/libnetxms.so.*
%{_libdir}/libnxclient.so.*
%{_libdir}/libnxdb.so.*
%{_libdir}/libnxsnmp.so.*


### netxms-agent
%package agent
Summary: NetXMS agent and extensions (subagents)
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(post): systemd
Requires: netxms-dbdrv-sqlite3 = %{version}-%{release}

%description agent
This package provides agent and agent-related diagnostic and integration tools.
Most of the subagents which does not require additional dependences are included as well.

%pre agent

%post agent
%systemd_post netxms-agent.service

%preun agent
%systemd_preun netxms-agent.service

%postun agent
%systemd_postun netxms-agent.service

%files agent
%config(noreplace) %{_sysconfdir}/nxagentd.conf
%{_bindir}/nxaevent
%{_bindir}/nxagentd
%{_bindir}/nxagentd-generate-tunnel-config
%{_bindir}/nxappget
%{_bindir}/nxapush
%{_bindir}/nxhwid
%{_bindir}/nxlptest
%{_bindir}/nxtftp
%{_libdir}/libappagent.so.*
%{_libdir}/libnxagent.so.*
%{_libdir}/libnxlp.so.*
%{_libdir}/netxms/bind9.nsm
%{_libdir}/netxms/dbquery.nsm
%{_libdir}/netxms/devemu.nsm
%{_libdir}/netxms/ds18x20.nsm
%{_libdir}/netxms/filemgr.nsm
%{_libdir}/netxms/gps.nsm
%{_libdir}/netxms/linux.nsm
%{_libdir}/netxms/lmsensors.nsm
%{_libdir}/netxms/logwatch.nsm
%{_libdir}/netxms/netsvc.nsm
%{_libdir}/netxms/ping.nsm
%{_libdir}/netxms/sms.nsm
%{_libdir}/netxms/ssh.nsm
%{_libdir}/netxms/ups.nsm
%{_unitdir}/netxms-agent.service


### netxms-agent-asterisk
%package agent-asterisk
Summary: Agent extension (subagent) for monitoring Asterisk

%description agent-asterisk
This package allows you to collect health metrics and statistics from Asterisk instance.

%files agent-asterisk
%{_libdir}/netxms/asterisk.nsm


### netxms-java-base
%package java-base
Summary: Common java libraries used by the NetXMS components
Requires: (java-17-openjdk-headless or java-11-openjdk-headless)

%description java-base
This package provides java libraries which are shared by various components
like netxms-reporting and java subagent (netxms-agent-java)

%files java-base
%{_libdir}/libnxjava.so.*
%{_libdir}/netxms/java/SparseBitSet-*.jar
%{_libdir}/netxms/java/commons-codec-*.jar
%{_libdir}/netxms/java/commons-collections4-*.jar
%{_libdir}/netxms/java/commons-compiler-*.jar
%{_libdir}/netxms/java/commons-io-*.jar
%{_libdir}/netxms/java/commons-math3-*.jar
%{_libdir}/netxms/java/janino-*.jar
%{_libdir}/netxms/java/log4j-api-*.jar
%{_libdir}/netxms/java/logback-classic-*.jar
%{_libdir}/netxms/java/logback-core-*.jar
%{_libdir}/netxms/java/netxms-base-*.jar
%{_libdir}/netxms/java/netxms-client-*.jar
%{_libdir}/netxms/java/netxms-java-bridge-*.jar
%{_libdir}/netxms/java/poi-*.jar
%{_libdir}/netxms/java/simple-xml-safe-*.jar
%{_libdir}/netxms/java/slf4j-api-*.jar


### netxms-agent-java
%package agent-java
Summary: Agent extension (subagent) for running java-based monitoring providers
Requires: netxms-java-base = %{version}-%{release}

%description agent-java
This pacakge provides bridge to java monitoring plugins like JMX or OPCUA.

%files agent-java
%{_libdir}/netxms/java.nsm
%{_libdir}/netxms/java/jmx.jar
%{_libdir}/netxms/java/netxms-agent-*.jar
%{_libdir}/netxms/java/ubntlw.jar
%{_libdir}/netxms/java/opcua.jar


### netxms-agent-oracle
%package agent-oracle
Summary: Agent extension (subagent) for monitoring Oracle databases
Requires: netxms-dbdrv-oracle = %{version}-%{release}

%description agent-oracle
This package extends agent to collect health metrics and statistics from one of more Oracle instances.

%files agent-oracle
%{_libdir}/netxms/oracle.nsm

### netxms-agent-mariadb
%package agent-mariadb
Summary: Agent extension (subagent) for monitoring MySQL/MariaDB databases
Requires: netxms-dbdrv-mariadb = %{version}-%{release}

%description agent-mariadb
This package extends agent to collect health metrics and statistics from one of more MySQL/MariaDB instances.

%files agent-mariadb
%{_libdir}/netxms/mariadb.nsm
%{_libdir}/netxms/mysql.nsm


### netxms-agent-pgsql
%package agent-pgsql
Summary: Agent extension (subagent) for monitoring PostgreSQL databases
Requires: netxms-dbdrv-pgsql = %{version}-%{release}

%description agent-pgsql
This package extends agent to collect health metrics and statistics from one of more PostgreSQL instances.

%files agent-pgsql
%{_libdir}/netxms/pgsql.nsm


### netxms-agent-mqtt
%package agent-mqtt
Summary: Agent extension (subagents) for communicating wiht MQTT brokers

%description agent-mqtt
This package extends agent to enable communications with MQTT brokers.
You can both subscribe to topics and publish.

%files agent-mqtt
%{_libdir}/netxms/mqtt.nsm


### netxms-agent-vmgr
%package agent-vmgr
Summary: Agent extension (subagents) for monitoring virtualization platforms

%description agent-vmgr
This subagent use libvirt to communicate with any supported virtualization platform -
KVM, Hypervisor.framework, QEMU, Xen, Virtuozzo, VMWare ESX, LXC, BHyve and more.

%files agent-vmgr
%{_libdir}/netxms/vmgr.nsm


### netxms-client
%package client
Summary: Integration and diagnostics tools for the NetXMSX server.
Requires: netxms-java-base = %{version}-%{release}

%description client
This package provides various integration tools (e.g. nxshell).

%files client
%{_bindir}/nxalarm
%{_bindir}/nxevent
%{_bindir}/nxnotify
%{_bindir}/nxpush
%{_bindir}/nxshell
%{_libdir}/netxms/java/jython-standalone-2.7.4b1.jar
%{_libdir}/netxms/java/nxshell-*.jar


### netxms-server
%package server
Summary: Monitoring server core
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(post): systemd
Requires: (netxms-dbdrv-pgsql = %{version}-%{release} or netxms-dbdrv-mariadb = %{version}-%{release} or netxms-dbdrv-oracle = %{version}-%{release} or netxms-dbdrv-sqlite3 = %{version}-%{release} or netxms-dbdrv-odbc = %{version}-%{release})
Requires: netxms-agent = %{version}-%{release}

%description server
...

%post server
%systemd_post netxms-server.service

if [ $1 -eq 1 ]; then
   cat <<__END
NetXMS server is installed but currently stopped.

Additional steps required:

1. Edit default configuration file (%{_sysconfdir}/netxmsd.conf)

2. Create database schema:

   nxdbmgr init

3. Start daemon and enable autostart:

   systemctl start netxms-server
   systemctl enable netxms-server
__END
fi

%preun server
%systemd_preun netxms-server.service

%postun server
%systemd_postun netxms-server.service

%files server
%config(noreplace) %{_sysconfdir}/netxmsd.conf

%{_bindir}/netxmsd
%{_bindir}/nxaction
%{_bindir}/nxadm
%{_bindir}/nxap
%{_bindir}/nxdbmgr
%{_bindir}/nxdownload
%{_bindir}/nxethernetip
%{_bindir}/nxget
%{_bindir}/nxmibc
%{_bindir}/nxminfo
%{_bindir}/nxscript
%{_bindir}/nxsnmp*
%{_bindir}/nxupload
%{_bindir}/nxwsget
%{_datadir}/netxms/mibs/*.txt
%{_datadir}/netxms/oui/*.csv
%{_datadir}/netxms/radius.dict
%{_datadir}/netxms/sql/*.sql
%{_datadir}/netxms/templates/*.xml
%{_libdir}/libethernetip.so.*
%{_libdir}/libnxcore.so.*
%{_libdir}/libnxdbmgr.so.*
%{_libdir}/libnxsl.so.*
%{_libdir}/libnxsrv.so.*
%{_libdir}/libstrophe.so.*
%{_libdir}/netxms/*.hdlink
%{_libdir}/netxms/*.nxm
%{_libdir}/netxms/ncdrv/anysms.ncd
%{_libdir}/netxms/ncdrv/dbtable.ncd
%{_libdir}/netxms/ncdrv/dummy.ncd
%{_libdir}/netxms/ncdrv/googlechat.ncd
%{_libdir}/netxms/ncdrv/gsm.ncd
%{_libdir}/netxms/ncdrv/kannel.ncd
# % {_libdir}/netxms/ncdrv/mqtt.ncd
%{_libdir}/netxms/ncdrv/msteams.ncd
%{_libdir}/netxms/ncdrv/mymobile.ncd
%{_libdir}/netxms/ncdrv/nexmo.ncd
%{_libdir}/netxms/ncdrv/nxagent.ncd
%{_libdir}/netxms/ncdrv/portech.ncd
%{_libdir}/netxms/ncdrv/shell.ncd
%{_libdir}/netxms/ncdrv/slack.ncd
%{_libdir}/netxms/ncdrv/smseagle.ncd
%{_libdir}/netxms/ncdrv/smtp.ncd
%{_libdir}/netxms/ncdrv/snmptrap.ncd
%{_libdir}/netxms/ncdrv/telegram.ncd
%{_libdir}/netxms/ncdrv/text2reach.ncd
%{_libdir}/netxms/ncdrv/textfile.ncd
%{_libdir}/netxms/ncdrv/twilio.ncd
%{_libdir}/netxms/ncdrv/websms.ncd
%{_libdir}/netxms/ncdrv/xmpp.ncd
%{_libdir}/netxms/ndd/*
%{_libdir}/netxms/pdsdrv/*
%{_sharedstatedir}/netxms/*
%{_unitdir}/netxms-server.service


### netxms-dbdrv-sqlite3
%package dbdrv-sqlite3
Summary: Middleware for interfacing with SQLite3 database engine

%description dbdrv-sqlite3
...

%files dbdrv-sqlite3
%{_libdir}/netxms/dbdrv/sqlite.ddr


### netxms-dbdrv-pgsql
%package dbdrv-pgsql
Summary: Middleware for interfacing with PostgreSQL database engine

%description dbdrv-pgsql
...

%files dbdrv-pgsql
%{_libdir}/netxms/dbdrv/pgsql.ddr


## netxms-dbdrv-mariadb
%package dbdrv-mariadb
Summary: ...

%description dbdrv-mariadb
...

%files dbdrv-mariadb
%{_libdir}/netxms/dbdrv/mariadb.ddr


### netxms-dbdrv-odbc
%package dbdrv-odbc
Summary: Middleware for interfacing with any compatible database engine via ODBC

%description dbdrv-odbc
...

%files dbdrv-odbc
%{_libdir}/netxms/dbdrv/odbc.ddr


### netxms-dbdrv-oracle
%package dbdrv-oracle
Summary: Middleware for interfacing with Oracle database engine
Requires: (oracle-instantclient-basic or oracle-instantclient-basiclite or oracle-instantclient19.10-basic or oracle-instantclient19.10-basiclite)

%description dbdrv-oracle
...

%files dbdrv-oracle
%{_libdir}/netxms/dbdrv/oracle.ddr


### netxms-reporting
%package reporting
Summary: JasperReports-based reporting server integrated into NetXMS
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(post): systemd
Requires: (java-17-openjdk-headless or java-11-openjdk-headless)
Requires: netxms-java-base = %{version}-%{release}

%description reporting
...

%post reporting
%systemd_post netxms-reporting.service

%preun reporting
%systemd_preun netxms-reporting.service

%postun reporting
%systemd_postun netxms-reporting.service

%files reporting
%{_bindir}/nxreportd
%{_libdir}/netxms/java/activation-*.jar
%{_libdir}/netxms/java/caffeine-*.jar
%{_libdir}/netxms/java/checker-qual-*.jar
%{_libdir}/netxms/java/commons-beanutils-*.jar
%{_libdir}/netxms/java/commons-collections-*.jar
%{_libdir}/netxms/java/commons-daemon-*.jar
%{_libdir}/netxms/java/commons-digester-*.jar
%{_libdir}/netxms/java/commons-logging-*.jar
%{_libdir}/netxms/java/ecj-*.jar
%{_libdir}/netxms/java/error_prone_annotations-*.jar
%{_libdir}/netxms/java/jackson-annotations-*.jar
%{_libdir}/netxms/java/jackson-core-*.jar
%{_libdir}/netxms/java/jackson-databind-*.jar
%{_libdir}/netxms/java/jackson-dataformat-xml-*.jar
%{_libdir}/netxms/java/jasperreports-*.jar
%{_libdir}/netxms/java/jcl-over-slf4j-*.jar
%{_libdir}/netxms/java/jcommon-*.jar
%{_libdir}/netxms/java/jfreechart-*.jar
%{_libdir}/netxms/java/jna-*.jar
%{_libdir}/netxms/java/mail-*.jar
%{_libdir}/netxms/java/mariadb-java-client-*.jar
%{_libdir}/netxms/java/mssql-jdbc-*.jre8.jar
%{_libdir}/netxms/java/mysql-connector-j-*.jar
%{_libdir}/netxms/java/nxreportd-*.jar
%{_libdir}/netxms/java/ojdbc10-*.jar
%{_libdir}/netxms/java/openpdf-*.jar
%{_libdir}/netxms/java/postgresql-*.jar
%{_libdir}/netxms/java/protobuf-java-*.jar
%{_libdir}/netxms/java/stax2-api-*.jar
%{_libdir}/netxms/java/waffle-jna-*.jar
%{_libdir}/netxms/java/woodstox-core-*.jar
%{_libdir}/netxms/java/xercesImpl-*.jar
%{_libdir}/netxms/java/xml-apis-*.jar
%{_unitdir}/netxms-reporting.service

%changelog
* Wed Jul 17 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.6-1
- Added notification channel driver for Mattermost
- Topic support in notification channel driver for Telegram
- Fixed incorrect client IP address reported iby Windows agent in table System.ActiveUserSessions
- Fixed bug in output of nxget -U
- Fixed web UI crash when opening dashboard in kiosk mode
- Fixed issues:
-   NX-2550 (Errors in desktop client log (Widget is disposed))

* Fri Jun 28 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.5-1
- L2 network map seeds with no SNMP or L2 data will not prevent network map from update
- Server performance improvements
- Server actions of types "agent command" and "SSH command" executed asynchronously (partial fix for NX-2541)
- Fixed server crash during LDAP synchronization
- Subnets bound to containers correctly displayed in infrastructure perspective
- Predefined maps with default size and background image resized automatically to be no less than image size

* Tue Jun 11 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.4-1
- New SNMP DCI option "Interpret raw value as IPv6 address"
- Added driver for GE MDS Orbit devices
- Added driver for EtherWan switches
- Added driver for Siemens RuggedCom switches
- Mikrotik driver reports RSSI for wireless clients
- RSSI is displayed in "Wireless Stations" view
- Added "move object" item to object context menu
- Optional context selector for dashboards in dashboard perspective
- Seed node propery page removed for custom network maps
- Fixed server crash when accessing alarm category list from NXSL
- Fixed drawing issues of line charts with logarithmic scale
- Fixed incorrect line numbers in NXSL error messages
- Fixed bug in "Go to object" action in UI
- Fixed bug in D-Link driver
- Fixed interface utilization information sychronization
- Fixed network map color source selection
- Fixed historical line chart pop-out on web
- Fixed save of network map object position
- Fixed tables display glitch on Windows
- Fixed data type of configuration variable "Objects.NetworkMaps.UpdateInterval"
- Fixed issues:
-   NX-2489 (Read list of performance counters only when needed)
-   NX-2536 (SNMP DCI "interpret raw value as MAC address" does not support EUI-64)
-   NX-2537 (Double links on maps)

* Wed May 15 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.3-1
- Notification channel driver "Shell" escapes single quote character during exec-type command line expansion
- Priority inclusion rules in UI element filter
- Macro expansion in API call executeLibraryScript works for all object classes
- Improved handling of large number of simultaneous ICMP ping requests
- Fixed bug in database upgrade procedure
- Fixed deadlock in web UI
- Fixed issues:
-   NX-2521 (ICMP.PacketLoss internal DCI collects 0 after server restart)
-   NX-2529 (Option to enable/disable Version Number on Web interface)

* Tue May 07 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.2-1
- Fixed bug in database upgrade procedure
- Fixed "pin to pinboard" in UI

* Fri May 03 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.1-1
- Fixed bug in database upgrade procedure
- Added CSV export in alarm viewer and agent tunnel manager

* Wed May 01 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.0-1
- Improved network maps
- Added network map link styling script
- Delegate access option that allows read access to network maps without full read access to objects on a map
- Reworked monitoring of wireless access points and controllers
- Major overhaul of sensor objects
- Many NXSL function deprecated in favor of object methods
- Improved NXSL classes and functions for date/time handling
- Add option to check alarm details from alarm log view
- Log parser rules can define metrics that are populated from match data
- Special NXSL return codes for data collection and transformation scripts (DataCollection::ERROR, DataCollection::NOT_SUPPORTED, DataCollection::NO_SUCH_INSTANCE)
- New NXSL function FindAccessPointByMACAddress
- New NXSL function GetMappingTableKeys
- "Stop" function in script executor view
- Desktop client can reconnect automatically after short connectivity loss
- New agent metric File.Hash.SHA256
- New agent list and table Net.IP.Neighbors
- Index property displayed in MIB browser
- Root object can be set for object query
- Improved SNMP trap processing performance
- New log parser file option "removeEscapeSequences"
- Added peer certififcate verification issue tracker integration
- Housekeeper scripts (NXSL and SQL)
- Improved REST API
- Introduces new object class "Collector"
- Downtime log controlled by EPP
- Fixed issues:
-   NX-797 (Automatic reconnect of management console)
-   NX-1790 (Drag-n-dropped object are positioned to wrong place when map is scrolled down or right)
-   NX-1870 (Representation of float DCI that gets string data as input)
-   NX-1935 (Introduce hook script on map regeneration with ability to set link names)
-   NX-2006 (Remove example event templates (code 4000-4011) from database)
-   NX-2076 (Raw value should be always displayed as string)
-   NX-2292 (Automatic maps should not include nodes that are connected through a node that was excluded by filter script)
-   NX-2323 (Make parameters in all events named)
-   NX-2343 (Several changes in NXSL syntax in v 5.0)
-   NX-2375 (Use "varchar(max)" instead of "text" on Microsoft SQL Server)
-   NX-2403 (Add support for AES-192 and AES-256 in SNMPv3)
-   NX-2444 (On demand background external metrics)
-   NX-2455 (Ability to check TLS.Certificate.\* for protocols with STARTTLS command)
-   NX-2481 (Add ability to manually poll network map generation)
-   NX-2507 (Add ability to cancel timers from NXSL)
-   NX-2520 (Remove "Channel name" selector from "Send notification" dialog)
-   NX-2523 (New agent metric Process.MemoryUsage (percentage of memory used by process))
-   NX-2524 (Option to disable threshold without deleting it)
-   NX-2525 (Add the ability to specify multiplier values in threshold)
-   NX-2526 (When editing a template with a DCI without instance to use instance - DCI becomes unsupported)

* Mon Apr 15 2024 Victor Kirhenshtein <victor@netxms.org> - 4.5.6-1
- Fixed bug in background task scheduler
- Fixed bug in reporting access control
- Fixed minor memory leak in server
- Fixed event storm detection event generation
- Fixed incorrect notification popup size calculation in user agent
- Fixed bug in NXSL function CreateUserAgentNotification
- Improved housekeeper throttling logic
- User-defined scripts for housekeeper
- Object context menu available in alarm view
- Call for DCI status change added to web API

* Mon Apr 01 2024 Victor Kirhenshtein <victor@netxms.org> - 4.5.5-1
- Fixed scheduled file upload
- Fixed policy apply on object selection change
- Fixed custom attribute conflict propagation and conflict removal
- Fixed agent crash on empty output from external table provider
- Fixed bug in pin/popup agent file view
- Updated OPC UA subagent dependencies
- New agent metrics System.CurrentTime.ISO8601.Local, System.CurrentTime.ISO8601.UTC, and System.TimeZoneOffset
- Bundled zlib updated to latest version
- Print exception trace replaced by error logging
- Disable walk action on root object in mib browser
- Business service polls can be disabled or will not be executed if object is unmanaged
- Added peer certificate verification for notification channels
- Fixed issues:
-   NX-2511 (In repeating events, you can specify no more than 5 characters, sometimes more is needed)
-   NX-2516 (CURLAUTH_NEGOTIATE in not available in libCURL 7.29.0)

* Thu Mar 07 2024 Victor Kirhenshtein <victor@netxms.org> - 4.5.4-1
- Improved Juniper driver
- Improved integration with ticketing system Redmine
- Fixed build errors on Solaris 11.4 with Solaris Studio 12.6
- Fixed memory leak in web UI (server side)
- Fixed some server performance issues
- Fixed issues:
-   NX-2492 (Custom attribute inheritance conflict not detected)
-   NX-2515 (Inherited object custom attributes not deleted from children)

* Fri Feb 16 2024 Victor Kirhenshtein <victor@netxms.org> - 4.5.3-1
- Fixed server crash during passive network discovery
- Fixed bug in dashboard chart data source editor
- Fixed bug in TCP proxy session setup
- Fixed issues:
-   NX-2509 (productVersion does not display value correctly with Ethernet-IP)

* Thu Feb 08 2024 Victor Kirhenshtein <victor@netxms.org> - 4.5.2-1
- Fixed server crash on client session disconnect
- Fixed updated issues in new web UI
- Cosmetic fixes in UI
- Fixed issues:
-   NX-2490 (Server tries to read from tdata_xxxx table when TimescaleDB is used as backend)
-   NX-2502 (nxagentd uses UDP port 4700 to exchange hearthbeat messages and listens on address 0.0.0.0)

* Wed Feb 07 2024 Alex Kirhenshtein <alk@netxms.org> - 4.5.1-1
- Driver for Edgecore enterprise switches
- Driver for HPE Aruba Networking switches and wireless controllers
- Chart height in performance view automatically adjusted to accomodate large legend
- New NXSL class "MacAddress"
- Attribute "state" of NXSL class "AccessPoint" renamed to "apState" (to avoid conflict with attribute "state" from parent class)
- Context object views can be hidden
- Configurable timeout for client session first packet
- Improved VLAN handling by generic driver
- Updated Eltex driver
- Fix missing object synchronization for ad-hock maps (drill down)
- Fixed server crash when interface list cannot be read from SNMP device and option to ignore interfaces in NOT PRESENT state is on
- Fixed bug in EPP rule copying
- Fixed line numbering bug in desktop UI script editor
- Fixed issues:
-   NX-2491 (Add alarm category attribute to NXSL alarm class)
-   NX-2493 (Activation / Deactivation event not shown in threshold editor)

* Mon Dec 25 2023 Alex Kirhenshtein <alk@netxms.org> - 4.5.0-1
- XPath can be used for querying XML-based web services
- New NXSL operation "?." (safe dereference)
- New method "join" in NXSL arrays
- Server-side custom attributes (not visible by clients)
- Additional argument in NXSL method createSNMPTransport to control if it should fail when node is marked as unreachable via SNMP
- Updated drivers for Eltex and TP-Link switches
- Added agent metric Agent.LocalDatabase.FileSize
- Fixed internal metrics PollTime.\*
- Fixed issues:
-   NX-1409 (Implement separate access right for editing object comments)
-   NX-2412 (Separate access right for editing agent configuration file)
-   NX-2440 (Wildcard imports in NXSL)
-   NX-2275 (Option for ignoring interfaces in NOT PRESENT state)
-   NX-2485 (XPath support in web service queries)
-   NX-2487 (Any changes to object from UI or via Java API wipe out responsible users list)

* Fri Dec 08 2023 Alex Kirhenshtein <alk@netxms.org> - 4.4.5-1
- Improved SNMP proxy performance under heavy load
- Added limit on number of nested NXSL VMs (to prevent accidential infinite loop of script execution)
- Fixed server crash on polling TP-Link switches
- Fixed bug in dashboard element "status indicator"
- Fixed bug in status map view
- Fixed bug in database manager check function
- Fixed "Failed to register resource" error in web UI
- Fixed database import/migration to TimescaleDB
- Java components switched to logback 1.3.13 (fixes CVE-2023-6378)
- Fixed issues:
-   NX-2465 (List of saved queries in Tools->Find Object is not updated when query list is altered in Configuration)
-   NX-2479 (Misleading error messages when loading properties for root objects)

* Tue Nov 28 2023 Alex Kirhenshtein <alk@netxms.org> - 4.4.4-1
- New methods in NXSL class "InetAddress": contains, equals, inRange, sameSubnet
- Constructor for NXSL class "InetAddress" accepts mask length as second argument
- Fixed incorrect ICMP polling if ICMP proxy set on node level
- Improved topology discovery on TP-Link devices
- Improved driver for DLink devices
- Added driver for TP-Link devices
- Added driver for Eltex devices
- Added driver for Q-tech devices
- nxencpasswd can read password from terminal
- GUI clients built with patched version of simple-xml (fixes CVE-2017-1000190)
- Fixed deadlock after login in legacy web UI
- Fixed issues:
-   NX-2431 (Implement agent list Net.IP.RoutingTable for AIX)
-   NX-2478 (Named function parameters does not work for entry points)

* Thu Nov 02 2023 Alex Kirhenshtein <alk@netxms.org> - 4.4.3-1
- Package deployment can be scheduled
- Server-side macro expansion in package deployment command
- Use compact JSON format when saving events to database
- Improved event processing performance
- Improved NXSL function "random"
- New event processing macros %d (DCI description), %D (DCI comments), %L (object alias), and %C (object comments)
- Added driver for FortiGate devices
- Fixed server crash during execution of delayed EPP action
- Fixed server crash when processing interfaces with 8 byte MAC address
- Fixed session disconnect handling in new management client application
- Fixed bug in physical disk information reading on Windows
- Fixed bug in SSH key store
- Improved debug logging
- Minor fixes and improvements in new management client application
- Fixed issues:
-   NX-1063 (Interface icon is incorrect)
-   NX-2224 (Command history in nxadm)
-   NX-2446 (Increase timeout for agent tunnel binding)
-   NX-2463 (Add metric to measure execution time of background queries in dbquery subagent)
-   NX-2467 (Allow to execute same action multiple times in one EPP rule)
-   NX-2468 (NetworkService.Status SMTP call to curl_easy_perform failed (56: Command failed: 502))
-   NX-2469 (Empty "Parameters" line should be interpreted as no arguments in Execute Script)
-   NX-2471 (Add agent list and table to list physical disks)
-   NX-2475 (netsvc: ServiceCheck.SMTP() uses VRFY command, which is disabled on most servers)

* Mon Sep 04 2023 Alex Kirhenshtein <alk@netxms.org> - 4.4.2-1
- Server checks interface speed during status poll and generates event if it changes
- Improved Cambium device driver
- Added driver for Hirschmann switches
- Implemented implicit import for constants in NXSL
- NXSL implicit import does not add non-referenced functions and constants from imported module
- Context action "Change expected interface state" implemented in new GUI client
- Context action "Clone network map" implemented in new GUI client
- Masked credentials in "Network Credentials" view
- Fixed bugs in TCP proxy session closure handling (server and agent side)
- Fixed bug in parsing XML content returned by web service
- Fixed template apply/remove in new GUI client
- Fixed server crash when network map uses physical link with non existing rack
- Fixed audit log writing on object move
- Fixed issues:
-   NX-2410 (Notification driver is locked during retry waiting period)
-   NX-2432 (Query interface speed when status poll detects that interface goes up)
-   NX-2441 (Auto-focus on Two-Factor input on WebUI)
-   NX-2442 (Maintenance predefined time)
-   NX-2449 (Unexpected SYS_DUPLICATE_IP_ADDRESS generation)
-   NX-2450 (microhttpd presence is not detected correctly)
-   NX-2451 (GetDCIValue() should return same data type as set in DCI properties)
-   NX-2452 (Agent on Windows returns only one software inventory record when multiple versions of same software are installed)

* Wed Jul 26 2023 Alex Kirhenshtein <alk@netxms.org> - 4.4.1-1
- Improved support for LLDP-V2-MIB
- Server can use both LLDP-MIB and LLDP-V2-MIB if supported by device
- Server saves SNMPv3 context engine ID alongside authoritative engine ID to avoid unnecessary engine ID discovery
- NXSL function GetDCIValues can be used to retrieve raw DCI values
- Added method "enableWinPerfCountersCache" to NXSL class "Node"
- Custom timeouts for external metric providers in agent
- Fixed incorrect display of line chart series with "Invert values" option
- Fixed database upgrade procedure (zone UIN update)
- Fixed memory leak in subagent "netsvc"
- Fixed bug in NXSL function FormatMetricPrefix
- Added workaround for "unexpected eof" OpenSSL error reported by web service calls to some servers
- Minor fixes in asset management
- Minor fixes and improvements in new management client application
- Fixed issues:
-   NX-2407 (Add the ability to duplicate server action in action manager)
-   NX-2414 (nxdbmgr should ignore data for deleted DCIs if there's record in dci_delete_list for that DCI)
-   NX-2415 (Legend text color is ignored in the nxmc console)
-   NX-2419 (When log file monitoring with wildcards is used, data right after file creation might be skipped)
-   NX-2428 (Cannot import configuration if threshold activation or deactivation event tags are missing or empty)
-   NX-2434 (Add option to set user, password as a parameters for IMAP and SMTP)
-   NX-2435 (0 is not shown on Y scale in graphs)

* Wed Jun 28 2023 Alex Kirhenshtein <alk@netxms.org> - 4.4.0-1
- "Trusted devices" in two-factor authentication
- Scrollable dashboards
- Native Modbus TCP support
- Arguments can be passed to script called via script macro
- Indirect function calls in NXSL
- Interface table in agents
- Linux agent can report interface aliases
- Improved dashboard elements "Pie Chart" and "Gauge"
- New macro {node-name} in DCI performance view configuration
- Added Query table columns for SNMP Table DCI
- Spanning Tree port state for interfaces collected at status poll
- System event for STP port state change
- Improved configuration import
- Fixed issues:
-   NX-457 (Support for multiple tile providers)
-   NX-696 (Condition status reset to UNKNOWN on change)
-   NX-875 (More info on per-node basis on polls for that node)
-   NX-935 (Scrollbar in Dashboards)
-   NX-1014 (Correct names of "Remove" menu items to "Remove from node" or "Remove from template")
-   NX-1232 (Tool for simplified SNMP tables configuration)
-   NX-1598 (Rename column "submap_id" in table "object_properties")
-   NX-1613 (Object state icon not shown in Template -> Remove)
-   NX-2067 (Add a hotkey to save policies. Ctrl+S)
-   NX-2244 (Have ability in the UI to jump to specific DCI from check)
-   NX-2294 (Add server setting to prefer IPv4 address when resolving node hostname)
-   NX-2295 (Use System.ActiveUserSessions agent list to display "User sessions" in management client)
-   NX-2317 (Add parameters to threshold activation events with additional information on triggered threshold)
-   NX-2357 (Create events for invalid object identifiers in EPP rules)
-   NX-2364 (Add option to request 2FA authorization less frequently)
-   NX-2370 (Use libedit for shell-style tools)
-   NX-2372 (Show DCI comments in Data Collection / Last Values view)
-   NX-2373 (Make DCI comments available in alarms generated from threshold violation events)
-   NX-2384 (Store and display event message in active threshold)
-   NX-2391 (Not possible to set correct zone for cluster)
-   NX-2392 (ARP table view for nodes)
-   NX-2397 (Cluster that is in another zone still belongs to the zone with Zone UIN=0)
-   NX-2420 (Add explicit option for log parser to follow symlinks)
-   NX-2422 (Keep separate session for each node in MIB explorer in new Management Client)
-   NX-2424 (Add information about user login failure (2FA issue, etc) to audit log)

* Fri May 26 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.7-1
- Fixed bug in reading topology information from LLDPv2 MIB
- Small fixes and improvements in new management client application
- Fixed issues:
-   NX-2253 (Actual repeat count should be passed to event in log file monitoring when reset repeat count is true)
-   NX-2418 (Log file monitoring does not work properly with symlinks)
-   NX-2421 (Invalid time format in log parser configuration can cause agent crash)

* Mon May 08 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.6-1
- Correctly handle FDB record type "secure"
- Improved driver for Cambium devices
- Fixed bug in handling /32 addresses during network discovery
- Fixed bug in flood notification processing in Telegram driver
- Fixed server crash caused by timeout during file transfer to agent
- Fixed bug in SNMP codepage handling
- Fixed bar gauge dashboard element drawing issue
- Small fixes and improvements in new management client application

* Fri Apr 21 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.5-1
- Fixed bug in X.509 certificate subject and issuer decoding
- Agent tunnel listener will not start if server certificate is not loaded
- Fixed WEB service configuration import with multiple headers
- Fixed login issues in new web UI
- Small fixes and improvements in new management client application
- Fixed issues:
-   NX-2272 (Session is not closed if user cancel 2FA auth initialization)
-   NX-2276 (Warn user when adding too wide mask to active discovery)
-   NX-2388 (Modify default templates - filesystem with type "ahafs" should be excluded from discovery)
-   NX-2404 (Integer division by zero in NXSL crashes server)
-   NX-2406 (Entering maintenance mode on cluster does not trigger maintenance mode on nodes within cluster)

* Thu Apr 06 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.4-1
- Fixed bug in ICMP ping implementation introduced in 4.3.3
- Added agent configuration option for setting file mode creation mask (umask)
- Bundled SQLite updated to version 3.41.2
- Multiple fixes and improvements in new management client application

* Wed Mar 29 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.3-1
- Improved database migration procedure when TimescaleDB is target (GitHub issue 83)
- Fixed bug in handling "verify-peer" option for network service metrics
- Fixed server crash when doing RADIUS authentication using MS-CHAP
- Fixed columns for 'Find switch port' search result
- Added additional information to debug message about event with incorrect source id
- Added ZoneUIN for Cluster's overview page
- Small fixes and adjustments to new management client
- Close DCI config view message not shown on DCI copy
- Dashboard element "Table Value" works in context dashboards
- Fixed issues:
-   NX-2387 (SQL errors when saving OSPF neighbor list)

* Thu Mar  2 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.2-1
- Fixed stacked line charts in new UI
- Fixed timeout inconsistencies in netsvc subagent
- Added web API calls for managing alarm comments
- More functionality migrated to new management client
- Fixed issues:
-   NX-677 (Dashboard editor: accelerators are duplicated in Line chart -> Data sources)
-   NX-2377 (Copy-paste of rules not working in EPP editor)
-   NX-2348 (Show active threshold event name in Last Values)
-   NX-2376 (Agent restart is not working correctly on RedHat based Linux OS)
-   NX-2379 (REST API to force poll DCI)
-   NX-2383 (Ignore systemd synthetic records when resolving node IP address to hostname)

* Fri Feb 10 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.1-2
- "Execute server command" object tool crash fixed

* Thu Feb 09 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.1-1
- Fixed database schema upgrade on Microsoft SQL Server
- Fixed issues with network service checks using netsvc subagent as a replacement for portcheck subagent
- Fixed bug in external table provider command execution
- Dashboard element "Availability Chart" is working again
- Mikrotik driver correctly handles server settings for using ifXTable and interface aliases
- Fixed VLAN configuration reading bug in Juniper driver
- Multiple fixes and improvements in new management client application
- Cosmetic fixes in Windows agent installer
- Fixed issues:
-   NX-808 (NXSL error message should include module name)
-   NX-2222 (Interface alias duplicated in UI if Objects.Interfaces.UseAliases set to "concatenate name with alias")
-   NX-2345 (Copy to Clipboard and Save as image... buttons no longer exist in WebUI in line chart window)
-   NX-2374 (Template auto unbind grace period handled incorrectly)

* Thu Feb 02 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.0-2
- Default agent's config fixed - SubAgents moved to correct section

* Thu Jan 26 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.0-1
- Upstream updated to 4.3.0
- Subagents ecs and portcheck are superseded by netsvc and removed

* Tue Dec 06 2022 Alex Kirhenshtein <alk@netxms.org> - 4.2.461-1
- Upstream updated to 4.2.461

* Fri Nov 18 2022 Alex Kirhenshtein <alk@netxms.org> - 4.2.433-1
- Upstream updated to 4.2.433

* Tue Oct 04 2022 Alex Kirhenshtein <alk@netxms.org> - 4.2.355-1
- Upstream updated to 4.2.355
