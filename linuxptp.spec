%global gitdate 20121114
%global gitrev e6bbbb
Name:		linuxptp
Version:	0
Release:	0.6.%{gitdate}git%{gitrev}%{?dist}
Summary:	PTP implementation for Linux
ExclusiveArch:	%{ix86} x86_64

Group:		System Environment/Base
License:	GPLv2+
URL:		http://linuxptp.sourceforge.net/

# git clone git://git.code.sf.net/p/linuxptp/code linuxptp; cd linuxptp
# git archive --prefix=linuxptp/ %{gitrev} | gzip > linuxptp-%{gitdate}git%{gitrev}.tar.gz
Source0:	%{name}-%{gitdate}git%{gitrev}.tar.gz
Source1:	phc2sys.init
Source2:	ptp4l.init

BuildRequires:	kernel-headers > 2.6.32-322

Requires(post): chkconfig info
Requires(preun): chkconfig initscripts info
Requires(postun): initscripts

%description
This software is an implementation of the Precision Time Protocol (PTP)
according to IEEE standard 1588 for Linux. The dual design goals are to provide
a robust implementation of the standard and to use the most relevant and modern
Application Programming Interfaces (API) offered by the Linux kernel.
Supporting legacy APIs and other platforms is not a goal.

%prep
%setup -q -n %{name}

%build
make %{?_smp_mflags} \
	EXTRA_CFLAGS="$RPM_OPT_FLAGS -pie -fpie" \
	EXTRA_LDFLAGS="-Wl,-z,relro,-z,now"

%install
%makeinstall
mkdir -p $RPM_BUILD_ROOT{%{_sysconfdir}/sysconfig,%{_initrddir}}
install -m 644 -p default.cfg $RPM_BUILD_ROOT%{_sysconfdir}/ptp4l.conf
install -m 755 -p %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/phc2sys
install -m 755 -p %{SOURCE2} $RPM_BUILD_ROOT%{_initrddir}/ptp4l
echo 'OPTIONS="-f /etc/ptp4l.conf -i eth0"' > \
	$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ptp4l
echo 'OPTIONS="-d /dev/pps0"' > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/phc2sys

%post
/sbin/chkconfig --add ptp4l
/sbin/chkconfig --add phc2sys
:

%preun
if [ "$1" -eq 0 ]; then
	/sbin/service phc2sys stop &> /dev/null
	/sbin/chkconfig --del phc2sys
	/sbin/service ptp4l stop &> /dev/null
	/sbin/chkconfig --del ptp4l
fi
:

%postun
if [ "$1" -ge 1 ]; then
	/sbin/service ptp4l condrestart &> /dev/null
	/sbin/service phc2sys condrestart &> /dev/null
fi
:

%files
%doc COPYING README.org default.cfg gPTP.cfg
%config(noreplace) %{_sysconfdir}/ptp4l.conf
%config(noreplace) %{_sysconfdir}/sysconfig/phc2sys
%config(noreplace) %{_sysconfdir}/sysconfig/ptp4l
%{_initrddir}/phc2sys
%{_initrddir}/ptp4l
%{_sbindir}/hwstamp_ctl
%{_sbindir}/phc2sys
%{_sbindir}/pmc
%{_sbindir}/ptp4l
%{_mandir}/man8/*.8*

%changelog
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
