# vim: ts=3 sw=3 expandtab
Summary:       NetXMS umbrella package
Name:          netxms
Version:       4.3.5
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
BuildRequires: (java-17-openjdk-headless or java-11-openjdk-headless)
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

BuildRequires: jemalloc-devel = 5.3.0-1%{?dist}_netxms
BuildRequires: libosip2-devel = 5.3.0-1%{?dist}_netxms libexosip2-devel = 5.3.0-1%{?dist}_netxms

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
   --with-jemalloc \
   --with-asterisk

#sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
#sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

cp build/netxms-build-tag.properties src/java-common/netxms-base/src/main/resources/
mvn -f src/pom.xml versions:set -DnewVersion=$(grep NETXMS_VERSION= build/netxms-build-tag.properties | cut -d = -f 2) -DprocessAllModules=true
mvn -f src/client/nxmc/java/pom.xml versions:set -DnewVersion=$(grep NETXMS_VERSION= build/netxms-build-tag.properties | cut -d = -f 2)
mvn -f src/pom.xml install -Dmaven.test.skip=true -Dmaven.javadoc.skip=true

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
%{_libdir}/netxms/java/commons-codec-*.jar
%{_libdir}/netxms/java/commons-lang3-*.jar
%{_libdir}/netxms/java/netxms-base-*.jar
%{_libdir}/netxms/java/netxms-client-*.jar
%{_libdir}/netxms/java/netxms-java-bridge-*.jar
%{_libdir}/netxms/java/simple-xml-*.jar
%{_libdir}/netxms/java/slf4j-api-*.jar
%{_libdir}/netxms/java/stax-*.jar
%{_libdir}/netxms/java/xpp3-*.jar
%{_libdir}/netxms/java/logback-classic-*.jar
%{_libdir}/netxms/java/logback-core-*.jar


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
%{_libdir}/netxms/java/jython-standalone-2.7.2.jar
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
%{_libdir}/netxms/jira.hdlink
%{_libdir}/netxms/leef.nxm
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
%{_libdir}/netxms/ntcb.nxm
%{_libdir}/netxms/pdsdrv/*
%{_libdir}/netxms/redmine.hdlink
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
%{_libdir}/netxms/java/bcprov-jdk15on-*.jar
%{_libdir}/netxms/java/caffeine-*.jar
%{_libdir}/netxms/java/castor-core-*.jar
%{_libdir}/netxms/java/castor-xml-*.jar
%{_libdir}/netxms/java/checker-qual-*.jar
%{_libdir}/netxms/java/commons-beanutils-*.jar
%{_libdir}/netxms/java/commons-collections-*.jar
%{_libdir}/netxms/java/commons-collections4-*.jar
%{_libdir}/netxms/java/commons-compiler-*.jar
%{_libdir}/netxms/java/commons-daemon-*.jar
%{_libdir}/netxms/java/commons-digester-*.jar
%{_libdir}/netxms/java/commons-logging-*.jar
%{_libdir}/netxms/java/commons-math3-*.jar
%{_libdir}/netxms/java/ecj-*.jar
%{_libdir}/netxms/java/error_prone_annotations-*.jar
%{_libdir}/netxms/java/itext-*.js8.jar
%{_libdir}/netxms/java/jackson-annotations-*.jar
%{_libdir}/netxms/java/jackson-core-*.jar
%{_libdir}/netxms/java/jackson-databind-*.jar
%{_libdir}/netxms/java/janino-*.jar
%{_libdir}/netxms/java/jasperreports-*.jar
%{_libdir}/netxms/java/javax.inject-*.jar
%{_libdir}/netxms/java/jcl-over-slf4j-*.jar
%{_libdir}/netxms/java/jcommon-*.jar
%{_libdir}/netxms/java/jfreechart-*.jar
%{_libdir}/netxms/java/jna-*.jar
%{_libdir}/netxms/java/joda-time-*.jar
%{_libdir}/netxms/java/jpathwatch-*.jar
%{_libdir}/netxms/java/mail-*.jar
%{_libdir}/netxms/java/mariadb-java-client-*.jar
%{_libdir}/netxms/java/mssql-jdbc-*.jre8.jar
%{_libdir}/netxms/java/mysql-connector-j-*.jar
%{_libdir}/netxms/java/nxreportd-*.jar
%{_libdir}/netxms/java/ojdbc8-*.jar
%{_libdir}/netxms/java/poi-*.jar
%{_libdir}/netxms/java/postgresql-*.jar
%{_libdir}/netxms/java/protobuf-java-*.jar
%{_libdir}/netxms/java/waffle-jna-*.jar
%{_libdir}/netxms/java/xercesImpl-*.jar
%{_libdir}/netxms/java/xml-apis-*.jar
%{_unitdir}/netxms-reporting.service

%changelog
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

* Thu Feb 10 2023 Alex Kirhenshtein <alk@netxms.org> - 4.3.1-2
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
