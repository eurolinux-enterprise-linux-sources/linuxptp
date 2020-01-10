%global _hardened_build 1
%global testsuite_ver 502e82
%global clknetsim_ver ce89a1
Name:		linuxptp
Version:	1.8
Release:	3%{?dist}.1
Summary:	PTP implementation for Linux

Group:		System Environment/Base
License:	GPLv2+
URL:		http://linuxptp.sourceforge.net/

Source0:	https://downloads.sourceforge.net/%{name}/%{name}-%{version}.tgz
Source1:	phc2sys.service
Source2:	ptp4l.service
Source3:	timemaster.service
Source4:	timemaster.conf
# external test suite
Source10:	https://github.com/mlichvar/linuxptp-testsuite/archive/%{testsuite_ver}/linuxptp-testsuite-%{testsuite_ver}.tar.gz
# simulator for test suite
Source11:	https://github.com/mlichvar/clknetsim/archive/%{clknetsim_ver}/clknetsim-%{clknetsim_ver}.tar.gz

# update default TAI-UTC offset and make it configurable
Patch1:		linuxptp-utcoffset.patch
# add options to tag ptp4l/phc2sys log messages and use them in timemaster
Patch2:		linuxptp-messagetag.patch
# check support for SW timestamping in timemaster
Patch3:		linuxptp-swtscheck.patch
# fix leaks of sockets in error handling
Patch4:		linuxptp-closesocket.patch
# force BMC election when link goes down
Patch5:		linuxptp-linkdown.patch
# Fix phc2sys to check both the state and new_state variables of the clock
Patch6:   linuxptp-statechange.patch

BuildRequires:	systemd-units

Requires(post):	systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units

%description
This software is an implementation of the Precision Time Protocol (PTP)
according to IEEE standard 1588 for Linux. The dual design goals are to provide
a robust implementation of the standard and to use the most relevant and modern
Application Programming Interfaces (API) offered by the Linux kernel.
Supporting legacy APIs and other platforms is not a goal.

%prep
%setup -q -a 10 -a 11
%patch1 -p1 -b .utcoffset
%patch2 -p1 -b .messagetag
%patch3 -p1 -b .swtscheck
%patch4 -p1 -b .closesocket
%patch5 -p1 -b .linkdown
%patch6 -p1 -b .statechange
mv linuxptp-testsuite-%{testsuite_ver}* testsuite
mv clknetsim-%{clknetsim_ver}* testsuite/clknetsim

%build
make %{?_smp_mflags} \
	EXTRA_CFLAGS="$RPM_OPT_FLAGS" \
	EXTRA_LDFLAGS="$RPM_LD_FLAGS"

%install
%makeinstall

mkdir -p $RPM_BUILD_ROOT{%{_sysconfdir}/sysconfig,%{_unitdir},%{_mandir}/man5}
install -m 644 -p default.cfg $RPM_BUILD_ROOT%{_sysconfdir}/ptp4l.conf
install -m 644 -p %{SOURCE1} %{SOURCE2} %{SOURCE3} $RPM_BUILD_ROOT%{_unitdir}
install -m 644 -p %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}

echo 'OPTIONS="-f /etc/ptp4l.conf -i eth0"' > \
	$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ptp4l
echo 'OPTIONS="-a -r"' > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/phc2sys

echo '.so man8/ptp4l.8' > $RPM_BUILD_ROOT%{_mandir}/man5/ptp4l.conf.5
echo '.so man8/timemaster.8' > $RPM_BUILD_ROOT%{_mandir}/man5/timemaster.conf.5

%check
cd testsuite
# set random seed to get deterministic results
export CLKNETSIM_RANDOM_SEED=26743
make %{?_smp_mflags} -C clknetsim
PATH=..:$PATH ./run

%post
%systemd_post phc2sys.service ptp4l.service timemaster.service

%preun
%systemd_preun phc2sys.service ptp4l.service timemaster.service

%postun
%systemd_postun_with_restart phc2sys.service ptp4l.service timemaster.service

%files
%doc COPYING README.org default.cfg gPTP.cfg
%config(noreplace) %{_sysconfdir}/ptp4l.conf
%config(noreplace) %{_sysconfdir}/sysconfig/phc2sys
%config(noreplace) %{_sysconfdir}/sysconfig/ptp4l
%config(noreplace) %{_sysconfdir}/timemaster.conf
%{_unitdir}/phc2sys.service
%{_unitdir}/ptp4l.service
%{_unitdir}/timemaster.service
%{_sbindir}/hwstamp_ctl
%{_sbindir}/phc2sys
%{_sbindir}/phc_ctl
%{_sbindir}/pmc
%{_sbindir}/ptp4l
%{_sbindir}/timemaster
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*

%changelog
* Fri Sep 08 2017 Michal Ruprich <mruprich@redhat.com> 1.8-3.1
- Resolves: #1489425 - Race condition in phc2sys

* Wed Mar 15 2017 Miroslav Lichvar <mlichvar@redhat.com> 1.8-3
- fix backport of linkdown patch

* Tue Mar 14 2017 Miroslav Lichvar <mlichvar@redhat.com> 1.8-2
- force BMC election when link goes down

* Tue Feb 07 2017 Miroslav Lichvar <mlichvar@redhat.com> 1.8-1
- update to 1.8 (#1359311 #1353336)

* Tue Nov 25 2014 Miroslav Lichvar <mlichvar@redhat.com> 1.4-3.20140718gitbdb6a3
- fix resetting of linreg servo (#1165045)
- fix phc2sys automatic mode with multiple interfaces (#1108795)

* Tue Oct 14 2014 Miroslav Lichvar <mlichvar@redhat.com> 1.4-2.20140718gitbdb6a3
- add timemaster (#1085580)
- send peer messages to correct address
- make NTP SHM segment number configurable
- update UDS handling to allow running multiple ptp4l/phc2sys instances
- fix warnings from static analysis

* Wed Sep 03 2014 Miroslav Lichvar <mlichvar@redhat.com> 1.4-1.20140718gitbdb6a3
- update to 20140718gitbdb6a3 (#1108795, #1059039)
- fix PIE linking (#1092537)
- replace hardening build flags with _hardened_build
- include simulation test suite

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1.3-3
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.3-2
- Mass rebuild 2013-12-27

* Fri Aug 02 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.3-1
- update to 1.3

* Tue Jul 30 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.2-3.20130730git7789f0
- update to 20130730git7789f0

* Fri Jul 19 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.2-2.20130719git46db40
- update to 20130719git46db40
- drop old systemd scriptlets
- add man page link for ptp4l.conf

* Mon Apr 22 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.2-1
- update to 1.2

* Mon Feb 18 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.1-1
- update to 1.1
- log phc2sys output

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Dec 13 2012 Miroslav Lichvar <mlichvar@redhat.com> 1.0-1
- update to 1.0

* Fri Nov 09 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.3.20121109git4e8107
- update to 20121109git4e8107
- install unchanged default.cfg as ptp4l.conf
- drop conflicts from phc2sys service

* Fri Sep 21 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.2.20120920git6ce135
- fix issues found in package review (#859193)

* Thu Sep 20 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.1.20120920git6ce135
- initial release
