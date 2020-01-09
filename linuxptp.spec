%global testsuite_ver 7c523f
%global clknetsim_ver 592d17

Name:		linuxptp
Version:	1.5
Release:	2%{?dist}
Summary:	PTP implementation for Linux
ExclusiveArch:	%{ix86} x86_64 ppc ppc64

Group:		System Environment/Base
License:	GPLv2+
URL:		http://linuxptp.sourceforge.net/

Source0:	http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tgz
Source1:	phc2sys.init
Source2:	ptp4l.init
Source3:	timemaster.init
Source4:	timemaster.conf
# external test suite
Source10:	https://github.com/mlichvar/linuxptp-testsuite/archive/%{testsuite_ver}/linuxptp-testsuite-%{testsuite_ver}.tar.gz
# simulator for test suite
Source11:	https://github.com/mlichvar/clknetsim/archive/%{clknetsim_ver}/clknetsim-%{clknetsim_ver}.tar.gz

Patch1:		linuxptp-rhdoc.patch
Patch2:		linuxptp-ntpmode.patch
Patch3:		linuxptp-phc2sys_reconf.patch
Patch4:		linuxptp-timemaster_kill.patch

BuildRequires:	kernel-headers > 2.6.32-477

Requires(post): chkconfig
Requires(preun): chkconfig initscripts
Requires(postun): initscripts

%description
This software is an implementation of the Precision Time Protocol (PTP)
according to IEEE standard 1588 for Linux. The dual design goals are to provide
a robust implementation of the standard and to use the most relevant and modern
Application Programming Interfaces (API) offered by the Linux kernel.
Supporting legacy APIs and other platforms is not a goal.

%prep
%setup -q -a 10 -a 11
%patch2 -p1 -b .ntpmode
%patch1 -p1 -b .rhdoc
%patch3 -p1 -b .phc2sys_reconf
%patch4 -p1 -b .timemaster_kill
mv linuxptp-testsuite-%{testsuite_ver}* testsuite
mv clknetsim-%{clknetsim_ver}* testsuite/clknetsim

%build
make %{?_smp_mflags} \
	EXTRA_CFLAGS="$RPM_OPT_FLAGS -fpie" \
	EXTRA_LDFLAGS="-pie -Wl,-z,relro,-z,now"

%install
%makeinstall

mkdir -p $RPM_BUILD_ROOT{%{_sysconfdir}/sysconfig,%{_initrddir},%{_mandir}/man5}
install -m 644 -p default.cfg $RPM_BUILD_ROOT%{_sysconfdir}/ptp4l.conf
install -m 755 -p %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/phc2sys
install -m 755 -p %{SOURCE2} $RPM_BUILD_ROOT%{_initrddir}/ptp4l
install -m 755 -p %{SOURCE3} $RPM_BUILD_ROOT%{_initrddir}/timemaster
install -m 644 -p %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}

echo 'OPTIONS="-f /etc/ptp4l.conf -i eth0"' > \
	$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ptp4l
echo 'OPTIONS="-a -r"' > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/phc2sys

echo '.so man8/ptp4l.8' > $RPM_BUILD_ROOT%{_mandir}/man5/ptp4l.conf.5
echo '.so man8/timemaster.8' > $RPM_BUILD_ROOT%{_mandir}/man5/timemaster.conf.5

%check
cd testsuite
make %{?_smp_mflags} -C clknetsim
PATH=..:$PATH ./run

%post
/sbin/chkconfig --add ptp4l
/sbin/chkconfig --add phc2sys
/sbin/chkconfig --add timemaster
:

%preun
if [ "$1" -eq 0 ]; then
	/sbin/service phc2sys stop &> /dev/null
	/sbin/chkconfig --del phc2sys
	/sbin/service ptp4l stop &> /dev/null
	/sbin/chkconfig --del ptp4l
	/sbin/service timemaster stop &> /dev/null
	/sbin/chkconfig --del timemaster
fi
:

%postun
if [ "$1" -ge 1 ]; then
	/sbin/service ptp4l condrestart &> /dev/null
	/sbin/service phc2sys condrestart &> /dev/null
	/sbin/service timemaster condrestart &> /dev/null
fi
:

%files
%doc COPYING README.org default.cfg gPTP.cfg
%config(noreplace) %{_sysconfdir}/ptp4l.conf
%config(noreplace) %{_sysconfdir}/sysconfig/phc2sys
%config(noreplace) %{_sysconfdir}/sysconfig/ptp4l
%config(noreplace) %{_sysconfdir}/timemaster.conf
%{_initrddir}/phc2sys
%{_initrddir}/ptp4l
%{_initrddir}/timemaster
%{_sbindir}/hwstamp_ctl
%{_sbindir}/phc2sys
%{_sbindir}/phc_ctl
%{_sbindir}/pmc
%{_sbindir}/ptp4l
%{_sbindir}/timemaster
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*

%changelog
* Mon May 18 2015 Miroslav Lichvar <mlichvar@redhat.com> 1.5-2
- kill timemaster processes by PID instead of process group (#1221514)

* Wed Feb 18 2015 Miroslav Lichvar <mlichvar@redhat.com> 1.5-1
- update to 1.5 (#1190222, #1085584)
- use pidfiles in init scripts

* Tue Jun 10 2014 Miroslav Lichvar <mlichvar@redhat.com> 1.4-2.20140318git2b099c
- build also on ppc and ppc64 (#1095400)

* Wed May 28 2014 Miroslav Lichvar <mlichvar@redhat.com> 1.4-1.20140318git2b099c
- update to 20140318git2b099c (#1067502, #1011022, #1019121, #1004996, #1016356)
- fix PIE linking (#1094368)
- include simulation test suite

* Mon Aug 05 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.3-1
- update to 1.3 (#991332, #916787)

* Tue Jul 30 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.2-3.20130730git7789f0
- update to 20130730git7789f0 (#916787)

* Fri Jul 19 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.2-2.20130719git48f4dc
- update to 20130719git48f4dc (#916787, #985531)
- add man page link for ptp4l.conf
- update kernel-headers build requirement
- change default phc2sys options to use -s

* Wed Jun 26 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.2-1.20130625gitfa41be
- update to 20130625gitfa41be
  (#916787, #977258, #910966, #910974, #924041, #966787)
- improve initial frequency estimation

* Thu Nov 22 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.6.20121114gite6bbbb
- update to 20121114gite6bbbb
- add versioned build requirement on kernel-headers

* Fri Nov 09 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.5.20121109git4e8107
- update to 20121109git4e8107
- install unchanged default.cfg as ptp4l.conf
- update phc2sys service description

* Fri Sep 21 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.4.20120920git6ce135
- fix issues found in package review (#859193)

* Thu Sep 20 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.3.20120920git6ce135
- update to git 6ce135
- add phc2sys service

* Tue Sep 11 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.2.20120905git9edd31
- update to git 9edd31

* Tue Aug 21 2012 Miroslav Lichvar <mlichvar@redhat.com> 0-0.1.20120820gite4c3fb
- initial release
