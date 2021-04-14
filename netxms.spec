Summary:        NetXMS meta package
Name:           netxms
Version:        2.2.15.2
#Epoch:          2
Release:        1%{?dist}
License:        GPL
URL:            https://netxms.org
Group:          Admin
Source:        %{name}-%{version}.tar.gz

BuildRequires:	gcc-c++ expat-devel jansson-devel libcurl-devel libssh-devel
BuildRequires:	libvirt-devel lm_sensors-devel mosquitto-devel openldap-devel openssl-devel
BuildRequires:	readline-devel systemd-devel xen-devel zeromq-devel zlib-devel
BuildRequires:	postgresql-devel sqlite-devel unixODBC-devel

%if 0%{?suse_version} >= 1210
BuildRequires: systemd-rpm-macros

%{?systemd_requires}
%endif

%description

#%%define _unpackaged_files_terminate_build 0

%prep
%setup -q

%build
%configure --with-server --with-agent --with-client --with-sqlite --with-pgsql --with-odbc --enable-unicode --with-vmgr --with-zeromq --with-xen

%make

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d %{buildroot}%{_unitdir}
install -m 644 -D contrib/startup/systemd/nxagentd.service %{buildroot}%{_unitdir}
install -m 644 -D contrib/startup/systemd/netxmsd.service %{buildroot}%{_unitdir}

%make_install

