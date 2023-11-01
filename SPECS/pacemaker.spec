# User-configurable globals and defines to control package behavior
# (these should not test {with X} values, which are declared later)

## User and group to use for nonprivileged services
%global uname hacluster
%global gname haclient

## Where to install Pacemaker documentation
%if 0%{?suse_version} > 0
%global pcmk_docdir %{_docdir}/%{name}-%{version}
%else
%if 0%{?rhel} > 7
%global pcmk_docdir %{_docdir}/%{name}-doc
%else
%global pcmk_docdir %{_docdir}/%{name}
%endif
%endif

## GitHub entity that distributes source (for ease of using a fork)
%global github_owner ClusterLabs

## Where bug reports should be submitted
## Leave bug_url undefined to use ClusterLabs default, others define it here
%if 0%{?rhel}
%global bug_url https://bugzilla.redhat.com/
%else
%if 0%{?fedora}
%global bug_url https://bugz.fedoraproject.org/%{name}
%endif
%endif

## What to use as the OCF resource agent root directory
%global ocf_root %{_prefix}/lib/ocf

## Upstream pacemaker version, and its package version (specversion
## can be incremented to build packages reliably considered "newer"
## than previously built packages with the same pcmkversion)
%global pcmkversion 2.1.5
%global specversion 9

## Upstream commit (full commit ID, abbreviated commit ID, or tag) to build
%global commit a3f44794f94e1571c6ba0042915ade369b4ce4b1

## Since git v2.11, the extent of abbreviation is autoscaled by default
## (used to be constant of 7), so we need to convey it for non-tags, too.
%if (0%{?fedora} >= 26) || (0%{?rhel} >= 9)
%global commit_abbrev 9
%else
%global commit_abbrev 7
%endif

## Nagios source control identifiers
%global nagios_name nagios-agents-metadata
%global nagios_hash 105ab8a


# Define conditionals so that "rpmbuild --with <feature>" and
# "rpmbuild --without <feature>" can enable and disable specific features

## Add option to enable support for stonith/external fencing agents
%bcond_with stonithd

## Add option for whether to support storing sensitive information outside CIB
%bcond_without cibsecrets

## Add option to enable Native Language Support (experimental)
%bcond_with nls

## Add option to create binaries suitable for use with profiling tools
%bcond_with profiling

## Allow deprecated option to skip (or enable, on RHEL) documentation
%if 0%{?rhel}
%bcond_with doc
%else
%bcond_without doc
%endif

## Add option to default to start-up synchronization with SBD.
##
## If enabled, SBD *MUST* be built to default similarly, otherwise data
## corruption could occur. Building both Pacemaker and SBD to default
## to synchronization improves safety, without requiring higher-level tools
## to be aware of the setting or requiring users to modify configurations
## after upgrading to versions that support synchronization.
%bcond_without sbd_sync

## Add option to prefix package version with "0."
## (so later "official" packages will be considered updates)
%bcond_with pre_release

## Add option to ship Upstart job files
%bcond_with upstart_job

## Add option to turn off hardening of libraries and daemon executables
%bcond_without hardening

## Add option to enable (or disable, on RHEL 8) links for legacy daemon names
%if 0%{?rhel} && 0%{?rhel} <= 8
%bcond_without legacy_links
%else
%bcond_with legacy_links
%endif

# Define globals for convenient use later

## Workaround to use parentheses in other globals
%global lparen (
%global rparen )

## Whether this is a tagged release (final or release candidate)
%define tag_release %(c=%{commit}; case ${c} in Pacemaker-*%{rparen} echo 1 ;;
                      *%{rparen} echo 0 ;; esac)

## Portion of export/dist tarball name after "pacemaker-", and release version
%if 0%{tag_release}
%define archive_version %(c=%{commit}; echo ${c:10})
%define archive_github_url %{commit}#/%{name}-%{archive_version}.tar.gz
%else
%if "%{commit}" == "DIST"
%define archive_version %{pcmkversion}
%define archive_github_url %{archive_version}#/%{name}-%{pcmkversion}.tar.gz
%else
%define archive_version %(c=%{commit}; echo ${c:0:%{commit_abbrev}})
%define archive_github_url %{archive_version}#/%{name}-%{archive_version}.tar.gz
%endif
%endif
### Always use a simple release number
%define pcmk_release %{specversion}

## Whether this platform defaults to using systemd as an init system
## (needs to be evaluated prior to BuildRequires being enumerated and
## installed as it's intended to conditionally select some of these, and
## for that there are only few indicators with varying reliability:
## - presence of systemd-defined macros (when building in a full-fledged
##   environment, which is not the case with ordinary mock-based builds)
## - systemd-aware rpm as manifested with the presence of particular
##   macro (rpm itself will trivially always be present when building)
## - existence of /usr/lib/os-release file, which is something heavily
##   propagated by systemd project
## - when not good enough, there's always a possibility to check
##   particular distro-specific macros (incl. version comparison)
%define systemd_native (%{?_unitdir:1}%{!?_unitdir:0}%{nil \
  } || %{?__transaction_systemd_inhibit:1}%{!?__transaction_systemd_inhibit:0}%{nil \
  } || %(test -f /usr/lib/os-release; test $? -ne 0; echo $?))

# Even though we pass @SYSTEM here, Pacemaker is still an exception to the
# crypto policies because it adds "+ANON-DH" for CIB remote commands and
# "+DHE-PSK:+PSK" for Pacemaker Remote connections. This is currently
# required for the respective functionality.
%if 0%{?fedora} > 20 || 0%{?rhel} > 7
## Base GnuTLS cipher priorities (presumably only the initial, required keyword)
## overridable with "rpmbuild --define 'pcmk_gnutls_priorities PRIORITY-SPEC'"
%define gnutls_priorities %{?pcmk_gnutls_priorities}%{!?pcmk_gnutls_priorities:@SYSTEM}
%endif

%if 0%{?fedora} > 22 || 0%{?rhel} > 7
%global supports_recommends 1
%endif

## Different distros name certain packages differently
## (note: corosync libraries also differ, but all provide corosync-devel)
%if 0%{?suse_version} > 0
%global pkgname_bzip2_devel libbz2-devel
%global pkgname_docbook_xsl docbook-xsl-stylesheets
%global pkgname_gettext gettext-tools
%global pkgname_gnutls_devel libgnutls-devel
%global pkgname_shadow_utils shadow
%global pkgname_procps procps
%global pkgname_glue_libs libglue
%global pkgname_pcmk_libs lib%{name}3
%global hacluster_id 90
%else
%global pkgname_libtool_devel libtool-ltdl-devel
%global pkgname_libtool_devel_arch libtool-ltdl-devel%{?_isa}
%global pkgname_bzip2_devel bzip2-devel
%global pkgname_docbook_xsl docbook-style-xsl
%global pkgname_gettext gettext-devel
%global pkgname_gnutls_devel gnutls-devel
%global pkgname_shadow_utils shadow-utils
%global pkgname_procps procps-ng
%global pkgname_glue_libs cluster-glue-libs
%global pkgname_pcmk_libs %{name}-libs
%global hacluster_id 189
%endif

## Distro-specific configuration choices

### Use 2.0-style output when other distro packages don't support current output
%if 0%{?fedora} || ( 0%{?rhel} && 0%{?rhel} <= 8 )
%global compat20 --enable-compat-2.0
%endif

### Default concurrent-fencing to true when distro prefers that
%if 0%{?rhel} >= 7
%global concurrent_fencing --with-concurrent-fencing-default=true
%endif

### Default resource-stickiness to 1 when distro prefers that
%if 0%{?fedora} >= 35 || 0%{?rhel} >= 9
%global resource_stickiness --with-resource-stickiness-default=1
%endif


# Python-related definitions

