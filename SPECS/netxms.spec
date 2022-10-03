# vim: ts=3 sw=3 expandtab
Summary:        NetXMS meta package
Name:           netxms
Version:        4.2.355
Release:        1%{?dist}
License:        GPL
URL:            https://netxms.org
Group:          Admin
Source0:        %{name}-%{version}.tar.gz
Source1:        netxms-server.service
Source2:        netxms-agent.service
Source3:        netxms-reporting.service

BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: maven
BuildRequires: chrpath

BuildRequires: expat-devel
BuildRequires: jansson-devel
BuildRequires: java-latest-openjdk-headless
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

BuildRequires: jemalloc-devel = 5.3.0-%{release}_netxms
BuildRequires: libosip2-devel = 5.3.0-%{release}_netxms libexosip2-devel = 5.3.0-%{release}_netxms

%description

%prep
%setup -q

%build
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
   --with-mariadb-compat-headers \
   --with-zeromq \
   --with-oracle \
   --with-jemalloc \
   --with-asterisk

./build/build_java_components.sh -skip-nxmc-build -no-revert-version

#sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
#sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}

%install
rm -rf %{buildroot}

%make_install

install -m755 -d %{buildroot}%{_unitdir}
install -m644 %{SOURCE1} %{buildroot}%{_unitdir}/netxms-server.service
install -m644 %{SOURCE2} %{buildroot}%{_unitdir}/netxms-agent.service
install -m644 %{SOURCE3} %{buildroot}%{_unitdir}/netxms-reporting.service

