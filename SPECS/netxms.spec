# vim: ts=3 sw=3 expandtab
Summary:       NetXMS umbrella package
Name:          netxms
Version:       5.2.5
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
BuildRequires: perl

BuildRequires: expat-devel
BuildRequires: jansson-devel
BuildRequires: (java-21-openjdk-devel or java-17-openjdk-devel or java-11-openjdk-devel)
BuildRequires: jq-devel
BuildRequires: libcurl-devel
BuildRequires: libmicrohttpd-devel
BuildRequires: libssh-devel
%if 0%{?rhel} != 10
BuildRequires: libstrophe-devel
%endif
BuildRequires: libvirt-devel
BuildRequires: lm_sensors-devel
BuildRequires: mosquitto-devel
BuildRequires: openldap-devel
BuildRequires: openssl-devel
%if 0%{?fedora} == 41
BuildRequires: openssl-devel-engine
%endif
BuildRequires: (pcre2-devel or pcre-devel)
BuildRequires: readline-devel
BuildRequires: systemd-devel
BuildRequires: zeromq-devel
BuildRequires: zlib-devel

BuildRequires: (oracle-instantclient-devel or oracle-instantclient19.10-devel)
BuildRequires: mariadb-connector-c-devel
BuildRequires: postgresql-devel
BuildRequires: sqlite-devel
BuildRequires: unixODBC-devel

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
   --with-asterisk

#sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
#sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

[ -e /usr/lib/jvm/java-11 ] && export JAVA_HOME=/usr/lib/jvm/java-11
[ -e /usr/lib/jvm/java-17 ] && export JAVA_HOME=/usr/lib/jvm/java-17

export MAVEN_OPTS="$MAVEN_OPTS -Dorg.slf4j.simpleLogger.log.org.apache.maven.cli.transfer.Slf4jMavenTransferListener=warn"