## Turn off auto-compilation of Python files outside Python specific paths,
## so there's no risk that unexpected "__python" macro gets picked to do the
## RPM-native byte-compiling there (only "{_datadir}/pacemaker/tests" affected)
## -- distro-dependent tricks or automake's fallback to be applied there
%if %{defined _python_bytecompile_extra}
%global _python_bytecompile_extra 0
%else
### the statement effectively means no RPM-native byte-compiling will occur at
### all, so distro-dependent tricks for Python-specific packages to be applied
%global __os_install_post %(echo '%{__os_install_post}' | {
                            sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g'; })
%endif

## Prefer Python 3 definitions explicitly, in case 2 is also available
%if %{defined __python3}
%global python_name python3
%global python_path %{__python3}
%define python_site %{?python3_sitelib}%{!?python3_sitelib:%(
  %{python_path} -c 'from distutils.sysconfig import get_python_lib as gpl; print(gpl(1))' 2>/dev/null)}
%else
%if %{defined python_version}
%global python_name python%(echo %{python_version} | cut -d'.' -f1)
%define python_path %{?__python}%{!?__python:/usr/bin/%{python_name}}
%else
%global python_name python
%global python_path %{?__python}%{!?__python:/usr/bin/python%{?python_pkgversion}}
%endif
%define python_site %{?python_sitelib}%{!?python_sitelib:%(
  %{python_name} -c 'from distutils.sysconfig import get_python_lib as gpl; print(gpl(1))' 2>/dev/null)}
%endif


# Keep sane profiling data if requested
%if %{with profiling}

## Disable -debuginfo package and stripping binaries/libraries
%define debug_package %{nil}

%endif


Name:          pacemaker
Summary:       Scalable High-Availability cluster resource manager
Version:       %{pcmkversion}
Release:       %{pcmk_release}.3%{?dist}
%if %{defined _unitdir}
License:       GPLv2+ and LGPLv2+
%else
# initscript is Revised BSD
License:       GPLv2+ and LGPLv2+ and BSD
%endif
Url:           https://www.clusterlabs.org/

# Example: https://codeload.github.com/ClusterLabs/pacemaker/tar.gz/e91769e
# will download pacemaker-e91769e.tar.gz
#
# The ending part starting with '#' is ignored by github but necessary for
# rpmbuild to know what the tar archive name is. (The downloaded file will be
# named correctly only for commit IDs, not tagged releases.)
#
# You can use "spectool -s 0 pacemaker.spec" (rpmdevtools) to show final URL.
Source0:       https://codeload.github.com/%{github_owner}/%{name}/tar.gz/%{archive_github_url}
Source1:       nagios-agents-metadata-%{nagios_hash}.tar.gz

# upstream commits
Patch001:      001-sync-points.patch
Patch002:      002-remote-regression.patch
Patch003:      003-history-cleanup.patch
Patch004:      004-g_source_remove.patch
Patch005:      005-query-null.patch
Patch006:      006-watchdog-fencing-topology.patch
Patch007:      007-attrd-dampen.patch
Patch008:      008-controller-reply.patch
Patch009:      009-glib-assertions.patch
Patch010:      010-attrd-shutdown.patch
Patch011:      011-attrd-shutdown-2.patch

# downstream-only commits
#Patch1xx:      1xx-xxxx.patch

Requires:      resource-agents
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}
Requires:      %{name}-cluster-libs%{?_isa} = %{version}-%{release}
Requires:      %{name}-cli = %{version}-%{release}
%if !%{defined _unitdir}
Requires:      %{pkgname_procps}
Requires:      psmisc
%endif
%{?systemd_requires}

%if %{defined centos}
ExclusiveArch: aarch64 i686 ppc64le s390x x86_64 %{arm}
%else
%if 0%{?rhel}
ExclusiveArch: aarch64 i686 ppc64le s390x x86_64
%endif
%endif

Requires:      %{python_path}
BuildRequires: %{python_name}-devel

# Pacemaker requires a minimum libqb functionality
Requires:      libqb >= 0.17.0
BuildRequires: libqb-devel >= 0.17.0

# Required basic build tools
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: coreutils
BuildRequires: findutils
BuildRequires: gcc
BuildRequires: grep
BuildRequires: libtool
%if %{defined pkgname_libtool_devel}
BuildRequires: %{?pkgname_libtool_devel}
%endif
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: sed

# Required for core functionality
BuildRequires: pkgconfig(glib-2.0) >= 2.42
BuildRequires: libxml2-devel
BuildRequires: libxslt-devel
BuildRequires: libuuid-devel
BuildRequires: %{pkgname_bzip2_devel}

# Enables optional functionality
BuildRequires: pkgconfig(dbus-1)
BuildRequires: %{pkgname_docbook_xsl}
BuildRequires: %{pkgname_gnutls_devel}
BuildRequires: help2man
BuildRequires: ncurses-devel
BuildRequires: pam-devel
BuildRequires: %{pkgname_gettext} >= 0.18

# Required for "make check"
BuildRequires: libcmocka-devel

%if %{systemd_native}
BuildRequires: pkgconfig(systemd)
%endif

# RH patches are created by git, so we need git to apply them
BuildRequires: git

# The RHEL 8.5+ build root has corosync_cfg_trackstart() available, so
# Pacemaker's configure script will build support for it. Add a hard dependency
# to ensure users have compatible Corosync libraries if they upgrade Pacemaker.
Requires:      corosync >= 3.1.1
BuildRequires: corosync-devel >= 3.1.1

%if %{with stonithd}
BuildRequires: %{pkgname_glue_libs}-devel
%endif

%if %{with doc}
BuildRequires: asciidoc
BuildRequires: inkscape
BuildRequires: %{python_name}-sphinx
%endif

# Booth requires this
Provides:      pacemaker-ticket-support = 2.0

Provides:      pcmk-cluster-manager = %{version}-%{release}
Provides:      pcmk-cluster-manager%{?_isa} = %{version}-%{release}

# Bundled bits
## Pacemaker uses the crypto/md5-buffer module from gnulib
%if 0%{?fedora} || 0%{?rhel}
Provides:      bundled(gnulib) = 20200404
%endif

%description
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

It supports more than 16 node clusters with significant capabilities
for managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

Available rpmbuild rebuild options:
  --with(out) : cibsecrets hardening nls pre_release profiling
                stonithd

%package cli
License:       GPLv2+ and LGPLv2+
Summary:       Command line tools for controlling Pacemaker clusters
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}
# For crm_report
Requires:      tar
Requires:      bzip2
Requires:      perl-TimeDate
Requires:      %{pkgname_procps}
Requires:      psmisc
Requires(post):coreutils

%description cli
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{name}-cli package contains command line tools that can be used
to query and control the cluster from machines that may, or may not,
be part of the cluster.

%package -n %{pkgname_pcmk_libs}
License:       GPLv2+ and LGPLv2+
Summary:       Core Pacemaker libraries
Requires(pre): %{pkgname_shadow_utils}
Requires:      %{name}-schemas = %{version}-%{release}
# sbd 1.4.0+ supports the libpe_status API for pe_working_set_t
# sbd 1.4.2+ supports startup/shutdown handshake via pacemakerd-api
#            and handshake defaults to enabled in this spec
Conflicts:     sbd < 1.4.2

%description -n %{pkgname_pcmk_libs}
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{pkgname_pcmk_libs} package contains shared libraries needed for cluster
nodes and those just running the CLI tools.

%package cluster-libs
License:       GPLv2+ and LGPLv2+
Summary:       Cluster Libraries used by Pacemaker
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}

%description cluster-libs
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{name}-cluster-libs package contains cluster-aware shared
libraries needed for nodes that will form part of the cluster nodes.