rm -f %{buildroot}%{_libdir}/*.la

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
%exclude %{_includedir}/netxms-build-tag.h
%exclude %{_libdir}/*.la
%exclude %{_libdir}/*.so
%exclude %{_libdir}/*.so
%exclude %{_libdir}/netxms/spe.nxm
%exclude %{_datadir}/netxms/lsan-suppressions.txt

%doc

### netxms-base
%package base
Summary: xxx

%description base
...

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
Summary: xxx
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(post): systemd

%description agent
...

%post agent
%systemd_post netxms-agent.service

%preun agent
%systemd_preun netxms-agent.service

%postun agent
%systemd_postun netxms-agent.service

%files agent
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
%{_libdir}/netxms/ecs.nsm
%{_libdir}/netxms/filemgr.nsm
%{_libdir}/netxms/gps.nsm
%{_libdir}/netxms/linux.nsm
%{_libdir}/netxms/lmsensors.nsm
%{_libdir}/netxms/logwatch.nsm
%{_libdir}/netxms/netsvc.nsm
%{_libdir}/netxms/ping.nsm
%{_libdir}/netxms/portcheck.nsm
%{_libdir}/netxms/sms.nsm
%{_libdir}/netxms/ssh.nsm
%{_libdir}/netxms/ups.nsm
%{_unitdir}/netxms-agent.service


### netxms-agent-asterisk
%package agent-asterisk
Summary: xxx

%description agent-asterisk
...

%files agent-asterisk
%{_libdir}/netxms/asterisk.nsm    


### netxms-java-base
%package java-base
Summary: xxx

%description java-base
...

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
Summary: xxx

%description agent-java
...

%files agent-java
%{_libdir}/netxms/java.nsm
%{_libdir}/netxms/java/jmx.jar
%{_libdir}/netxms/java/netxms-agent-*.jar
%{_libdir}/netxms/java/ubntlw.jar
%{_libdir}/netxms/java/opcua.jar


### netxms-agent-mysql
#%package agent-mysql
#Summary: xxx
#
#%description agent-mysql
#...
#
#%files agent-mysql
#%XXX{_libdir}/netxms/mysql.nsm


### netxms-agent-oracle
%package agent-oracle
Summary: xxx

%description agent-oracle
...

%files agent-oracle
%{_libdir}/netxms/oracle.nsm


### netxms-agent-pgsql
%package agent-pgsql
Summary: xxx

%description agent-pgsql
...

%files agent-pgsql
%{_libdir}/netxms/pgsql.nsm


### netxms-agent-mqtt
%package agent-mqtt
Summary: xxx

%description agent-mqtt
...

%files agent-mqtt
%{_libdir}/netxms/mqtt.nsm


### netxms-agent-vmgr
%package agent-vmgr
Summary: xxx

%description agent-vmgr
...

%files agent-vmgr
%{_libdir}/netxms/vmgr.nsm


### netxms-client
%package client
Summary: xxx

%description client
...

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
Summary: xxx
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(post): systemd

%description server
...

%post server
%systemd_post netxms-server.service

%preun server
%systemd_preun netxms-server.service

%postun server
%systemd_postun netxms-server.service

%files server
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
%{_libdir}/libethernetip.so.*
%{_libdir}/libnxcore.so.*
%{_libdir}/libnxdbmgr.so.*
%{_libdir}/libnxsl.so.*
%{_libdir}/libnxsrv.so.*
%{_libdir}/libstrophe.so.*
%{_libdir}/netxms/jira.hdlink
%{_libdir}/netxms/ncdrv/*
%{_libdir}/netxms/ndd/*
%{_libdir}/netxms/ntcb.nxm
%{_libdir}/netxms/pdsdrv/*
%{_libdir}/netxms/redmine.hdlink
%{_sharedstatedir}/netxms/*
%{_unitdir}/netxms-server.service


### netxms-dbdrv-sqlite3
%package dbdrv-sqlite3
Summary: xxx

%description dbdrv-sqlite3
...

%files dbdrv-sqlite3
%{_libdir}/netxms/dbdrv/sqlite.ddr


### netxms-dbdrv-pgsql
%package dbdrv-pgsql
Summary: xxx

%description dbdrv-pgsql
...

%files dbdrv-pgsql
%{_libdir}/netxms/dbdrv/pgsql.ddr


### netxms-dbdrv-mariadb
#%package dbdrv-mariadb
#Summary: xxx
#
#%description dbdrv-mariadb
#...
#
#%files dbdrv-mariadb
#%XXX{_libdir}/netxms/dbdrv/mariadb.ddr


### netxms-dbdrv-odbc
%package dbdrv-odbc
Summary: xxx

%description dbdrv-odbc
...

%files dbdrv-odbc
%{_libdir}/netxms/dbdrv/odbc.ddr


### netxms-dbdrv-oracle
%package dbdrv-oracle
Summary: xxx

%description dbdrv-oracle
...

%files dbdrv-oracle
%{_libdir}/netxms/dbdrv/oracle.ddr


### netxms-reporting
%package reporting
Summary: xxx
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(post): systemd

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
%{_libdir}/netxms/leef.nxm
%{_libdir}/netxms/java/activation-*.jar
%{_libdir}/netxms/java/bcprov-jdk15on-*.jar
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
%{_libdir}/netxms/java/itext-*.js8.jar
%{_libdir}/netxms/java/jackson-annotations-*.jar
%{_libdir}/netxms/java/jackson-core-*.jar
%{_libdir}/netxms/java/jackson-databind-*.jar
%{_libdir}/netxms/java/janino-*.jar
%{_libdir}/netxms/java/jasperreports-*.jar
%{_libdir}/netxms/java/javax.inject-*.jar
%{_libdir}/netxms/java/jcommon-*.jar
%{_libdir}/netxms/java/jfreechart-*.jar
%{_libdir}/netxms/java/joda-time-*.jar
%{_libdir}/netxms/java/jpathwatch-*.jar
%{_libdir}/netxms/java/mail-*.jar
%{_libdir}/netxms/java/mariadb-java-client-*.jar
%{_libdir}/netxms/java/mssql-jdbc-*.jre8.jar
%{_libdir}/netxms/java/mysql-connector-java-*.jar
%{_libdir}/netxms/java/nxreportd-*.jar
%{_libdir}/netxms/java/ojdbc8-*.jar
%{_libdir}/netxms/java/ons-*.jar
%{_libdir}/netxms/java/oraclepki-*.jar
%{_libdir}/netxms/java/osdt_cert-*.jar
%{_libdir}/netxms/java/osdt_core-*.jar
%{_libdir}/netxms/java/poi-*.jar
%{_libdir}/netxms/java/postgresql-*.jar
%{_libdir}/netxms/java/protobuf-java-*.jar
%{_libdir}/netxms/java/simplefan-*.jar
%{_libdir}/netxms/java/ucp-*.jar
%{_libdir}/netxms/java/xercesImpl-*.jar
%{_libdir}/netxms/java/xml-apis-*.jar
%{_unitdir}/netxms-reporting.service
%{_datadir}/netxms/mibs/*.txt
%{_datadir}/netxms/oui/*.csv
%{_datadir}/netxms/sql/*.sql
%{_datadir}/netxms/templates/*.xml
%{_datadir}/netxms/radius.dict

%changelog
* Mon Oct 3 2022 Alex Kirhenshtein <alk@netxms.org>
- Upstream updated to 4.2.355