%files
%exclude %{_bindir}/nxdevcfg
%exclude %{_libdir}/*.la
%exclude %{_libdir}/libappagent.so
%exclude %{_libdir}/libnetxms.so
%exclude %{_libdir}/libnsm_dbquery.so
%exclude %{_libdir}/libnsm_devemu.so
%exclude %{_libdir}/libnsm_ds18x20.so
%exclude %{_libdir}/libnsm_ecs.so
%exclude %{_libdir}/libnsm_filemgr.so
%exclude %{_libdir}/libnsm_gps.so
%exclude %{_libdir}/libnsm_linux.so
%exclude %{_libdir}/libnsm_lmsensors.so
%exclude %{_libdir}/libnsm_logwatch.so
%exclude %{_libdir}/libnsm_mqtt.so
%exclude %{_libdir}/libnsm_netsvc.so
%exclude %{_libdir}/libnsm_ping.so
%exclude %{_libdir}/libnsm_portcheck.so
%exclude %{_libdir}/libnsm_sms.so
%exclude %{_libdir}/libnsm_ssh.so
%exclude %{_libdir}/libnsm_ups.so
%exclude %{_libdir}/libnsm_vmgr.so
%exclude %{_libdir}/libnsm_xen.so
%exclude %{_libdir}/libnxagent.so
%exclude %{_libdir}/libnxappc.a
%exclude %{_libdir}/libnxcc.*
%exclude %{_libdir}/libnxclient.so
%exclude %{_libdir}/libnxdb.so
%exclude %{_libdir}/libnxddr_odbc.so
%exclude %{_libdir}/libnxddr_pgsql.so
%exclude %{_libdir}/libnxddr_sqlite.so
%exclude %{_libdir}/libnxlp.so
%exclude %{_libdir}/libnxsnmp.so
%exclude %{_libdir}/libnxtre.so

%doc

### netxms-agent-mqtt
%package agent-mqtt
Summary: NetXMS subagent for MQTT
Requires: netxms-agent = %{version} mosquitto

%description agent-mqtt

%files agent-mqtt
%{_libdir}/netxms/mqtt.nsm    

### netxms-agent-vmgr
%package agent-vmgr
Summary: NetXMS subagent for monitoring hypervisors
Requires: netxms-agent = %{version} libvirt-libs

%description agent-vmgr

%files agent-vmgr
%{_libdir}/netxms/vmgr.nsm    

### netxms-agent-xen
%package agent-xen
Summary: NetXMS subagent for monitoring XEN
Requires: netxms-agent = %{version} xen-libs

%description agent-xen

%files agent-xen
%{_libdir}/netxms/xen.nsm     

### netxms-agent
%package agent
Summary: NetXMS Agent
Requires: netxms-base = %{version} netxms-dbdrv-sqlite3 = %{version}

%description agent
 
%pre agent
%if 0%{?suse_version}
%service_add_pre nxagentd.service
%endif

%post agent
%service_add_post nxagentd.service

%preun agent
%service_del_preun nxagentd.service

%postun agent
%service_del_postun nxagentd.service

%files agent
%{_bindir}/nxagentd             
%{_bindir}/nxappget
%{_bindir}/nxapush
%{_bindir}/nxlptest
%{_libdir}/libappagent.so.*
%{_libdir}/libnxagent.so.*
%{_libdir}/libnxlp.so.*
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
%{_unitdir}/nxagentd.service

### netxms-base
%package base
Summary: base

%description base

%files base
%{_bindir}/nxcsum          
%{_bindir}/nxencpasswd          
%{_bindir}/nxgenguid
%{_libdir}/libnetxms.so.*
%{_libdir}/libnxclient.so.*
%{_libdir}/libnxdb.so.*
%{_libdir}/libnxsnmp.so.*  
%{_libdir}/libnxtre.so.*  

### netxms-client
%package client
Summary: client
Requires: netxms-base = %{version}

%description client

%files client
%{_bindir}/nxpush
%{_bindir}/nxevent
%{_bindir}/nxalarm
%{_bindir}/nxsms

### netxms-dbdrv-odbc
%package dbdrv-odbc
Summary: odbc
Provides: netxms-dbdrv
Requires: netxms-base = %{version} unixODBC

%description dbdrv-odbc

%files dbdrv-odbc
%{_libdir}/netxms/dbdrv/odbc.ddr   

### netxms-dbdrv-pgsql
%package dbdrv-pgsql
Summary: pgsql
Requires: netxms-base = %{version} postgresql-libs
Provides: netxms-dbdrv
#Suggests: postgresql

%description dbdrv-pgsql

%files dbdrv-pgsql
%{_libdir}/netxms/dbdrv/pgsql.ddr

### netxms-dbdrv-sqlite3
%package dbdrv-sqlite3
Summary: sqlite
Requires: netxms-base = %{version} sqlite

%description dbdrv-sqlite3

%files dbdrv-sqlite3
%{_libdir}/netxms/dbdrv/sqlite.ddr 

### netxms-server
%package server
Summary: server
Requires: netxms-base = %{version} netxms-dbdrv
#Suggests: netxmsd-dbdrv-pgsql

%description server

%pre server
%service_add_pre netxmsd.service

%post server
%service_add_post netxmsd.service

%preun server
%service_del_preun netxmsd.service

%postun server
%service_del_postun netxmsd.service

%files server
%{_bindir}/netxmsd                   
%{_bindir}/nxaction
%{_bindir}/nxadm
%{_bindir}/nxap
%{_bindir}/nx-collect-server-diag
%{_bindir}/nxdbmgr
%{_bindir}/nxdownload
%{_bindir}/nxget
%{_bindir}/nxmibc
%{_bindir}/nxminfo
%{_bindir}/nxscript
%{_bindir}/nxsnmp*
%{_bindir}/nxupload
%{_datadir}/netxms/*
%{_libdir}/libnxcore.so*
%{_libdir}/libnxdbmgr*.so*
%{_libdir}/libnxsl.so*
%{_libdir}/libnxsms_*.so*
%{_libdir}/libnxsrv.so*
%{_libdir}/libstrophe.so*
%{_libdir}/netxms/jira.hdlink
%{_libdir}/netxms/ndd/*
%{_libdir}/netxms/redmine.hdlink
%{_libdir}/netxms/smsdrv/*
%{_sharedstatedir}/netxms/*
%{_unitdir}/netxmsd.service

############################

%changelog
* Mon Jun 10 2019 Alex Kirhenshtein <alk@netxms.org>
-