%package remote
%if %{defined _unitdir}
License:       GPLv2+ and LGPLv2+
%else
# initscript is Revised BSD
License:       GPLv2+ and LGPLv2+ and BSD
%endif
Summary:       Pacemaker remote executor daemon for non-cluster nodes
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}
Requires:      %{name}-cli = %{version}-%{release}
Requires:      resource-agents
%if !%{defined _unitdir}
Requires:      %{pkgname_procps}
%endif
# -remote can be fully independent of systemd
%{?systemd_ordering}%{!?systemd_ordering:%{?systemd_requires}}
Provides:      pcmk-cluster-manager = %{version}-%{release}
Provides:      pcmk-cluster-manager%{?_isa} = %{version}-%{release}

%description remote
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{name}-remote package contains the Pacemaker Remote daemon
which is capable of extending pacemaker functionality to remote
nodes not running the full corosync/cluster stack.

%package -n %{pkgname_pcmk_libs}-devel
License:       GPLv2+ and LGPLv2+
Summary:       Pacemaker development package
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}
Requires:      %{name}-cluster-libs%{?_isa} = %{version}-%{release}
Requires:      %{pkgname_bzip2_devel}%{?_isa}
Requires:      corosync-devel >= 2.0.0
Requires:      glib2-devel%{?_isa}
Requires:      libqb-devel%{?_isa}
%if %{defined pkgname_libtool_devel_arch}
Requires:      %{?pkgname_libtool_devel_arch}
%endif
Requires:      libuuid-devel%{?_isa}
Requires:      libxml2-devel%{?_isa}
Requires:      libxslt-devel%{?_isa}

%description -n %{pkgname_pcmk_libs}-devel
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{pkgname_pcmk_libs}-devel package contains headers and shared libraries
for developing tools for Pacemaker.

%package       cts
License:       GPLv2+ and LGPLv2+
Summary:       Test framework for cluster-related technologies like Pacemaker
Requires:      %{python_path}
Requires:      %{pkgname_pcmk_libs} = %{version}-%{release}
Requires:      %{name}-cli = %{version}-%{release}
Requires:      %{pkgname_procps}
Requires:      psmisc
Requires:      %{python_name}-psutil
BuildArch:     noarch

# systemd Python bindings are a separate package in some distros
%if %{defined systemd_requires}
%if 0%{?fedora} > 22 || 0%{?rhel} > 7
Requires:      %{python_name}-systemd
%endif
%endif

%description   cts
Test framework for cluster-related technologies like Pacemaker

%package       doc
License:       CC-BY-SA-4.0
Summary:       Documentation for Pacemaker
BuildArch:     noarch

%description   doc
Documentation for Pacemaker.

Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

%package       schemas
License:       GPLv2+
Summary:       Schemas and upgrade stylesheets for Pacemaker
BuildArch:     noarch

%description   schemas
Schemas and upgrade stylesheets for Pacemaker

Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

%package       nagios-plugins-metadata
License:       GPLv3
Summary:       Pacemaker Nagios Metadata
# NOTE below are the plugins this metadata uses.
# These packages are not requirements because RHEL does not ship these plugins.
# This metadata provides third-party support for nagios. Users may install the
# plugins via third-party rpm packages, or source. If RHEL ships the plugins in
# the future, we should consider enabling the following required fields.
#Requires:      nagios-plugins-http
#Requires:      nagios-plugins-ldap
#Requires:      nagios-plugins-mysql
#Requires:      nagios-plugins-pgsql
#Requires:      nagios-plugins-tcp
Requires:      pcmk-cluster-manager
BuildArch:     noarch

%description   nagios-plugins-metadata
The metadata files required for Pacemaker to execute the nagios plugin
monitor resources.

%prep
%autosetup -a 1 -n %{name}-%{archive_version} -S git_am -p 1

%build

export systemdsystemunitdir=%{?_unitdir}%{!?_unitdir:no}

%if %{with hardening}
# prefer distro-provided hardening flags in case they are defined
# through _hardening_{c,ld}flags macros, configure script will
# use its own defaults otherwise; if such hardenings are completely
# undesired, rpmbuild using "--without hardening"
# (or "--define '_without_hardening 1'")
export CFLAGS_HARDENED_EXE="%{?_hardening_cflags}"
export CFLAGS_HARDENED_LIB="%{?_hardening_cflags}"
export LDFLAGS_HARDENED_EXE="%{?_hardening_ldflags}"
export LDFLAGS_HARDENED_LIB="%{?_hardening_ldflags}"
%endif

./autogen.sh

%{configure}                                                                    \
        PYTHON=%{python_path}                                                   \
        %{!?with_hardening:    --disable-hardening}                             \
        %{?with_legacy_links:  --enable-legacy-links}                           \
        %{?with_profiling:     --with-profiling}                                \
        %{?with_cibsecrets:    --with-cibsecrets}                               \
        %{?with_nls:           --enable-nls}                                    \
        %{?with_sbd_sync:      --with-sbd-sync-default="true"}                  \
        %{?gnutls_priorities:  --with-gnutls-priorities="%{gnutls_priorities}"} \
        %{?bug_url:            --with-bug-url=%{bug_url}}                       \
        %{?ocf_root:           --with-ocfdir=%{ocf_root}}                       \
        %{?concurrent_fencing}                                                  \
        %{?resource_stickiness}                                                 \
        %{?compat20}                                                            \
        --disable-static                                                        \
        --with-initdir=%{_initrddir}                                            \
        --with-runstatedir=%{_rundir}                                           \
        --localstatedir=%{_var}                                                 \
        --with-nagios                                                             \
        --with-nagios-metadata-dir=%{_datadir}/pacemaker/nagios/plugins-metadata/ \
        --with-nagios-plugin-dir=%{_libdir}/nagios/plugins/                       \
        --with-version=%{version}-%{release}

%if 0%{?suse_version} >= 1200
# Fedora handles rpath removal automagically
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%endif

make %{_smp_mflags} V=1

%check
make %{_smp_mflags} check
{ cts/cts-scheduler --run load-stopped-loop \
  && cts/cts-cli \
  && touch .CHECKED
} 2>&1 | sed 's/[fF]ail/faiil/g'  # prevent false positives in rpmlint
[ -f .CHECKED ] && rm -f -- .CHECKED
exit $?  # TODO remove when rpm<4.14 compatibility irrelevant

%install
# skip automake-native Python byte-compilation, since RPM-native one (possibly
# distro-confined to Python-specific directories, which is currently the only
# relevant place, anyway) assures proper intrinsic alignment with wider system
# (such as with py_byte_compile macro, which is concurrent Fedora/EL specific)
make install \
  DESTDIR=%{buildroot} V=1 docdir=%{pcmk_docdir} \
  %{?_python_bytecompile_extra:%{?py_byte_compile:am__py_compile=true}}

%if %{with upstart_job}
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/init
install -m 644 pacemakerd/pacemaker.upstart ${RPM_BUILD_ROOT}%{_sysconfdir}/init/pacemaker.conf
install -m 644 pacemakerd/pacemaker.combined.upstart ${RPM_BUILD_ROOT}%{_sysconfdir}/init/pacemaker.combined.conf
install -m 644 tools/crm_mon.upstart ${RPM_BUILD_ROOT}%{_sysconfdir}/init/crm_mon.conf
%endif

mkdir -p %{buildroot}%{_datadir}/pacemaker/nagios/plugins-metadata
for file in $(find %{nagios_name}-%{nagios_hash}/metadata -type f); do
    install -m 644 $file %{buildroot}%{_datadir}/pacemaker/nagios/plugins-metadata
done

%if %{defined _unitdir}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/lib/rpm-state/%{name}
%endif

%if %{with nls}
%find_lang %{name}
%endif

# Don't package libtool archives
find %{buildroot} -name '*.la' -type f -print0 | xargs -0 rm -f