cp build/netxms-build-tag.properties src/java-common/netxms-base/src/main/resources/
mvn -B -f src/pom.xml versions:set -DnewVersion=$(grep NETXMS_VERSION= build/netxms-build-tag.properties | cut -d = -f 2) -DprocessAllModules=true
mvn -B -f src/client/nxmc/java/pom.xml versions:set -DnewVersion=$(grep NETXMS_VERSION= build/netxms-build-tag.properties | cut -d = -f 2)
mvn -B -f src/pom.xml install -Dmaven.test.skip=true -Dmaven.javadoc.skip=true

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
%exclude %{_libdir}/netxms/java/hamcrest-core-*.jar
%exclude %{_libdir}/netxms/java/junit-*.jar
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
%{_libdir}/libnxsde.so.*
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
%{_libdir}/netxms/java/commons-collections4-*.jar
%{_libdir}/netxms/java/commons-compiler-*.jar
%{_libdir}/netxms/java/commons-io-*.jar
%{_libdir}/netxms/java/commons-lang3-*.jar
%{_libdir}/netxms/java/commons-math3-*.jar
%{_libdir}/netxms/java/gson-*.jar
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
%{_libdir}/netxms/java/SparseBitSet-*.jar


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
%{_libdir}/netxms/java/jython-standalone-*.jar
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
%{_datadir}/netxms/mibs/*.mib
%{_datadir}/netxms/oui/*.csv
%{_datadir}/netxms/radius.dict
%{_datadir}/netxms/sql/*.sql
%{_datadir}/netxms/templates/*.xml
%{_libdir}/libethernetip.so.*
%{_libdir}/libnxcore.so.*
%{_libdir}/libnxdbmgr.so.*
%{_libdir}/libnxsl.so.*
%{_libdir}/libnxsrv.so.*
%{_libdir}/netxms/*.hdlink
%{_libdir}/netxms/*.nxm
# % {_libdir}/netxms/ncdrv/mqtt.ncd
%{_libdir}/netxms/ncdrv/anysms.ncd
%{_libdir}/netxms/ncdrv/dbtable.ncd
%{_libdir}/netxms/ncdrv/dummy.ncd
%{_libdir}/netxms/ncdrv/googlechat.ncd
%{_libdir}/netxms/ncdrv/gsm.ncd
%{_libdir}/netxms/ncdrv/kannel.ncd
%{_libdir}/netxms/ncdrv/mattermost.ncd
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
%if 0%{?rhel} != 10
%{_libdir}/netxms/ncdrv/xmpp.ncd
%endif
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
%{_libdir}/netxms/java/jcommon-*.jar
%{_libdir}/netxms/java/jfreechart-*.jar
%{_libdir}/netxms/java/mail-*.jar
%{_libdir}/netxms/java/mariadb-java-client-*.jar
%{_libdir}/netxms/java/mjson-*.jar
%{_libdir}/netxms/java/mssql-jdbc-*.jar
%{_libdir}/netxms/java/mysql-connector-j-*.jar
%{_libdir}/netxms/java/nxreportd-*.jar
%{_libdir}/netxms/java/ojdbc*-*.jar
%{_libdir}/netxms/java/openpdf-*.jar
%{_libdir}/netxms/java/postgresql-*.jar
%{_libdir}/netxms/java/protobuf-java-*.jar
%{_libdir}/netxms/java/stax2-api-*.jar
%{_libdir}/netxms/java/woodstox-core-*.jar
%{_libdir}/netxms/java/xercesImpl-*.jar
%{_libdir}/netxms/java/xml-apis-*.jar
%{_unitdir}/netxms-reporting.service

%changelog
* Mon Sep 01 2025 Alex Kirhenshtein <alk@netxms.org> - 5.2.5-1
  * Agent configuration file options can be passed from command line
  * New AIX agent metrics: System.Memory.Physical.Client, System.Memory.Physical.ClientPerc, System.Memory.Physical.Computational, System.Memory.Physical.ComputationalPerc
  * User ACL reports generated in XLSX format
  * Improved driver for Ubiquity AirMax devices
  * Running configuration logged after log rotation
  * Configurable maximum size for cached routing tables
  * New metric USB.ConnectedCount in WinNT subagent
  * Fixed incorrect object status calculation after restarting server with resolved alarms
  * Fixed bug in network map display in dashboard widget
  * Fixed bug in calculation of physical CPU usage on AIX
  * Fixed missing agent database table file\_integrity
  * Fixed issues:
  *   NX-2794 (Add more info to log message: Potential node x.x.x.x in zone x rejected (IP address is known as cluster resource address))
  *   NX-2819 (DCI data recalculation not working for TimescaleDB)
  *   NX-2822 (Alarms not appearing if nxmc has reconnected)
  *   NX-2825 (Tables missing PK, this breaks master-master replication (at least in Postgres))

* Thu Jul 10 2025 Alex Kirhenshtein <alk@netxms.org> - 5.2.4-1
  * System event is generated when responsible user for object added or removed
  * Support for custom OUI database entries
  * Fixed bug in loading NXSL "stdlib" script
  * Add BOM sequence skip for structured data extractors (including web service extractor)
  * Network map fixes: refresh while drag, jumping labels on links and not saved object location after 'align to grid' action
  * NXSL function JsonParse sets global variables $jsonErrorMessage, $jsonErrorLine, and $jsonErrorColumn after parsing error
  * NXSL function JsonParse accepts optional second argument to control interpretation of integers as floating point numbers
  * Configurable data collection scheduling mode that requires connectivity before scheduling DCI for collection
  * Fixed issues:
  *   NX-2737 (Switch from obsolete SQLite shared cache mode to WAL mode)
  *   NX-2783 (Network discovery view shows "Invalid thread access" error on web)
  *   NX-2788 (Changing Objects.Nodes.SyncNamesWithDNS requires server restart, while it should not)
  *   NX-2790 (Interface Overview view should have node name when interface is under a circuit)
  *   NX-2795 (Selection on map is frequently lost)
  *   NX-2797 (Hide passwords in server configuration variables view)
  *   NX-2802 (Show units for server configuration variables)
  *   NX-2806 (Data collection scheduling mode that requires connectivity before scheduling DCI for collection)
  *   NX-2807 (EPP export does not escape < and > in XML attributes)

* Thu Jun 05 2025 Alex Kirhenshtein <alk@netxms.org> - 5.2.3-1
- Default timeout for service checks via netsvc subagent set to 1 second
- Fixed alarm severity text for Grafana API
- Forced plain text web service requests are cached separately
- Fixed issues:
-   NX-2766 (Template macros are not expanded in instance data filed in DCIs Instance discovery)
-   NX-2768 (Changes to VNC properties not logged to audit log)
-   NX-2770 (Object query result view pinning does not work)
-   NX-2777 (No favicon in new Web UI)
-   NX-2781 (Send all parameters of default email notification channel to reporting server)
-   #140 (SQL errors after converting database to TimescaleDB)

* Mon May 19 2025 Alex Kirhenshtein <alk@netxms.org> - 5.2.2-1
- Fixed insert into table "notification_log" for TimescaleDB
- Improved client performance, by disabling alarm refresh if tab is not active
- Fixed missing DCI on network map links when new DCI's are added on alreay opened map
- Added job progress indication within views
- Fixed issues:
-   NX-2733 (Do not show zone column in discovery targets if zoning is off)
-   NX-2742 (Add NXSL node object method for enabling/disabling SM-CLP polling)
-   NX-2751 (Delete scheduled tasks on node deletion)
-   NX-2752 (Add ICMP response time jitter internal DCI for ICMP response statistic collection)
-   NX-2754 (Separate error code for situation when TCP proxy is not enabled in agent config)
-   NX-2755 (NXSL Interface utilization values returned as int, without decimal point)
-   NX-2764 (Add PostgreSQL 17 support in monitoring subagent (pgi_stat_checkpointer))
-   NX-2765 (Increase command length in package manager)

* Thu Apr 08 2025 Alex Kirhenshtein <alk@netxms.org> - 5.2.1-1
- NXSL function PostEvent accepts any event source object
- Added option to set in maintenance all objects under Wireless Domain
- InfluxDB and Clickhouse drivers can be configured to use custom attributes of DCI's template
- Fixed bug in driver for Cambium CnPilot devices
- Fixed database connection leak during package deployment
- Fixed issues:
-   NX-2600 (Threshold for missing table instances never deactivated)
-   NX-2723 (Add Web API endpoint for object maintenance)
-   NX-2729 (Display hints for hook scripts in script library)
-   NX-2734 (When exporting event processing policy rule, automatically add referenced actions)
-   NX-2735 (Cannot delete user from object access control list)
-   NX-2740 (Modbus DCI becomes unsupported when proxy is unreachable)

* Thu Mar 27 2025 Alex Kirhenshtein <alk@netxms.org> - 5.2.0-1
- User-defined tags on data collection items
- Network maps can be shown in object's context in a same way as dashboards
- Improved package deployment
- NXSL math functions Min, Max, Average, MeanAbsoluteDeviation, and StandardDeviation accepts variadic arguments
- New NXSL function Math::Sum
- New NXSL array method indexOf
- Simplified loops over numeric ranges in NXSL using class "Range"
- Unicode escape sequences in NXSL string literals
- Script entry point can be given for script DCI
- Dot can be used as script entry point separator instead of slash
- Fan-out diver for ClickHouse
- Fixed direction and arrow size for Network Map links
- Reworked Network Map link label location calculation for multi link connection
- Configurable values for RADIUS authentication request attributes Service-Type and NAS-Identifier
- SM-CLP protocol support reworked and switched to SSH as a transport
- Fixed incorrect data and occasional server crashes in network discovery filter script
- Fixed issues:
-   NX-74 (New node options - "expected capabilities")
-   NX-1301 (Automatic traffic DCI linking to interface)
-   NX-2654 (Add agent running config object tool via db migration script)
-   NX-1302 ("Traffic" overlay for maps)
-   NX-2568 (Add case-insensitive versions of threshold operations "like" and "not like")
-   NX-2624 (Review SMCLP data source and switch it to SSH)
-   NX-2662 (Show map in tab on object)
-   NX-2667 (Context dashboard should be able to pick DCIs from child objects by specific DCI tag)
-   NX-2668 (Change all server configuration variables related to polling intervals to be modifiable without server restart)
-   NX-2680 (Add NXSL function Math::Sum)
-   NX-2681 (Add array method "indexOf")
-   NX-2686 (Put DCI to ERROR state if it's transformation script has compilation error)
-   NX-2689 (Add event ID (if available) to notification log)
-   NX-2694 (Add "front side only" property to rack objects)
-   NX-2695 (Fit rack image into the view both vertically and horizontally)
-   NX-2703 (Support Unicode escape sequences in NXSL string literals)
-   NX-2707 (Add method "createSensor" to container object classes in NXSL)
-   NX-2716 (Agent metric that reports server's access level to that agent)
-   NX-2721 (Add $ipAddress variable of class InetAddress in Hook::AcceptNewNode script)
-   NX-2725 (NetXMS does not fallback to secondary proxy nodes)
-   NX-2728 (Update interface configuration when a node with an agent is rebooted)
-   NX-2732 (Server attempts TCP ping for nodes behind proxy)

* Wed Mar 26 2025 Alex Kirhenshtein <alk@netxms.org> - 5.1.5-1
- VNC detection during configuration poll can be disabled
- System access rights included into user ACL report
- Fixed bugs in NXSL script conversion to V5 format
- Fixed file handle leak in SSH subagent
- Fixed bug in configuration export
- Fixed issues:
-   NX-2712 (Scripted thresholds triggers activation event repeatedly)
-   NX-2714 (Status of interface not propagated to circuit)
-   NX-2726 (Web API call causes server crash)

* Mon Mar 03 2025 Alex Kirhenshtein <alk@netxms.org> - 5.1.4-1
- Agent uses Windows Installer API instead of launching msiexec.exe for installing .msi and .msp packages
- New Windows agent metric System.IsRestartPending
- Improved server performance when launching multiple external actions
- MIB Explorer added to "Tools" perspective
- Fixed incorrect parsing of 32 bit agent installer names when adding package to package manager
- Changed IPv4 address parser - now it only accepts canonical form (4 decimal numbers separated by dots)
- Correct handling of network mask /31 on peer-to-peer interfaces
- Node sub objects like Interface will not be shown on Infrastructure perspective if they do not have parent shown in the same tree
- Added dBm and rpm DCI units to no multipliers list
- Fixed tab priority for multiple built in views
- Fixed problem when newly added DCI were not shown on Network Map (links, DCI containers)
- Fixed broken autobind during node configuration poll
- Fixed issues:
-   NX-2645 (Remember perspective splitter position)
-   NX-2684 (Remove hardcoded license id from the nxlicmgr)
-   NX-2690 (Migration from Timescale to regular Postgres fails on win\_event\_log table)
-   NX-2696 (View options in Data Collection does not show actual state of Use Multipliers checkbox)
-   NX-2699 (Show value of os.name in nxmc's About dialog)
-   NX-2701 (Automatic DB unlock fails because GetLocalIpAddr() may return different address)
-   NX-2705 (NXSL split string with trim option)
-   NX-2711 (scheduled_tasks column is out of range for type integer)

* Mon Dec 16 2024 Alex Kirhenshtein <alk@netxms.org> - 5.1.3-1
- Fixed critical bug in SNMP trap receiver
- Server checks for other possible SNMP credentials during configuration poll if node marked as SNMP unreachable
- Image attributes in Markdown viewer
- Fixed bug in counter reset detection
- Fixed issues:
-   NX-2685 (nxshell asks for password while using properties file)

* Mon Dec 16 2024 Alex Kirhenshtein <alk@netxms.org> - 5.1.2-1
- Server performance and memory usage optimization when polling multiple SNMP devices
- Limit routing table scans during SNMP device configuration poll
- Optimized memory usage in InfluxDB driver
- Server startup time improved
- Added server configuration option "Client.MinVersion"
- Improved Markdown viewer
- InfluxDB driver options for validation and correction of DCI values being sent
- Fixed issues:
-   NX-2635 (Predefined graphs perspective not working in web UI)
-   NX-2640 (Add more detailed stats on pollers to debug console)
-   NX-2647 (On node deletion interfaces under circuit objects are not deleted)
-   NX-2649 (Issues with "move to another container" context menu on interfaces)
-   NX-2650 (Add new hotkey in "execute server script" for "clear output+run script")
-   NX-2653 (Can not pin Data Collection tab which is in edit mode)
-   NX-2657 (IllegalStateException in nxmc log)
-   NX-2660 (Add method to read little-endian 4 byte float value from ByteStream)
-   NX-2661 (Issues with loading image of DCI image element of map)
-   NX-2669 (Add internal table with node's interfaces)
-   NX-2672 (Kiosk mode issues)
-   NX-2673 (Table DCI column querying not working, if metric has no leading dot)
-   NX-2675 (Add NXSL methods to handle markdown comments correctly)
-   NX-2676 (Issues with comment tab creation and modification on object)

* Wed Nov 20 2024 Alex Kirhenshtein <alk@netxms.org> - 5.1.1-1
- Improved server performance
- Improved wireless controller bridge for HFCL
- MS SQL database driver no longer requires SQL Server Native Client (can use SQL Server ODBC driver v13, v17, or v18 instead)
- Added driver for Huawei LAN switches
- Updated driver for Dell switches
- Updated driver for Qtech switches
- Added internal metrics Server.ObjectCount.AccessPoints and Server.ObjectCount.Interfaces
- New NXSL functions Math::Average, Math::MeanAbsoluteDeviation, and Math::StandardDeviation
- nxdbmgr can do in-place conversion from standard PostgreSQL schema to TimescaleDB
- Fixed server crash on receiving SNMP trap
- Fixed bug in database initialization script
- Fixed task scheduler performance issues
- Removed "Delete" button form object upper bar
- Fixed issues:
-   NX-2629 (Can not clone an object tool)
-   NX-2630 (Not all the Markdowns are functioning)
-   NX-2631 (In-place migration from standard PostgreSQL to TimescaleDB)
-   NX-2632 (Inconsistency in asset management schema enum field definition)
-   NX-2633 (Text not fully displayed in button)
-   NX-2637 (Circuit class functionality)
-   NX-2639 (Incorrect log message for Mattermost driver)
-   NX-2642 (Add alarm_state_changes and certificate_action_log tables to nxdbmgr -Z all)

* Sat Nov 02 2024 Alex Kirhenshtein <alk@netxms.org> - 5.1.0-1
-  New automatic map type "hybrid topology"
-  New object class "Circuit"
-  Only read access is needed for dashboard context object for scripting dashboard elements
-  Reading of FDB moved to network device drivers to allow better handling of devices not following standards
-  Peer information on interfaces can be set and cleared manually
-  Added down since nxsl parameter to access point
-  Vlans view merged in to the Ports view
-  Added option to show physical links on L2 ad-hoc map
-  L2 predefined map will not cache results, only ad-hock map results are cached
-  More accurate ad-hoc IP topology maps
-  Unreachable node will be tested for all protocols in each configuration poll
-  Use inetCidrRouteTable, ipCidrRouteTable, and ipForwardTable in addition to ipRouteTable to get routing information via SNMP
-  EtherNet/IP added as DCI data source
-  Improved web UI login pages
-  Separate "Comments" view for objects
-  Templates perspective can be configured to show nodes under assigned templates
-  New attributes in NXSL class "InetAddress" ("isSubnetBase", "isSubnetBroadcast", "subnet")
-  New NXSL function "CalculateDowntime"
-  New method "calculateDowntime" in NXSL class "NetObj"
-  Other UI usability improvements
-  Fixed session agent compatibility issues on Windows 11
-  Optional DCI event "all thresholds deactivated"
-  DCI data type after transformation can be configured separately from input data type
-  New scheduled task handler Agent.ExecuteCommand
-  Improved network map multi link spacing
-  New action System.TerminateUserSession in Windows agent
-  Fixed network map object lable sacling zoom in/zoom out
-  Fixed issues:
-    NX-253 (Configurable label for Y axis on line charts)
-    NX-834 (DCI Table scroll position in dashboard is reset during refresh)
-    NX-968 (Remove Peer from unmanaged interface)
-    NX-1118 (Add "hide link labels" option for network map dashboard elements)
-    NX-1200 (New object group - Circuits)
-    NX-1288 (Fix selection colors in syslog monitor)
-    NX-1414 (Support for ipCidrRouteTable)
-    NX-1465 (When MIB browser opened, unfold tree and select longest match of device's SNMP object ID)
-    NX-1617 (Show comments window only if comment present)
-    NX-1958 (Support custom font for Label in Dashboard)
-    NX-1973 (Add ability to manually specify a peer for an interface)
-    NX-2034 (Use RENAME COLUMN on SQLite newer than 3.25.0)
-    NX-2353 (Add hotkey to start search in "Search IP address" view)
-    NX-2371 (Separate data types for raw and transformed DCI values)
-    NX-2439 (Implement agent table System.InstalledProducts for ArchLinux)
-    NX-2458 (Add option to nest context dashboard in dashboard)
-    NX-2461 (Smart algorithm for processing counter32/64 roll-over)
-    NX-2488 (Use caching when using web service requests in NXSL)
-    NX-2512 (Not able to import columns for table DCI with origin=script)
-    NX-2517 (Linux agent can crash if some CPUs are disabled)
-    NX-2528 (Markdown Support in Object Comment Sections)
-    NX-2531 (Ability to disable server actions in EPP)
-    NX-2533 (NXSL global variable that contains object tool input field values)
-    NX-2535 (Replace drop down with radio buttons in EPP rule Downtime Control)
-    NX-2538 (Add ability to use IPv4 style netmask in network discovery target properties)
-    NX-2540 (Add $map object for use in map filter script)
-    NX-2541 (All EPP actions should be executed asynchronously)
-    NX-2542 (Add syslog metadata to generated events)
-    NX-2544 (New agent metrics for counting online and offline CPUs)
-    NX-2545 (Exporting a template with big file in a policy causes nxmc to close)
-    NX-2552 (Exception in desktop UI)
-    NX-2562 (Add pollingScheduleType attribute to DCI object)
-    NX-2566 (List of packages is not read correctly on linux systems where alien is installed)
-    NX-2574 (nxevent and nxaevent utilities do not support named event parameters)
-    NX-2580 (Configurable default time range for ad-hoc line charts)
-    NX-2584 (Change network map edit mode to network map lock mode)
-    NX-2586 (Export all to CSV not working in data collection configuration view)
-    NX-2593 (Add option to use properties file for NXShell)
-    NX-2596 (Unable to create zone via Web API)
-    NX-2597 (Log PATH and LD_LIBRARY_PATH values on agent startup)
-    NX-2598 (Generate event when all thresholds of a DCI are rearmed)
-    NX-2602 (Audit log not available in context menu for some objects)
-    NX-2606 (no id ranges possible in Configuration->Windows event log parser)
-    NX-2613 (Show gray "Any" in "source objects" list, if it's empty)
-    NX-2617 (Show info in EPP rule that "Accept correlated events" is checked)
-    NX-2618 (Server crash when file upload task configuration is invalid)
-    NX-2619 (SQL insert into nodes failed)
-    NX-2620 (System.ProcessList truncates the full process name or path)
-    NX-2621 (Add "Line chart" item in context menu of map link)

* Thu Sep 05 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.8-1
-  Fixed error in web console on package deployment
-  Implemented refresh for Event Processing Policy view
-  Fixed Arp Cache view refresh when data is not available
-  Implemented find mac in Web APIs
-  NXSL function "trace" handles objects and arrays in a same way as "print"
-  New methods "print" and "trace" in NXSL class "Table"
-  Added workaround for incorrect LLDP information returned by Alpha Bridge switches
-  Fixed bug in network map link styling script processing
-  Fixed issues:
-    NX-1311 (Table DCIs ignoring table configuration)
-    NX-2567 (ExternalMetricProvider does not work on Windows)
-    NX-2570 (Use monotonic clock instead of system time for calculating agent uptime)
-    NX-2572 (Problem creating PostgreSQL database during installation on Windows)

* Thu Aug 15 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.7-1
- Server configuration option to enable agent tunnel binding using only tunnel's source IP address
- Fixed incorrect Windows Remote Desktop session color depth reported by agent
- Fixed buffer overflow for IPv6 IP addresses print in log
- Fixed top level object display issues in "Infrastructure" perspective
- Fixed issues:
-   NX-387 (Tool to read current (loaded) agent config)
-   NX-937 (Copy DCI value from object overview)
-   NX-2206 ("Package Deployment Monitor" should be resorted when status of any deployment changes)
-   NX-2549 (Exception in AlarmNotifier)
-   NX-2551 (Desktop UI show same warning in alarm viewer multiple times)
-   NX-2553 (New agent action - show running configuration)
-   NX-2557 (Exception in WebUI)
-   NX-2559 (Line colors and time frame not saved when double-clicking graphs in Performance tab)
-   NX-2561 (Object query hangs on script errors)

* Mon Aug 05 2024 Alex Kirhenshtein <alk@netxms.org> - 5.0.6-2
- libjq added to dependencies

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