# Do not package these either on RHEL
rm -f %{buildroot}/%{_sbindir}/fence_legacy
rm -f %{buildroot}/%{_mandir}/man8/fence_legacy.*
find %{buildroot} -name '*o2cb*' -type f -print0 | xargs -0 rm -f

# For now, don't package the servicelog-related binaries built only for
# ppc64le when certain dependencies are installed. If they get more exercise by
# advanced users, we can reconsider.
rm -f %{buildroot}/%{_sbindir}/notifyServicelogEvent
rm -f %{buildroot}/%{_sbindir}/ipmiservicelogd

# Byte-compile Python sources where suitable and the distro procedures known
%if %{defined py_byte_compile}
%{py_byte_compile %{python_path} %{buildroot}%{_datadir}/pacemaker/tests}
%if !%{defined _python_bytecompile_extra}
%{py_byte_compile %{python_path} %{buildroot}%{python_site}/cts}
%endif
%endif

%post
%if %{defined _unitdir}
%systemd_post pacemaker.service
%else
/sbin/chkconfig --add pacemaker || :
%endif

%preun
%if %{defined _unitdir}
%systemd_preun pacemaker.service
%else
/sbin/service pacemaker stop >/dev/null 2>&1 || :
if [ "$1" -eq 0 ]; then
    # Package removal, not upgrade
    /sbin/chkconfig --del pacemaker || :
fi
%endif

%postun
%if %{defined _unitdir}
%systemd_postun_with_restart pacemaker.service
%endif

%pre remote
%if %{defined _unitdir}
# Stop the service before anything is touched, and remember to restart
# it as one of the last actions (compared to using systemd_postun_with_restart,
# this avoids suicide when sbd is in use)
systemctl --quiet is-active pacemaker_remote
if [ $? -eq 0 ] ; then
    mkdir -p %{_localstatedir}/lib/rpm-state/%{name}
    touch %{_localstatedir}/lib/rpm-state/%{name}/restart_pacemaker_remote
    systemctl stop pacemaker_remote >/dev/null 2>&1
else
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/restart_pacemaker_remote
fi
%endif

%post remote
%if %{defined _unitdir}
%systemd_post pacemaker_remote.service
%else
/sbin/chkconfig --add pacemaker_remote || :
%endif

%preun remote
%if %{defined _unitdir}
%systemd_preun pacemaker_remote.service
%else
/sbin/service pacemaker_remote stop >/dev/null 2>&1 || :
if [ "$1" -eq 0 ]; then
    # Package removal, not upgrade
    /sbin/chkconfig --del pacemaker_remote || :
fi
%endif

%postun remote
%if %{defined _unitdir}
# This next line is a no-op, because we stopped the service earlier, but
# we leave it here because it allows us to revert to the standard behavior
# in the future if desired
%systemd_postun_with_restart pacemaker_remote.service
# Explicitly take care of removing the flag-file(s) upon final removal
if [ "$1" -eq 0 ] ; then
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/restart_pacemaker_remote
fi
%endif

%posttrans remote
%if %{defined _unitdir}
if [ -e %{_localstatedir}/lib/rpm-state/%{name}/restart_pacemaker_remote ] ; then
    systemctl start pacemaker_remote >/dev/null 2>&1
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/restart_pacemaker_remote
fi
%endif

%post cli
%if %{defined _unitdir}
%systemd_post crm_mon.service
%endif
if [ "$1" -eq 2 ]; then
    # Package upgrade, not initial install:
    # Move any pre-2.0 logs to new location to ensure they get rotated
    { mv -fbS.rpmsave %{_var}/log/pacemaker.log* %{_var}/log/pacemaker \
      || mv -f %{_var}/log/pacemaker.log* %{_var}/log/pacemaker
    } >/dev/null 2>/dev/null || :
fi

%preun cli
%if %{defined _unitdir}
%systemd_preun crm_mon.service
%endif

%postun cli
%if %{defined _unitdir}
%systemd_postun_with_restart crm_mon.service
%endif

%pre -n %{pkgname_pcmk_libs}
getent group %{gname} >/dev/null || groupadd -r %{gname} -g %{hacluster_id}
getent passwd %{uname} >/dev/null || useradd -r -g %{gname} -u %{hacluster_id} -s /sbin/nologin -c "cluster user" %{uname}
exit 0

%if %{defined ldconfig_scriptlets}
%ldconfig_scriptlets -n %{pkgname_pcmk_libs}
%ldconfig_scriptlets cluster-libs
%else
%post -n %{pkgname_pcmk_libs} -p /sbin/ldconfig
%postun -n %{pkgname_pcmk_libs} -p /sbin/ldconfig

%post cluster-libs -p /sbin/ldconfig
%postun cluster-libs -p /sbin/ldconfig
%endif

%files
###########################################################
%config(noreplace) %{_sysconfdir}/sysconfig/pacemaker
%{_sbindir}/pacemakerd

%if %{defined _unitdir}
%{_unitdir}/pacemaker.service
%else
%{_initrddir}/pacemaker
%endif

%exclude %{_libexecdir}/pacemaker/cts-log-watcher
%exclude %{_libexecdir}/pacemaker/cts-support
%exclude %{_sbindir}/pacemaker-remoted
%exclude %{_sbindir}/pacemaker_remoted
%exclude %{_datadir}/pacemaker/nagios
%{_libexecdir}/pacemaker/*

%{_sbindir}/crm_master
%{_sbindir}/fence_watchdog

%doc %{_mandir}/man7/pacemaker-controld.*
%doc %{_mandir}/man7/pacemaker-schedulerd.*
%doc %{_mandir}/man7/pacemaker-fenced.*
%doc %{_mandir}/man7/ocf_pacemaker_controld.*
%doc %{_mandir}/man7/ocf_pacemaker_remote.*
%doc %{_mandir}/man8/crm_master.*
%doc %{_mandir}/man8/fence_watchdog.*
%doc %{_mandir}/man8/pacemakerd.*

%doc %{_datadir}/pacemaker/alerts

%license licenses/GPLv2
%doc COPYING
%doc ChangeLog

%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker/cib
%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker/pengine
%{ocf_root}/resource.d/pacemaker/controld
%{ocf_root}/resource.d/pacemaker/remote

%if %{with upstart_job}
%config(noreplace) %{_sysconfdir}/init/pacemaker.conf
%config(noreplace) %{_sysconfdir}/init/pacemaker.combined.conf
%endif

%files cli
%dir %attr (750, root, %{gname}) %{_sysconfdir}/pacemaker
%config(noreplace) %{_sysconfdir}/logrotate.d/pacemaker
%config(noreplace) %{_sysconfdir}/sysconfig/crm_mon

%if %{defined _unitdir}
%{_unitdir}/crm_mon.service
%endif

%if %{with upstart_job}
%config(noreplace) %{_sysconfdir}/init/crm_mon.conf
%endif

%{_sbindir}/attrd_updater
%{_sbindir}/cibadmin
%if %{with cibsecrets}
%{_sbindir}/cibsecret
%endif
%{_sbindir}/crm_attribute
%{_sbindir}/crm_diff
%{_sbindir}/crm_error
%{_sbindir}/crm_failcount
%{_sbindir}/crm_mon
%{_sbindir}/crm_node
%{_sbindir}/crm_resource
%{_sbindir}/crm_rule
%{_sbindir}/crm_standby
%{_sbindir}/crm_verify
%{_sbindir}/crmadmin
%{_sbindir}/iso8601
%{_sbindir}/crm_shadow
%{_sbindir}/crm_simulate
%{_sbindir}/crm_report
%{_sbindir}/crm_ticket
%{_sbindir}/stonith_admin
# "dirname" is owned by -schemas, which is a prerequisite
%{_datadir}/pacemaker/report.collector
%{_datadir}/pacemaker/report.common
# XXX "dirname" is not owned by any prerequisite
%{_datadir}/snmp/mibs/PCMK-MIB.txt

%exclude %{ocf_root}/resource.d/pacemaker/controld
%exclude %{ocf_root}/resource.d/pacemaker/remote

%dir %{ocf_root}
%dir %{ocf_root}/resource.d
%{ocf_root}/resource.d/pacemaker

%doc %{_mandir}/man7/*
%exclude %{_mandir}/man7/pacemaker-controld.*
%exclude %{_mandir}/man7/pacemaker-schedulerd.*
%exclude %{_mandir}/man7/pacemaker-fenced.*
%exclude %{_mandir}/man7/ocf_pacemaker_controld.*
%exclude %{_mandir}/man7/ocf_pacemaker_remote.*
%doc %{_mandir}/man8/*
%exclude %{_mandir}/man8/crm_master.*
%exclude %{_mandir}/man8/fence_watchdog.*
%exclude %{_mandir}/man8/pacemakerd.*
%exclude %{_mandir}/man8/pacemaker-remoted.*

%license licenses/GPLv2
%doc COPYING
%doc ChangeLog

%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker
%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker/blackbox
%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker/cores
%dir %attr (770, %{uname}, %{gname}) %{_var}/log/pacemaker
%dir %attr (770, %{uname}, %{gname}) %{_var}/log/pacemaker/bundles

%files -n %{pkgname_pcmk_libs} %{?with_nls:-f %{name}.lang}
%{_libdir}/libcib.so.*
%{_libdir}/liblrmd.so.*
%{_libdir}/libcrmservice.so.*
%{_libdir}/libcrmcommon.so.*
%{_libdir}/libpe_status.so.*
%{_libdir}/libpe_rules.so.*
%{_libdir}/libpacemaker.so.*
%{_libdir}/libstonithd.so.*
%license licenses/LGPLv2.1
%doc COPYING
%doc ChangeLog

%files cluster-libs
%{_libdir}/libcrmcluster.so.*
%license licenses/LGPLv2.1
%doc COPYING
%doc ChangeLog

%files remote
%config(noreplace) %{_sysconfdir}/sysconfig/pacemaker
%if %{defined _unitdir}
# state directory is shared between the subpackets
# let rpm take care of removing it once it isn't
# referenced anymore and empty
%ghost %dir %{_localstatedir}/lib/rpm-state/%{name}
%{_unitdir}/pacemaker_remote.service
%else
%{_initrddir}/pacemaker_remote
%endif

%{_sbindir}/pacemaker-remoted
%{_sbindir}/pacemaker_remoted
%{_mandir}/man8/pacemaker-remoted.*
%license licenses/GPLv2
%doc COPYING
%doc ChangeLog

%files doc
%doc %{pcmk_docdir}
%license licenses/CC-BY-SA-4.0

%files cts
%{python_site}/cts
%{_datadir}/pacemaker/tests

%{_libexecdir}/pacemaker/cts-log-watcher
%{_libexecdir}/pacemaker/cts-support

%license licenses/GPLv2
%doc COPYING
%doc ChangeLog

%files -n %{pkgname_pcmk_libs}-devel
%{_includedir}/pacemaker
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%license licenses/LGPLv2.1
%doc COPYING
%doc ChangeLog

%files schemas
%license licenses/GPLv2
%dir %{_datadir}/pacemaker
%{_datadir}/pacemaker/*.rng
%{_datadir}/pacemaker/*.xsl
%{_datadir}/pacemaker/api
%{_datadir}/pacemaker/base
%{_datadir}/pkgconfig/pacemaker-schemas.pc

%files nagios-plugins-metadata
%dir %{_datadir}/pacemaker/nagios/plugins-metadata
%attr(0644,root,root) %{_datadir}/pacemaker/nagios/plugins-metadata/*
%license %{nagios_name}-%{nagios_hash}/COPYING

%changelog
* Wed Aug 30 2023 Chris Lumens <clumens@redhat.com> - 2.1.5-9.3
- Fix an additional shutdown race between attrd and the controller
- Related: rhbz2229013

* Tue Aug 8 2023 Chris Lumens <clumens@redhat.com> - 2.1.5-8.3
- Fix attrd race condition when shutting down
- Resolves: rhbz2229013

* Wed Aug 2 2023 Chris Lumens <clumens@redhat.com> - 2.1.5-8.2
- Apply dampening when creating attributes with attrd_updater -U
- Wait for a reply from various controller commands
- Resolves: rhbz2224070
- Resolves: rhbz2225668

* Fri May 5 2023 Klaus Wenninger <kwenning@redhat.com> - 2.1.5-8.1
- Fix overall timeout calculation if watchdog and another fencing
  device share a topology level
- Resolves: rhbz2187419

* Wed Feb 22 2023 Chris Lumens <clumens@redhat.com> - 2.1.5-8
- Rebuild with new release due to build system problems
- Related: rhbz2168249
- Related: rhbz2168675

* Tue Feb 21 2023 Chris Lumens <clumens@redhat.com> - 2.1.5-7
- Additional fixes for SIGABRT during pacemaker-fenced shutdown
- Backport fix for attrd_updater -QA not displaying all nodes
- Related: rhbz2168249
- Resolves: rhbz2168675

* Wed Feb 8 2023 Chris Lumens <clumens@redhat.com> - 2.1.5-6
- Backport fix for migration history cleanup causing resource recovery
- Backport fix for SIGABRT during pacemaker-fenced shutdown
- Resolves: rhbz2166388
- Resolves: rhbz2168249

* Tue Jan 24 2023 Ken Gaillot <kgaillot@redhat.com> - 2.1.5-5
- Backport fix for remote node shutdown regression
- Resolves: rhbz2163567

* Fri Dec 9 2022 Chris Lumens <clumens@redhat.com> - 2.1.5-4
- Rebase pacemaker on upstream 2.1.5 final release
- Add support for sync points to attribute daemon
- Resolves: rhbz1463033
- Resolves: rhbz1866578
- Resolves: rhbz2122352

* Tue Dec 6 2022 Chris Lumens <clumens@redhat.com> - 2.1.5-3
- Fix errors found by covscan
- Related: rhbz2122352

* Wed Nov 23 2022 Chris Lumens <clumens@redhat.com> - 2.1.5-2
- Rebase on upstream 2.1.5-rc3 release
- Resolves: rhbz1626546
- Related: rhbz2122352

* Tue Nov 22 2022 Chris Lumens <clumens@redhat.com> - 2.1.5-1
- Rebase on upstream 2.1.5-rc2 release
- Resolves: rhbz1822125
- Resolves: rhbz2095662
- Resolves: rhbz2121852
- Resolves: rhbz2122806
- Resolves: rhbz2133497
- Resolves: rhbz2142681

* Wed Aug 10 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-5
- Fix regression in crm_resource -O
- Resolves: rhbz2118337

* Wed Jul 20 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-4
- Ensure all nodes are re-unfenced after device configuration change
- crm_resource --why now checks node health status
- Resolves: rhbz1872483
- Resolves: rhbz2065818

* Wed Jun 29 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-3
- Add support for ACL groups
- Resolves: rhbz1724310

* Tue Jun 28 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-2
- Restore crm_attribute query behavior when attribute does not exist
- Resolves: rhbz2072107

* Wed Jun 15 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-1
- Fencer should not ignore CIB updates when stonith is disabled
- Rebase pacemaker on upstream 2.1.4 final release
- Fix typo in ocf:pacemaker:HealthSMART meta-data
- Resolves: rhbz2055935
- Resolves: rhbz2072107
- Resolves: rhbz2094855

* Wed Jun 1 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.3-2
- crm_attribute works on remote node command line when hostname differs
- Rebase pacemaker on upstream 2.1.3 final release
- Resolves: rhbz1384172
- Resolves: rhbz2072107

* Wed May 18 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.3-1
- crm_resource --restart fails to restart clone instances except instance 0
- Add new multiple-active option for "stop unexpected instances"
- Unable to show metadata for "service" agents with "@" and "." in the name
- Resource ocf:pacemaker:attribute does not comply with the OCF 1.1 standard
- Allow resource meta-attribute to exempt resource from node health restrictions
- Show node health states in crm_mon
- Rebase pacemaker on upstream 2.1.3-rc2 release
- crm_mon API result does not validate against schema if fence event has exit-reason
- Resolves: rhbz1930578
- Resolves: rhbz2036815
- Resolves: rhbz2045096
- Resolves: rhbz2049722
- Resolves: rhbz2059638
- Resolves: rhbz2065812
- Resolves: rhbz2072107
- Resolves: rhbz2086230

* Wed Jan 26 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.2-4
- Fix regression in down event detection that affects remote nodes
- Resolves: rhbz2046446

* Fri Jan 21 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.2-3
- Improve display of failed actions
- Handle certain probe failures as stopped instead of failed
- Update pcmk_delay_base description in option meta-data
- Avoid crash when using clone notifications
- Retry Corosync shutdown tracking if first attempt fails
- Resolves: rhbz1470834
- Resolves: rhbz1506372
- Resolves: rhbz2027370
- Resolves: rhbz2039675
- Resolves: rhbz2042550

* Thu Dec 16 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.2-2
- Correctly get metadata for systemd agent names that end in '@'
- Use correct OCF 1.1 syntax in ocf:pacemaker:Stateful meta-data
- Fix regression in displayed times in crm_mon's fence history
- Resolves: rhbz2003151
- Resolves: rhbz2027370
- Resolves: rhbz2032027

* Tue Nov 30 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.2-1
- Allow per-host fence delays for a single fence device
- Use OCF 1.1 enum type in cluster option metadata for better validation
- crm-resource --force-* now works with LSB resources
- Allow spaces in pcmk_host_map
- ACL group names are no longer restricted to a unique XML id
- Rebase on upstream 2.1.2
- Ensure upgrades get compatible Corosync libraries
- Resolves: rhbz1082146
- Resolves: rhbz1281463
- Resolves: rhbz1346014
- Resolves: rhbz1376538
- Resolves: rhbz1384420
- Resolves: rhbz2011973
- Resolves: rhbz2027006

* Fri Aug 20 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-8
- Fix XML issue in fence_watchdog meta-data
- Resolves: rhbz1443666

* Thu Aug 12 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-7
- Fix minor issue with crm_resource error message change
- Resolves: rhbz1447918

* Tue Aug 10 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-6
- Fix watchdog agent version information
- Ensure transient attributes are cleared when multiple nodes are lost
- Resolves: rhbz1443666
- Resolves: rhbz1986998

* Fri Aug 06 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-5
- Allow configuring specific nodes to use watchdog-only sbd for fencing
- Resolves: rhbz1443666

* Fri Jul 30 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-4
- Show better error messages in crm_resource with invalid resource types
- Avoid selecting wrong device when dynamic-list fencing is used with host map
- Do not schedule probes of unmanaged resources on pending nodes
- Fix argument handling regressions in crm_attribute and wrappers
- Resolves: rhbz1447918
- Resolves: rhbz1978010
- Resolves: rhbz1982453
- Resolves: rhbz1984120

* Tue Jun 22 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-3
- crm_resource now supports XML output from resource agent actions
- Correct output for crm_simulate --show-failcounts
- Avoid remote node unfencing loop
- Resolves: rhbz1644628
- Resolves: rhbz1686426
- Resolves: rhbz1961857

* Wed Jun 9 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-2
- Rebase on upstream 2.1.0 final release
- Correct schema for crm_resource XML output
- Resolves: rhbz1935464
- Resolves: rhbz1967087

* Thu May 20 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-1
- Add crm_simulate --show-attrs and --show-failcounts options
- Retry getting fence agent meta-data after initial failure
- Add debug option for more verbose ocf:pacemaker:ping logs
- Rebase on upstream 2.1.0-rc2 release
- Support OCF Resource Agent API 1.1 standard
- Fix crm_mon regression that could cause certain agents to fail at shutdown
- Allow setting OCF check level for crm_resource --validate and --force-check
- Resolves: rhbz1686426
- Resolves: rhbz1797579
- Resolves: rhbz1843177
- Resolves: rhbz1935464
- Resolves: rhbz1936696
- Resolves: rhbz1948620
- Resolves: rhbz1955792

* Mon Feb 15 2021 Ken Gaillot <kgaillot@redhat.com> - 2.0.5-8
- Route cancellations through correct node when remote connection is moving
- Resolves: rhbz1928762

* Fri Feb 12 2021 Ken Gaillot <kgaillot@redhat.com> - 2.0.5-7
- Do not introduce regression in crm_resource --locate
- Resolves: rhbz1925681

* Wed Feb 3 2021 Ken Gaillot <kgaillot@redhat.com> - 2.0.5-6
- crm_mon --daemonize should reconnect if cluster restarts
- crm_mon should show more informative messages when cluster is starting
- crm_mon should show rest of status if fencing history is unavailable
- cibsecret now works on remote nodes (as long as name can be reached via ssh)
- Stop remote nodes correctly when connection history is later than node history
- Resolves: rhbz1466875
- Resolves: rhbz1872490
- Resolves: rhbz1880426
- Resolves: rhbz1881537
- Resolves: rhbz1898457

* Thu Jan 14 2021 Ken Gaillot <kgaillot@redhat.com> - 2.0.5-5
- Allow non-critical resources that stop rather than make another resource move
- Support crm_resource --digests option for showing operation digests
- Clean-up of all resources should work from remote nodes
- Resolves: rhbz1371576
- Resolves: rhbz1872376
- Resolves: rhbz1907726

* Wed Dec 2 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-4
- Rebase on upstream 2.0.5 release
- Make waiting to be pinged by sbd via pacemakerd-api the default
- Resolves: rhbz1885645
- Resolves: rhbz1873138

* Wed Nov 18 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.5-3
- Rebase on upstream 2.0.5-rc3 release
- Resolves: rhbz1885645

* Wed Oct 28 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.5-2
- Rebase on upstream 2.0.5-rc2 release
- Prevent ACL bypass (CVE-2020-25654)
- Resolves: rhbz1885645
- Resolves: rhbz1889582

* Tue Oct 20 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.5-1
- crm_mon --resource option to filter output by resource
- Avoid filling /dev/shm after frequent corosync errors
- Allow configurable permissions for log files
- Ensure ACL write permission always supersedes read
- Use fence device monitor timeout for starts and probes
- Allow type="integer" in rule expressions
- Avoid error messages when running crm_node inside bundles
- Avoid situation where promotion is not scheduled until next transition
- crm_mon should show more clearly when an entire group is disabled
- Rebase on upstream 2.0.5-rc1 release
- Resolves: rhbz1300597
- Resolves: rhbz1614166
- Resolves: rhbz1647136
- Resolves: rhbz1833173
- Resolves: rhbz1856015
- Resolves: rhbz1866573
- Resolves: rhbz1874391
- Resolves: rhbz1835717
- Resolves: rhbz1748139
- Resolves: rhbz1885645

* Thu Aug 20 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.4-6
- Fix cibsecret bug when node name is different from hostname
- Resolves: rhbz1870873

* Fri Jul 24 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.4-5
- Synchronize start-up and shutdown with SBD
- Resolves: rhbz1718324

* Wed Jul 22 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.4-4
- Allow crm_node -l/-p options to work from Pacemaker Remote nodes
- Correct action timeout value listed in log message
- Fix regression in crm_mon --daemonize with HTML output
- Resolves: rhbz1796824
- Resolves: rhbz1856035
- Resolves: rhbz1857728

* Thu Jun 25 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.4-3
- Allow resource and operation defaults per resource or operation type
- Rebase on upstream 2.0.4 final release
- Support on-fail="demote" and no-quorum-policy="demote" options
- Remove incorrect comment from sysconfig file
- Resolves: rhbz1628701
- Resolves: rhbz1828488
- Resolves: rhbz1837747
- Resolves: rhbz1848789

* Wed Jun 10 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.4-2
- Improve cibsecret help and clean up code per static analysis
- Resolves: rhbz1793860

* Mon Jun 8 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.4-1
- Clear leaving node's attributes if there is no DC
- Add crm_mon --node option to limit display to particular node or tagged nodes
- Add crm_mon --include/--exclude options to select what sections are shown
- priority-fencing-delay option bases delay on where resources are active
- Pending DC fencing gets 'stuck' in status display
- crm_rule can now check rule expiration when "years" is specified
- crm_mon now formats error messages better
- Support for CIB secrets is enabled
- Rebase on latest upstream Pacemaker release
- Fix regression introduced in 8.2 so crm_node -n works on remote nodes
- Avoid infinite loop when topology is removed while unfencing is in progress
- Resolves: rhbz1300604
- Resolves: rhbz1363907
- Resolves: rhbz1784601
- Resolves: rhbz1787751
- Resolves: rhbz1790591
- Resolves: rhbz1793653
- Resolves: rhbz1793860
- Resolves: rhbz1828488
- Resolves: rhbz1830535
- Resolves: rhbz1831775

* Mon Jan 27 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.3-5
- Clear leaving node's attributes if there is no DC
- Resolves: rhbz1791841

* Thu Jan 16 2020 Ken Gaillot <kgaillot@redhat.com> - 2.0.3-4
- Implement shutdown-lock feature
- Resolves: rhbz1712584

* Wed Nov 27 2019 Ken Gaillot <kgaillot@redhat.com> - 2.0.3-3
- Rebase on Pacemaker-2.0.3 final release
- Resolves: rhbz1752538

* Wed Nov 13 2019 Ken Gaillot <kgaillot@redhat.com> - 2.0.3-2
- Rebase on Pacemaker-2.0.3-rc3
- Resolves: rhbz1752538

* Thu Oct 31 2019 Ken Gaillot <kgaillot@redhat.com> - 2.0.3-1
- Rebase on Pacemaker-2.0.3-rc2
- Parse crm_mon --fence-history option correctly
- Put timeout on controller waiting for scheduler response
- Offer Pacemaker Remote option for bind address
- Calculate cluster recheck interval dynamically
- Clarify crm_resource help text
- Reduce system calls after forking a child process
- Resolves: rhbz1699978
- Resolves: rhbz1725236
- Resolves: rhbz1743377
- Resolves: rhbz1747553
- Resolves: rhbz1748805
- Resolves: rhbz1752538
- Resolves: rhbz1762025

* Mon Aug 26 2019 Ken Gaillot <kgaillot@redhat.com> - 2.0.2-3
- Make pacemaker-cli require tar and bzip2
- Resolves: rhbz#1741580

* Fri Jun 21 2019 Klaus Wenninger <kwenning@redhat.com> - 2.0.2-2
- Synchronize fence-history on fenced-restart
- Cleanup leftover pending-fence-actions when fenced is restarted
- Improve fencing of remote-nodes
- Resolves: rhbz#1708380
- Resolves: rhbz#1708378
- Resolves: rhbz#1721198
- Resolves: rhbz#1695737

* Thu Jun 6 2019 Ken Gaillot <kgaillot@redhat.com> - 2.0.2-1
- Add stonith_admin option to display XML output
- Add new crm_rule tool to check date/time rules
- List any constraints cleared by crm_resource --clear
- crm_resource --validate can now get resource parameters from command line
- Rebase on upstream version 2.0.2
- Default concurrent-fencing to true
- Resolves: rhbz#1555939
- Resolves: rhbz#1572116
- Resolves: rhbz#1631752
- Resolves: rhbz#1637020
- Resolves: rhbz#1695737
- Resolves: rhbz#1715426

* Wed May 15 2019 Ken Gaillot <kgaillot@redhat.com> - 2.0.1-5
- Add gating tests for CI
- Restore correct behavior when live migration is interrupted
- Improve clients' authentication of IPC servers (CVE-2018-16877)
- Fix use-after-free with potential information disclosure (CVE-2019-3885)
- Improve pacemakerd authentication of running subdaemons (CVE-2018-16878)
- Resolves: rhbz#1682116
- Resolves: rhbz#1684306
- Resolves: rhbz#1694558
- Resolves: rhbz#1694560
- Resolves: rhbz#1694908

* Tue Jan 29 2019 Ken Gaillot <kgaillot@redhat.com> - 2.0.1-4
- Remove duplicate fence history state listing in crm_mon XML output
- Resolves: rhbz#1667191

* Thu Jan 10 2019 Ken Gaillot <kgaillot@redhat.com> - 2.0.1-3
- Fix bundle recovery regression in 2.0.1-2
- Resolves: rhbz#1660592

* Fri Dec 14 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.1-2
- Move pacemaker-doc installed files to /usr/share/doc/pacemaker-doc
  to avoid conflict with RHEL 8 location of pacemaker subpackage docs
- Resolves: rhbz#1543494

* Thu Dec 13 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.1-1
- Rebase on upstream commit 0eb799156489376e13fb79dca47ea9160e9d4595 (Pacemaker-2.0.1-rc1)
- Follow upstream change of splitting XML schemas into separate package
- Resolves: rhbz#1543494

* Fri Nov 16 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-11
- Rebase on upstream commit efbf81b65931423b34c91cde7204a2d0a71e77e6
- Resolves: rhbz#1543494

* Fri Sep 28 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-10
- Rebase on upstream commit b67d8d0de9794e59719608d9b156b4a3c6556344
- Update spec for Python macro changes
- Resolves: rhbz#1543494
- Resolves: rhbz#1633612

* Mon Sep 17 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-9
- Rebase on upstream commit c4330b46bf1c3dcd3e367b436efb3bbf82ef51cd
- Support podman as bundle container launcher
- Ignore fence history in crm_mon when using CIB_file
- Resolves: rhbz#1543494
- Resolves: rhbz#1607898
- Resolves: rhbz#1625231

* Thu Aug 30 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-8
- Rebase on upstream commit dd6fd26f77945b9bb100d5a3134f149b27601552
- Fixes (unreleased) API regression
- Resolves: rhbz#1543494
- Resolves: rhbz#1622969

* Mon Aug 13 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-7
- Include upstream main branch commits through 975347d4
- Resolves: rhbz#1543494
- Resolves: rhbz#1602650
- Resolves: rhbz#1608369

* Mon Jul 30 2018 Florian Weimer <fweimer@redhat.com> - 2.0.0-6
- Rebuild with fixed binutils

* Mon Jul 9 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-5
- Rebase to upstream version 2.0.0 final
- Resolves: rhbz#1543494

* Wed Jun 6 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-4
- Rebase to upstream version 2.0.0-rc5
- Resolves: rhbz#1543494

* Mon Apr 30 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-2
- Rebase to upstream version 2.0.0-rc3
- Resolves: rhbz#1543494

* Tue Apr 17 2018 Ken Gaillot <kgaillot@redhat.com> - 2.0.0-1
- Rebase to upstream version 2.0.0-rc2 with later fixes
- Resolves: rhbz#1543494

* Tue Apr 17 2018 Josh Boyer <jwboyer@redhat.com> - 1.1.17-3
- Stop hard requiring nagios-plugins

* Wed Oct 18 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.17-2
- Rebuilt to fix libqb vs. ld.bfd/binutils-2.29 incompatibility making
  some CLI executables unusable under some circumstances (rhbz#1503843)

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.17-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.17-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 07 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.17-1
- Update for new upstream tarball: Pacemaker-1.1.17,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.17

* Thu Jun 22 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.17-0.1.rc4
- Update for new upstream tarball for release candidate: Pacemaker-1.1.17-rc4,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.17-rc4
- Add an imposed lower bound for glib2 BuildRequires

* Thu Jun 01 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.17-0.1.rc3
- Update for new upstream tarball for release candidate: Pacemaker-1.1.17-rc3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.17-rc3

* Wed May 24 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.17-0.1.rc2
- Update for new upstream tarball for release candidate: Pacemaker-1.1.17-rc2,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.17-rc2

* Tue May 09 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.17-0.1.rc1
- Update for new upstream tarball for release candidate: Pacemaker-1.1.17-rc1,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.17-rc1

* Mon Feb 06 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.16-2.a39ea6491.git
- Update for (slightly stabilized) snapshot beyond Pacemaker-1.1.16
  (commit a39ea6491), including:
  . prevent FTBFS with new GCC 7 (a7476dd96)
- Adapt spec file more akin to upstream version including:
  . better pre-release vs. tags logic (4581d4366)

* Fri Dec 02 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.16-1
- Update for new upstream tarball: Pacemaker-1.1.16,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.16
- Adapt spec file more akin to upstream version including:
  . clarify licensing, especially for -doc (f01f734)
  . fix pacemaker-remote upgrade (779e0e3)
  . require python >= 2.6 (31ef7f0)
  . older libqb is sufficient (based on 30fe1ce)
  . remove openssl-devel and libselinux-devel as BRs (2e05c17)
  . make systemd BR pkgconfig-driven (6285924)
  . defines instead of some globals + error suppression (625d427)
- Rectify -nagios-plugins-metadata declared license and install
  also respective license text

* Thu Nov 03 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.15-3
- Apply fix for CVE-2016-7035 (improper IPC guarding)

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.15-2.1
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Jul 07 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.15-2
- Stop building with -fstack-protector-all using the upstream patches
  overhauling toolchain hardening (Fedora natively uses
  -fstack-protector-strong so this effectively relaxed stack protection
  is the only effect as hardened flags are already used by default:
  https://fedoraproject.org/wiki/Changes/Harden_All_Packages)

* Wed Jun 22 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.15-1
- Update for new upstream tarball: Pacemaker-1.1.15,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.15
- Adapt spec file more akin to upstream version:
  . move xml schema files + PCMK-MIB.txt (81ef956), logrotate configuration
    file (ce576cf; drop it from -remote package as well), attrd_updater
    (aff80ae), the normal resource agents (1fc7287), and common directories
    under /var/lib/pacemaker (3492794) from main package under -cli
  . simplify docdir build parameter passing and drop as of now
    redundant chmod invocations (e91769e)

* Fri May 27 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.15-0.1.rc3
- Update for new upstream tarball for release candidate: Pacemaker-1.1.15-rc3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.15-rc3
- Drop fence_pcmk (incl. man page) from the package (no use where no CMAN)
- Drop license macro emulation for cases when not supported natively
  (several recent Fedora releases do not need that)

* Mon May 16 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.15-0.1.rc2
- Update for new upstream tarball for release candidate: Pacemaker-1.1.15-rc2,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.15-rc2

* Tue Apr 26 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.15-0.1.rc1
- Update for new upstream tarball for release candidate: Pacemaker-1.1.15-rc1,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.15-rc1
- Adapt spec file more akin to upstream version (also to reflect recent
  changes like ability to built explicitly without Publican-based docs)

* Thu Mar 31 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.14-2.5a6cdd1.git
- Update for currently stabilized snapshot beyond Pacemaker-1.1.14
  (commit 5a6cdd1), but restore old-style notifications to the state at
  Pacemaker-1.1.14 point release (disabled)
- Definitely get rid of Corosync v1 (Flatiron) hypothetical support
- Remove some of the spec file cruft, not required for years
  (BuildRoot, AutoReqProv, "clean" scriptlet, etc.) and adapt the file
  per https://github.com/ClusterLabs/pacemaker/pull/965

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.14-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jan 18 2016 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.14-1
- Update for new upstream tarball: Pacemaker-1.1.14,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.14
- Disable Fedora crypto policies conformance patch for now (rhbz#1179335)
- Better align specfile with the upstream version (also fix issue with
  crm_mon sysconfig file not being installed)
- Further specfile modifications:
  - drop unused gcc-c++ and repeatedly mentioned pkgconfig packages
    from BuildRequires
  - refer to python_sitearch macro first, if defined
  - tolerate license macro not being defined (e.g., for EPEL rebuilds)
- Prevent console mode not available in crm_mon due to curses library test
  fragility of configure script in hardened build environment (rhbz#1297985)

* Tue Oct 20 2015 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.13-4
- Adapt to follow Fedora crypto policies (rhbz#1179335)

* Wed Oct 14 2015 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.13-3
- Update to Pacemaker-1.1.13 post-release + patches (sync)
- Add nagios-plugins-metadata subpackage enabling support of selected
  Nagios plugins as resources recognized by Pacemaker
- Several specfile improvements: drop irrelevant stuff, rehash the
  included/excluded files + dependencies, add check scriptlet,
  reflect current packaging practice, do minor cleanups
  (mostly adopted from another spec)

* Thu Aug 20 2015 Andrew Beekhof <abeekhof@redhat.com> - 1.1.13-2
- Update for new upstream tarball: Pacemaker-1.1.13
- See included ChangeLog file or https://raw.github.com/ClusterLabs/pacemaker/main/ChangeLog for full details

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.12-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Nov 05 2014 Andrew Beekhof <abeekhof@redhat.com> - 1.1.12-2
- Address incorrect use of the dbus API for interacting with systemd

* Tue Oct 28 2014 Andrew Beekhof <abeekhof@redhat.com> - 1.1.12-1
- Update for new upstream tarball: Pacemaker-1.1.12+ (a9c8177)
- See included ChangeLog file or https://raw.github.com/ClusterLabs/pacemaker/main/ChangeLog for full details

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.11-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.11-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Feb 18 2014 Andrew Beekhof <abeekhof@redhat.com> - 1.1.11-1
- Update for new upstream tarball: Pacemaker-1.1.11 (9d39a6b)
- See included ChangeLog file or https://raw.github.com/ClusterLabs/pacemaker/main/ChangeLog for full details

* Thu Jun 20 2013 Andrew Beekhof <abeekhof@redhat.com> - 1.1.9-3
- Update to upstream 7d8acec
- See included ChangeLog file or https://raw.github.com/ClusterLabs/pacemaker/main/ChangeLog for full details

  + Feature: Turn off auto-respawning of systemd services when the cluster starts them
  + Fix: crmd: Ensure operations for cleaned up resources don't block recovery
  + Fix: logging: If SIGTRAP is sent before tracing is turned on, turn it on instead of crashing

* Mon Jun 17 2013 Andrew Beekhof <abeekhof@redhat.com> - 1.1.9-2
- Update for new upstream tarball: 781a388
- See included ChangeLog file or https://raw.github.com/ClusterLabs/pacemaker/main/ChangeLog for full details

* Wed May 12 2010 Andrew Beekhof <andrew@beekhof.net> - 1.1.2-1
- Update the tarball from the upstream 1.1.2 release
- See included ChangeLog file or https://raw.github.com/ClusterLabs/pacemaker/main/ChangeLog for full details

* Tue Jul 14 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.4-1
- Initial checkin
