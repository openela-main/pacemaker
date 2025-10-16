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
%global bug_url https://issues.redhat.com/
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
%global pcmkversion 2.1.8
%global specversion 3

## Upstream commit (full commit ID, abbreviated commit ID, or tag) to build
%global commit 3980678f0372f2c7c294c01f61d63f0b2cafaad1

## Since git v2.11, the extent of abbreviation is autoscaled by default
## (used to be constant of 7), so we need to convey it for non-tags, too.
%global commit_abbrev 9


# Define conditionals so that "rpmbuild --with <feature>" and
# "rpmbuild --without <feature>" can enable and disable specific features

## Add option to enable support for stonith/external fencing agents
%bcond_with stonithd

## Add option for whether to support storing sensitive information outside CIB
%if (0%{?fedora} && 0%{?fedora} <= 33) || (0%{?rhel} && 0%{?rhel} <= 8)
%bcond_with cibsecrets
%else
%bcond_without cibsecrets
%endif

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
%if 0%{?rhel} && 0%{?rhel} > 8
%bcond_without sbd_sync
%else
%bcond_with sbd_sync
%endif

## Add option to prefix package version with "0."
## (so later "official" packages will be considered updates)
%bcond_with pre_release

## NOTE: skip --with upstart_job

## Add option to turn off hardening of libraries and daemon executables
%bcond_without hardening

## Add option to enable (or disable, on RHEL 8) links for legacy daemon names
%if 0%{?rhel} && 0%{?rhel} <= 8
%bcond_without legacy_links
%else
%bcond_with legacy_links
%endif

## Nagios source control identifiers
%global nagios_name nagios-agents-metadata
%global nagios_hash 105ab8a7b2c16b9a29cf1c1596b80136eeef332b
%global nagios_archive_github_url %{nagios_hash}#/%{nagios_name}-%{nagios_hash}.tar.gz

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
Release:       %{pcmk_release}%{?dist}
License:       GPL-2.0-or-later AND LGPL-2.1-or-later
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
Source1:       https://codeload.github.com/%{github_owner}/%{nagios_name}/tar.gz/%{nagios_archive_github_url}
Source2:       pacemaker.sysusers

# upstream commits
#Patch001:      001-xxxx.patch

Requires:      resource-agents
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}
Requires:      %{name}-cluster-libs%{?_isa} = %{version}-%{release}
Requires:      %{name}-cli = %{version}-%{release}
%if %{with stonithd}
Requires:      %{python_name}-%{name} = %{version}-%{release}
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
BuildRequires: %{python_name}-setuptools

# Pacemaker requires a minimum libqb functionality
# RHEL requires a higher version than upstream, for qb_ipcc_connect_async()
Requires:      libqb >= 2.0.3-7
BuildRequires: libqb-devel >= 2.0.3-7

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
BuildRequires: libxml2-devel >= 2.6.0
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
BuildRequires: libcmocka-devel >= 1.1.0

BuildRequires: pkgconfig(systemd)

# RH patches are created by git, so we need git to apply them
BuildRequires: git

# The RHEL 9 build root has corosync_cfg_trackstart() available, so
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

# Creation of Users / Groups
BuildRequires:  systemd-rpm-macros
%{?sysusers_requires_compat}

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
License:       GPL-2.0-or-later AND LGPL-2.1-or-later
Summary:       Command line tools for controlling Pacemaker clusters
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}
%if 0%{?supports_recommends}
Recommends:    pcmk-cluster-manager = %{version}-%{release}
# For crm_report
Requires:      tar
Requires:      bzip2
%endif
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
License:       GPL-2.0-or-later AND LGPL-2.1-or-later
Summary:       Core Pacemaker libraries
Requires(pre): %{pkgname_shadow_utils}
Requires:      %{name}-schemas = %{version}-%{release}
# sbd 1.4.0+ supports the libpe_status API for pe_working_set_t
# sbd 1.4.2+ supports startup/shutdown handshake via pacemakerd-api
# sbd 1.5.0+ supports handshake defaults to enabled in this spec
Conflicts:     sbd < 1.5.0

%description -n %{pkgname_pcmk_libs}
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{pkgname_pcmk_libs} package contains shared libraries needed for cluster
nodes and those just running the CLI tools.

%package cluster-libs
License:       GPL-2.0-or-later AND LGPL-2.1-or-later
Summary:       Cluster Libraries used by Pacemaker
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}

%description cluster-libs
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{name}-cluster-libs package contains cluster-aware shared
libraries needed for nodes that will form part of the cluster nodes.

%package -n %{python_name}-%{name}
License:       LGPL-2.1-or-later
Summary:       Python libraries for Pacemaker
Requires:      %{python_path}
Requires:      %{pkgname_pcmk_libs} = %{version}-%{release}
BuildArch:     noarch

%description -n %{python_name}-%{name}
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{python_name}-%{name} package contains a Python library that can be used
to interface with Pacemaker.

%package remote
License:       GPL-2.0-or-later AND LGPL-2.1-or-later
Summary:       Pacemaker remote executor daemon for non-cluster nodes
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}
Requires:      %{name}-cli = %{version}-%{release}
Requires:      resource-agents
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
License:       GPL-2.0-or-later AND LGPL-2.1-or-later
Summary:       Pacemaker development package
Requires:      %{pkgname_pcmk_libs}%{?_isa} = %{version}-%{release}
Requires:      %{name}-cluster-libs%{?_isa} = %{version}-%{release}
Requires:      %{pkgname_bzip2_devel}%{?_isa}
Requires:      corosync-devel%{?_isa} >= 2.0.0
Requires:      glib2-devel%{?_isa}
Requires:      libqb-devel%{?_isa}
%if %{defined pkgname_libtool_devel_arch}
Requires:      %{?pkgname_libtool_devel_arch}
%endif
Requires:      libuuid-devel%{?_isa}
Requires:      libxml2-devel%{?_isa} >= 2.6.0
Requires:      libxslt-devel%{?_isa}

%description -n %{pkgname_pcmk_libs}-devel
Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

The %{pkgname_pcmk_libs}-devel package contains headers and shared libraries
for developing tools for Pacemaker.

%package       cts
License:       GPL-2.0-or-later AND LGPL-2.1-or-later
Summary:       Test framework for cluster-related technologies like Pacemaker
Requires:      %{python_path}
Requires:      %{pkgname_pcmk_libs} = %{version}-%{release}
Requires:      %{name}-cli = %{version}-%{release}
Requires:      %{python_name}-%{name} = %{version}-%{release}
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
License:       GPL-2.0-or-later
Summary:       Schemas and upgrade stylesheets for Pacemaker
BuildArch:     noarch

%description   schemas
Schemas and upgrade stylesheets for Pacemaker

Pacemaker is an advanced, scalable High-Availability cluster resource
manager.

%package       nagios-plugins-metadata
License:       GPLv3
Summary:       Pacemaker Nagios Metadata
BuildArch:     noarch
# NOTE below are the plugins this metadata uses.
# Requires:      nagios-plugins-http
# Requires:      nagios-plugins-ldap
# Requires:      nagios-plugins-mysql
# Requires:      nagios-plugins-pgsql
# Requires:      nagios-plugins-tcp
Requires:      pcmk-cluster-manager

%description  nagios-plugins-metadata
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

# DO NOT REMOVE THE FOLLOWING LINE!
# This is necessary to ensure we use the git commit ID from the
# pacemaker-abcd1234 directory name as the latest commit ID when
# generating crm_config.h.
rm -rf .git

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

make %{_smp_mflags} V=1

pushd python
%py3_build
popd

%check
make %{_smp_mflags} check
{ cts/cts-scheduler --run load-stopped-loop \
  && cts/cts-cli \
  && touch .CHECKED
} 2>&1 | sed 's/[fF]ail/faiil/g'  # prevent false positives in rpmlint
[ -f .CHECKED ] && rm -f -- .CHECKED

%install
# skip automake-native Python byte-compilation, since RPM-native one (possibly
# distro-confined to Python-specific directories, which is currently the only
# relevant place, anyway) assures proper intrinsic alignment with wider system
# (such as with py_byte_compile macro, which is concurrent Fedora/EL specific)
make install \
  DESTDIR=%{buildroot} V=1 docdir=%{pcmk_docdir} \
  %{?_python_bytecompile_extra:%{?py_byte_compile:am__py_compile=true}}

pushd python
%py3_install
popd

mkdir -p %{buildroot}%{_datadir}/pacemaker/nagios/plugins-metadata
for file in $(find %{nagios_name}-%{nagios_hash}/metadata -type f); do
    install -m 644 $file %{buildroot}%{_datadir}/pacemaker/nagios/plugins-metadata
done


mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/lib/rpm-state/%{name}

%if %{with nls}
%find_lang %{name}
%endif

# Don't package libtool archives
find %{buildroot} -name '*.la' -type f -print0 | xargs -0 rm -f

# Do not package these either on CentOS Stream
rm -f %{buildroot}/%{_sbindir}/fence_legacy
rm -f %{buildroot}/%{_mandir}/man8/fence_legacy.*

install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysusersdir}/pacemaker.conf

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
%systemd_post pacemaker.service

%preun
%systemd_preun pacemaker.service

%postun
%systemd_postun_with_restart pacemaker.service

%pre remote
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

%post remote
%systemd_post pacemaker_remote.service

%preun remote
%systemd_preun pacemaker_remote.service

%postun remote
# This next line is a no-op, because we stopped the service earlier, but
# we leave it here because it allows us to revert to the standard behavior
# in the future if desired
%systemd_postun_with_restart pacemaker_remote.service
# Explicitly take care of removing the flag-file(s) upon final removal
if [ "$1" -eq 0 ] ; then
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/restart_pacemaker_remote
fi

%posttrans remote
if [ -e %{_localstatedir}/lib/rpm-state/%{name}/restart_pacemaker_remote ] ; then
    systemctl start pacemaker_remote >/dev/null 2>&1
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/restart_pacemaker_remote
fi

%post cli
%systemd_post crm_mon.service
if [ "$1" -eq 2 ]; then
    # Package upgrade, not initial install:
    # Move any pre-2.0 logs to new location to ensure they get rotated
    { mv -fbS.rpmsave %{_var}/log/pacemaker.log* %{_var}/log/pacemaker \
      || mv -f %{_var}/log/pacemaker.log* %{_var}/log/pacemaker
    } >/dev/null 2>/dev/null || :
fi

%preun cli
%systemd_preun crm_mon.service

%postun cli
%systemd_postun_with_restart crm_mon.service

%pre -n %{pkgname_pcmk_libs}
%sysusers_create_compat %{SOURCE2}
exit 0

%ldconfig_scriptlets -n %{pkgname_pcmk_libs}
%ldconfig_scriptlets cluster-libs

%files
###########################################################
%config(noreplace) %{_sysconfdir}/sysconfig/pacemaker
%{_sbindir}/pacemakerd

%{_unitdir}/pacemaker.service

%exclude %{_datadir}/pacemaker/nagios/plugins-metadata/*

%exclude %{_libexecdir}/pacemaker/cts-log-watcher
%exclude %{_libexecdir}/pacemaker/cts-support
%exclude %{_sbindir}/pacemaker-remoted
%exclude %{_sbindir}/pacemaker_remoted
%{_libexecdir}/pacemaker/*

%if %{with stonithd}
%{_sbindir}/fence_legacy
%endif
%{_sbindir}/fence_watchdog

%doc %{_mandir}/man7/pacemaker-based.*
%doc %{_mandir}/man7/pacemaker-controld.*
%doc %{_mandir}/man7/pacemaker-schedulerd.*
%doc %{_mandir}/man7/pacemaker-fenced.*
%doc %{_mandir}/man7/ocf_pacemaker_controld.*
%doc %{_mandir}/man7/ocf_pacemaker_o2cb.*
%doc %{_mandir}/man7/ocf_pacemaker_remote.*
%if %{with stonithd}
%doc %{_mandir}/man8/fence_legacy.*
%endif
%doc %{_mandir}/man8/fence_watchdog.*
%doc %{_mandir}/man8/pacemakerd.*

%doc %{_datadir}/pacemaker/alerts

%license licenses/GPLv2
%doc COPYING
%doc ChangeLog

%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker/cib
%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker/pengine
%{ocf_root}/resource.d/pacemaker/controld
%{ocf_root}/resource.d/pacemaker/o2cb
%{ocf_root}/resource.d/pacemaker/remote

%files cli
%dir %attr (750, root, %{gname}) %{_sysconfdir}/pacemaker
%config(noreplace) %{_sysconfdir}/logrotate.d/pacemaker
%config(noreplace) %{_sysconfdir}/sysconfig/crm_mon

%{_unitdir}/crm_mon.service

%{_sbindir}/attrd_updater
%{_sbindir}/cibadmin
%if %{with cibsecrets}
%{_sbindir}/cibsecret
%endif
%{_sbindir}/crm_attribute
%{_sbindir}/crm_diff
%{_sbindir}/crm_error
%{_sbindir}/crm_failcount
%{_sbindir}/crm_master
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
%exclude %{ocf_root}/resource.d/pacemaker/o2cb
%exclude %{ocf_root}/resource.d/pacemaker/remote

%dir %{ocf_root}
%dir %{ocf_root}/resource.d
%{ocf_root}/resource.d/pacemaker

%doc %{_mandir}/man7/*pacemaker*
%exclude %{_mandir}/man7/pacemaker-based.*
%exclude %{_mandir}/man7/pacemaker-controld.*
%exclude %{_mandir}/man7/pacemaker-schedulerd.*
%exclude %{_mandir}/man7/pacemaker-fenced.*
%exclude %{_mandir}/man7/ocf_pacemaker_controld.*
%exclude %{_mandir}/man7/ocf_pacemaker_o2cb.*
%exclude %{_mandir}/man7/ocf_pacemaker_remote.*
%doc %{_mandir}/man8/crm*.8.gz
%doc %{_mandir}/man8/attrd_updater.*
%doc %{_mandir}/man8/cibadmin.*
%if %{with cibsecrets}
    %doc %{_mandir}/man8/cibsecret.*
%endif
%doc %{_mandir}/man8/iso8601.*
%doc %{_mandir}/man8/stonith_admin.*

%license licenses/GPLv2
%doc COPYING
%doc ChangeLog

%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker
%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker/blackbox
%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pacemaker/cores
%dir %attr (770, %{uname}, %{gname}) %{_var}/log/pacemaker
%dir %attr (770, %{uname}, %{gname}) %{_var}/log/pacemaker/bundles

%files -n %{pkgname_pcmk_libs} %{?with_nls:-f %{name}.lang}
%{_sysusersdir}/pacemaker.conf
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

%files -n %{python_name}-%{name}
%{python3_sitelib}/pacemaker/
%{python3_sitelib}/pacemaker-*.egg-info
%exclude %{python3_sitelib}/pacemaker/_cts/
%license licenses/LGPLv2.1
%doc COPYING
%doc ChangeLog

%files remote
%config(noreplace) %{_sysconfdir}/sysconfig/pacemaker
# state directory is shared between the subpackets
# let rpm take care of removing it once it isn't
# referenced anymore and empty
%ghost %dir %{_localstatedir}/lib/rpm-state/%{name}
%{_unitdir}/pacemaker_remote.service

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
%{python3_sitelib}/pacemaker/_cts/
%{_datadir}/pacemaker/tests

%{_libexecdir}/pacemaker/cts-log-watcher
%{_libexecdir}/pacemaker/cts-support

%license licenses/GPLv2
%doc COPYING
%doc ChangeLog

%files -n %{pkgname_pcmk_libs}-devel
%{_includedir}/pacemaker
%{_libdir}/libcib.so
%{_libdir}/liblrmd.so
%{_libdir}/libcrmservice.so
%{_libdir}/libcrmcommon.so
%{_libdir}/libpe_status.so
%{_libdir}/libpe_rules.so
%{_libdir}/libpacemaker.so
%{_libdir}/libstonithd.so
%{_libdir}/libcrmcluster.so
%{_libdir}/pkgconfig/*pacemaker*.pc
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
%dir %{_datadir}/pacemaker/nagios
%dir %{_datadir}/pacemaker/nagios/plugins-metadata
%attr(0644,root,root) %{_datadir}/pacemaker/nagios/plugins-metadata/*
%license %{nagios_name}-%{nagios_hash}/COPYING

%changelog
* Fri Aug 9 2024 Chris Lumens <clumens@redhat.com> - 2.1.8-3
- Rebase on upstream 2.1.8 final release
- Resolves: RHEL-38540

* Wed Jul 17 2024 Chris Lumens <clumens@redhat.com> - 2.1.8-2
- Rebase on upstream 2.1.8-rc4 release
- Add ability to immediately shutdown system with PCMK_panic_action=
- Fix a memory leak in the attribute daemon
- Add ability to list options and parameters as parseable metadata
- crm_verify now reports invalid fence level indexes
- Fix an error in node ID handling in `crm_node -i`
- Fix regression in attrd_updater output
- Resolves: RHEL-39057
- Resolves: RHEL-40117
- Resolves: RHEL-23401
- Resolves: RHEL-2996
- Resolves: RHEL-47249
- Resolves: RHEL-45935

* Wed May 22 2024 Chris Lumens <clumens@redhat.com> - 2.1.8-1
- Rebase on upstream 2.1.8-rc1 release
- Fix a typo in the help output of pacemaker-fenced
- Fix escaping characters in XML attribute output
- Resolves: RHEL-25819
- Resolves: RHEL-30822

* Thu Mar 21 2024 Chris Lumens <clumens@redhat.com> - 2.1.7-5
- Fix upgrading to this package on multilib systems
- Resolves: RHEL-28999

* Wed Jan 31 2024 Chris Lumens <clumens@redhat.com> - 2.1.7-4
- Properly validate attribute set type in pacemaker-attrd
- Fix `crm_attribute -t nodes --node localhost`
- Resolves: RHEL-13216
- Resolves: RHEL-17225
- Resolves: RHEL-23498

* Tue Jan 16 2024 Chris Lumens <clumens@redhat.com> - 2.1.7-3
- Rebase on upstream 2.1.7 final release
- Fix documentation for Pacemaker Remote schema transfers
- Do not check CIB feature set version when CIB_file is set
- Consolidate attrd cache handling
- Avoid duplicating option metadata across daemons
- Related: RHEL-7665
- Related: RHEL-13216
- Resolves: RHEL-7702

* Wed Dec 13 2023 Chris Lumens <clumens@redhat.com> - 2.1.7-2
- Rebase on upstream 2.1.7-rc4 release
- Use systemd-sysusers to create user/group
- Pacemaker Remote nodes can validate against later schema versions
- Related: RHEL-17225
- Resolves: RHEL-7665

* Wed Nov 22 2023 Chris Lumens <clumens@redhat.com> - 2.1.7-1
- Rebase on upstream 2.1.7-rc2 release
- Resolves: RHEL-7682
- Related: RHEL-17225

* Tue Oct 31 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-10.1
- Revert the rest of the attrd shutdown race condition fix
- Related: RHEL-14044

* Thu Oct 19 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-10
- Avoid an error if the elected attrd is on a node that is shutting down
- Resolves: RHEL-14044

* Mon Aug 28 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-9
- Fix an additional shutdown race between attrd and the controller
- Related: rhbz2228933

* Tue Aug 8 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-8
- Fix attrd race condition when shutting down
- Resolves: rhbz2228933

* Thu Jul 27 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-7
- Wait for a reply from various controller commands
- Resolves: rhbz2221084
- Related: rhbz2189301

* Mon Jul 24 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-6
- Apply dampening when creating attributes with attrd_updater -U
- Resolves: rhbz2224051
- Related: rhbz2189301

* Wed Jul 19 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-5
- Clone instances should not shuffle unnecessarily
- Fix a bug in clone resource description display
- Resolves: rhbz2222055
- Related: rhbz2189301

* Fri Jun 30 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-4
- Fix moving groups when there's a constraint for a single group member
- Resolves: rhbz2218218
- Resolves: rhbz2189301

* Wed Jun 21 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-3
- Support start state for Pacemaker Remote nodes
- Related: rhbz2182482

* Fri May 26 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-2
- Rebase pacemaker on upstream 2.1.6 final release
- Related: rhbz2182482

* Tue May 23 2023 Chris Lumens <clumens@redhat.com> - 2.1.6-1
- Rebase on upstream 2.1.6-rc2 release
- Resolves: rhbz2182482

* Wed May 17 2023 Klaus Wenninger <kwenning@redhat.com> - 2.1.5-9
- Rebuild with incremented release to allow a safe upgrade from
  c8s/rhel-8
- Related: rhbz2187424

* Fri May 5 2023 Klaus Wenninger <kwenning@redhat.com> - 2.1.5-8
- Fix overall timeout calculation if watchdog and another fencing
  device share a topology level
- Resolves: rhbz2187424

* Wed Feb 22 2023 Chris Lumens <clumens@redhat.com> - 2.1.5-7
- Additional fixes for SIGABRT during pacemaker-fenced shutdown
- Backport fix for attrd_updater -QA not displaying all nodes
- Related: rhbz2166967
- Resolves: rhbz2169829

* Thu Feb 9 2023 Chris Lumens <clumens@redhat.com> - 2.1.5-6
- Backport fix for migration history cleanup causing resource recovery
- Backport fix for SIGABRT during pacemaker-fenced shutdown
- Resolves: rhbz2166393
- Resolves: rhbz2166967

* Tue Jan 24 2023 Ken Gaillot <kgaillot@redhat.com> - 2.1.5-5
- Backport fix for remote node shutdown regression
- Resolves: rhbz2163450

* Mon Dec 12 2022 Chris Lumens <clumens@redhat.com> - 2.1.5-4
- Rebase pacemaker on upstream 2.1.5 final release
- Add support for sync points to attribute daemon
- Resolves: rhbz2122353

* Tue Dec 06 2022 Chris Lumens <clumens@redhat.com> - 2.1.5-3
- Fix errors found by covscan
- Related: rhbz2122353

* Wed Nov 23 2022 Chris Lumens <clumens@redhat.com> - 2.1.5-2
- Rebase on upstream 2.1.5-rc3 release
- Related: rhbz2122353

* Tue Nov 15 2022 Chris Lumens <clumens@redhat.com> - 2.1.5-1
- Rebase on upstream 2.1.5-rc2 release
- Resolves: rhbz2123727
- Resolves: rhbz2125337
- Resolves: rhbz2125344
- Resolves: rhbz2133546
- Resolves: rhbz2142683

* Wed Aug 10 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-5
- Fix regression in crm_resource -O
- Resolves: rhbz2089353

* Wed Jul 20 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-3
- stonith_admin --validate works again
- Resolves: rhbz2102292

* Tue Jun 28 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-2
- Restore crm_attribute query behavior when attribute does not exist
- Resolves: rhbz2099331

* Wed Jun 15 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.4-1
- Rebase pacemaker on upstream 2.1.4 final release
- Resolves: rhbz2072108

* Thu Jun 2 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.3-2
- Rebase pacemaker on upstream 2.1.3 final release
- Resolves: rhbz2072108

* Thu May 19 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.3-1
- Unable to show metadata for "service" agents with "@" and "." in the name
- Resource ocf:pacemaker:attribute does not comply with the OCF 1.1 standard
- Pacemaker does not convert & to &amp; when generating metadata for non-ocf agents
- Rebase pacemaker on upstream 2.1.3 release
- Resolves: rhbz2045110
- Resolves: rhbz2049720
- Resolves: rhbz2050259
- Resolves: rhbz2072108

* Wed Jan 26 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.2-4
- Fix regression in down event detection that affects remote nodes
- Resolves: rhbz2039399

* Mon Jan 24 2022 Ken Gaillot <kgaillot@redhat.com> - 2.1.2-3
- Detect an unresponsive subdaemon
- Handle certain probe failures as stopped instead of failed
- Update pcmk_delay_base option meta-data
- Avoid crash when using clone notifications
- Retry Corosync shutdown tracking if first attempt fails
- Improve display of failed actions
- Resolves: rhbz1707851
- Resolves: rhbz2039982
- Resolves: rhbz2032032
- Resolves: rhbz2040443
- Resolves: rhbz2042367
- Resolves: rhbz2042546

* Thu Dec 16 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.2-2
- Correctly get metadata for systemd agent names that end in '@'
- Use correct OCF 1.1 syntax in ocf:pacemaker:Stateful meta-data
- Fix regression in displayed times in crm_mon's fence history
- Resolves: rhbz2032031
- Resolves: rhbz2032032
- Resolves: rhbz2031765

* Tue Nov 30 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.2-1
- Rebase on upstream 2.1.2
- Resolves: rhbz2011974

* Fri Aug 20 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-11
- Fix XML issue with fence_watchdog meta-data
- Resolves: rhbz1988568

* Thu Aug 12 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-10
- Fix minor issue with crm_resource error message change
- Resolves: rhbz1983196

* Wed Aug 11 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-9
- Fix watchdog agent version information
- Ensure transient attributes are cleared when multiple nodes are lost
- Resolves: rhbz1988568
- Resolves: rhbz1989292

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 2.1.0-7.1
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Aug 06 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-7
- Allow configuring specific nodes to use watchdog-only sbd for fencing
- Resolves: rhbz1988568

* Fri Jul 30 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-6
- Avoid selecting wrong device when dynamic-list fencing is used with host map
- Show better error messages in crm_resource with invalid resource types
- Do not schedule probes of unmanaged resources on pending nodes
- Fix argument handling regressions in crm_attribute and wrappers
- Resolves: rhbz1978013
- Resolves: rhbz1983196
- Resolves: rhbz1983197
- Resolves: rhbz1984130

* Wed Jun 30 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-5
- crm_resource now supports XML output from resource agent actions
- Correct output for crm_simulate --show-failcounts
- Avoid remote node unfencing loop
- Resolves: rhbz1975380
- Resolves: rhbz1975386
- Resolves: rhbz1975388

* Thu Jun 10 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-4
- Rebase on upstream 2.1.0 final release
- Resolves: rhbz1936023

* Tue Jun 1 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-3
- Rebase on upstream 2.1.0-rc3 release
- Resolves: rhbz1936023

* Wed May 26 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-2
- Include recent post-rc2 fixes with rebase
- Resolves: rhbz1936023

* Wed May 12 2021 Ken Gaillot <kgaillot@redhat.com> - 2.1.0-1
- Default resource-stickiness to 1 in newly created clusters
- Rebase on upstream 2.1.0-rc2 release
- Resolves: rhbz1850145
- Resolves: rhbz1936023

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 2.0.5-10.2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.5-10.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Dec 7 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-10
- Conflicts of doc package introduced to fix upgrade/downgrade
  issues needs to be independent from arch

* Fri Dec 4 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-9
- Make doc-package conflict with wrong version of libs
  to fix upgrade/downgrade issues

* Fri Dec 4 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-8
- Update for new upstream release tarball: Pacemaker-2.0.5
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.5

* Wed Nov 18 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-0.7.rc3
- a little more syncing with upstream spec-file

* Tue Nov 17 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-0.6.rc3
- Update for new upstream tarball for release candidate: Pacemaker-2.0.5-rc3
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.5-rc3
- Corosync in Fedora now provides corosync-devel as well in isa-flavor

* Sun Nov 1 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-0.5.rc2
- remove no more working dist.rpmdeplint from gating

* Fri Oct 30 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-0.4.rc2
- never use spec-variables in changelog
- replace dist.depcheck by dist.rpmdeplint
- do gate stable as well to be effective on rawhide

* Fri Oct 30 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-0.3.rc2
- revert dependency corosync-devel back to corosynclib-devel as long
  as corosynclib-devel-package doesn't provide corosync-devel(isa)
  we would need for pacemaker-libs-devel to require
- enable some basic gating-tests
- re-add building documentation using publican to everything but ELN
- rename doc-dir for ELN

* Wed Oct 28 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-0.2.rc2
- Update for new upstream tarball for release candidate: Pacemaker-2.0.5-rc2,
  includes fix for CVE-2020-25654
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.5-rc2

* Thu Oct 22 2020 Klaus Wenninger <kwenning@redhat.com> - 2.0.5-0.1.rc1
- Update for new upstream tarball for release candidate: Pacemaker-2.0.5-rc1,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.5-rc1
- Disable building of documentation - as not to pull in publican
- Remove dependencies to nagios-plugins from metadata-package
- some sync with structure of upstream spec-file
- removed some legacy conditionals
- added with-cibsecrets

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.4-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jun 16 2020 Chris Lumens <clumens@redhat.com> - 2.0.4-1
- Update for new upstream tarball: Pacemaker-2.0.4
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.4

* Thu Jun 04 2020 Chris Lumens <clumens@redhat.com> - 2.0.4-0.1.rc3
- Update for new upstream tarball for release candidate: Pacemaker-2.0.4-rc3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.4-rc3

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 2.0.4-0.2.rc1.1
- Rebuilt for Python 3.9

* Wed May 13 2020 Chris Lumens <clumens@redhat.com> - 2.0.4-0.2.rc1
- Rebuilt for libqb 2.0.

* Mon May 04 2020 Chris Lumens <clumens@redhat.com> - 2.0.4-0.1.rc1
- Update for new upstream tarball for release candidate: Pacemaker-2.0.4-rc1,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.4-rc1

* Fri Mar 06 2020 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.3-4
- return back to building also for s390x architecture, previous obstacle
  was identified and interim fix (way to build along with one actual bugfix
  as raised along) applied (RHBZ#1799842)

* Wed Mar 04 2020 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.3-3
- include upstream fix for buildability with GCC 10 (PR #1968)
- omit s390x architecture for now, compilation would fail at this time

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Tue Nov 26 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.3-1
- Update for new upstream tarball: Pacemaker-2.0.3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.3
  (functionally identical to 2.0.3-rc3, new build mostly to fix a memory
  leak & allow for easy glibc ~2.31+ friendly switch away from ftime(3))
- Fix unability to build with Inkscape 1.0 beta (and possibly beyond)

* Thu Nov 14 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.3-0.1.rc3
- Update for new upstream tarball for release candidate: Pacemaker-2.0.3-rc3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.3-rc3
- Fix failure to build due to using obsolete ftime(3)

* Wed Nov 06 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.3-0.1.rc2
- Update for new upstream tarball for release candidate: Pacemaker-2.0.3-rc2,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.3-rc2

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 2.0.2-1.3
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 2.0.2-1.2
- Rebuilt for Python 3.8

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.2-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jun 07 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.2-1
- Update for new upstream tarball: Pacemaker-2.0.2,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.2
  (functionally identical to 2.0.2-rc3, new build mostly to match expectations)

* Fri May 31 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.2-0.1.rc3
- Update for new upstream tarball for release candidate: Pacemaker-2.0.2-rc3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.2-rc3
- Adapt spec file more akin to upstream version including:
  . /usr/share/pacemaker now owned by -schemas, its "api" subdirectory
    is not carried redundantly in -cli anymore (f05eb7eec)

* Tue May 28 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.2-0.1.rc2
- Update for new upstream tarball for release candidate: Pacemaker-2.0.2-rc2,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.2-rc2

* Thu Apr 25 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.2-0.1.rc1
- Update for new upstream tarball for release candidate: Pacemaker-2.0.2-rc1,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.2-rc1
- Customize (as allowed now) exhibited downstream-specific bug reporting URL
- Adapt spec file more akin to upstream version including:
  . sbd ABI compatible version enforcement (37ad2bea1)

* Wed Apr 17 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.1-2
- Apply fixes for security issues:
  . CVE-2019-3885 (use-after-free with potential information disclosure)
  . CVE-2018-16877 (insufficient local IPC client-server authentication)
  . CVE-2018-16878 (insufficient verification inflicted preference of
                    uncontrolled processes)

* Tue Mar 05 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.1-1
- Update for new upstream tarball: Pacemaker-2.0.1,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.1

* Thu Feb 28 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.1-0.4.rc5
- Update for new upstream tarball for release candidate: Pacemaker-2.0.1-rc5,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.1-rc5
- Reflect that cts-scheduler tests are fully compatible with whatever recent
  glib version that gets to be used in run-time (incl. buildroot tests) again

* Mon Feb 04 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.1-0.3.rc4
- Update for new upstream tarball for release candidate: Pacemaker-2.0.1-rc4,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.1-rc4
- Conditionally disable "hash affected tests" in cts-scheduler (-cts package),
  since it is unlikely glib v2.59.0+ present in the buildroot will be
  artificially downgraded post-deployment

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.1-0.2.rc3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Jan 22 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.1-0.2.rc3
- Fix buildability with GCC 9 (PR #1681)
- Apply minor crm_mon XML output fix (PR #1678)

* Sun Jan 20 2019 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.1-0.1.rc3
- Update for new upstream tarball for release candidate: Pacemaker-2.0.1-rc3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.1-rc3
- Adapt spec file more akin to upstream version including:
  . split a dedicated, noarch -schemas package (c6a87bd86)
  . make static dependencies on inner libraries arch-specific (14bfff68e)
  . weak co-dependence of -cli with -remote & pacemaker proper (73e2c94a3)
  . declare bundled gnulib (d57aa84c1)
- Move stonith_admin to -cli where it belongs, since it doesn't require
  -cluster-libs (considered by upstream)
- Apply patches to restore basic buildability (still without much run-time
  reproducibility guarantees compared to what's been customary prior to glib
  v2.59.0+ that may now get run-time linked upon its fresh installation/update,
  but this applies also to whatever older version of pacemaker, and wasn't
  discovered until now; cf. https://github.com/ClusterLabs/pacemaker/pull/1677)

* Thu Aug 23 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-4
- Sanitize/generalize approach to Python byte-compilation, so that also
  out-of-Python-path *.py files (%%{_datadir}/pacemaker/tests/cts/CTSlab.py
  in particular) get the expected treatment now

* Wed Aug 15 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-3
- Fix Python 3.7 incompatibility (otherwise missed in bytecompilation phase,
  see rhbz#1616219)

* Thu Aug 09 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-2
- Include fix for "cibadmin --upgrade" related issues (rhbz#1611631)
- Adapt spec file more akin to upstream version including:
  . assuredly skip servicelog-related binaries even when build-time
    prerequisites are present on suitable systems (9f24448d8)

* Mon Jul 09 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-1
- Update for new upstream tarball: Pacemaker-2.0.0,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.0

* Mon Jul 02 2018 Miro Hrončok <mhroncok@redhat.com> - 2.0.0-0.1.rc6.1
- Rebuilt for Python 3.7

* Thu Jun 28 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-0.1.rc6
- Update for new upstream tarball for release candidate: Pacemaker-2.0.0-rc6,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.0-rc6
- Adapt spec file more akin to upstream version including:
  . new procps-ng and psmisc dependencies with -cli and -cts, for e.g.
    "ps/sysctl/uptime" and "killall" invocations, respectively (a4ad8183a)
  . move crm_node to -cli (a94a1ed58)

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 2.0.0-0.1.rc5.1
- Rebuilt for Python 3.7

* Fri Jun 01 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-0.1.rc5
- Update for new upstream tarball for release candidate: Pacemaker-2.0.0-rc5,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.0-rc5
- Adapt spec file more akin to upstream version including:
  . new coreutils dependency for "post" scriptlet of -cli,
    for "mv" invocation (c2b16165d)

* Wed May 16 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-0.1.rc4
- Update for new upstream tarball for release candidate: Pacemaker-2.0.0-rc4,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.0-rc4
  . as a special note, previous release candidate, rc3, had rolling upgrades
    broken, and if that is required, that particular release shall be
    skipped in the upgrade path altogether
- Adapt spec file more akin to upstream version including:
  . as part of the update process, possibly move old log files as implicitly
    used prior to 2.0 so there's a (limited) continuity with the new implicit
    location, preventing clutter and confusion (ce2e74c99, c2b16165d)
  . move cts-exec-helper from -cli under main package (a2dc2a67e)
  . -cts backed with new helpers and, tangentially, dummy systemd service
    file transiently generated on-demand again (fa2d43445, d52b001b1)

* Wed May 02 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-0.1.rc3
- Update for new upstream tarball for release candidate: Pacemaker-2.0.0-rc3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.0-rc3
  . IMPORTANT: this release candidate, rc3, has rolling upgrades broken,
               and if that is required, this particular release shall be
               skipped in the upgrade path altogether
- Adapt spec file more akin to upstream version including:
  . new --without legacy_links conditional (c8a7e5225)
  . reflect name change of the auxiliary daemons
    (e4f4a0d64, db5536e40, e2fdc2bac + 9ecbfea1c, 038c465e2 + ed8ce4055a)
  . new dummy systemd service for -cts (bf0a22812)
  . honor system-wide crypto policies once for all, via package-build-time
    configurable "pcmk_gnutls_priorities" defaulting to @SYSTEM as prescribed
    in https://fedoraproject.org/wiki/Packaging:CryptoPolicies
    (based on b3dfce1d3)
- Adapt spec file akin to current packaging guidelines including:
  . make -nagios-plugins-metadata package noarch

* Mon Apr 09 2018 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 2.0.0-0.1.rc2
- Update for new upstream tarball for release candidate: Pacemaker-2.0.0-rc2,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-2.0.0-rc2
- Adapt spec file more akin to upstream version including:
  . out-of-tree change from 1.1.18-2 build got subsumed (508ad52e7)
  . %%{_sysconfdir}/pacemaker path got properly owned
    (-cli package; f6e3ab98d)
  . -libs package started to properly declare Requires(pre): shadow-utils
    (293fcc1e8 + b3d49d210)
  . some build conditionals and dependencies dropped for no longer
    (snmp, esmtp; f24bdc6f2 and 1f7374884, respectively) or never
    being relevant (~bison, byacc, flex; 61aef8af4)
  . some dependencies were constrained with new or higher lower bounds:
    corosync needs to be of version 2+ unconditionally (ccd58fe29),
    ditto some others components (~GLib, 1ac2e7cbb), plus both 2 and 3
    versions of Python are now (comprehensively for the auxiliary
    functionality where used) supported upstream with the latter being
    a better fit (453355f8f)
  . package descriptions got to reflect the drop of legacy low-level
    cluster infrastructures (55ab749bf)
- Adapt spec file akin to current packaging guidelines including:
  . drop some redundant/futile expressions (defattr, "-n %%{name}-libs"
    instead of plain "libs", "timezone hack"), add some notes for future
  . make -cts and -doc packages noarch (former enabled with 088a5e7d4)
  . simplify "systemd_requires" macro invocation, and relax it to
    "systemd_ordering" for -remote package where possible so as not
    to drag systemd into a lightweight system setup (e.g. container)
    needlessly
  . adjust, in a compatible way, common ldconfig invocation with
    post{,un} scriptlets
    (https://fedoraproject.org/wiki/Changes/Removing_ldconfig_scriptlets)
  . drop some more unuseful conditionals (upstart_job)
- Apply some regression fixes on top as patches (PR #1457, #1459)

* Wed Feb 21 2018 Iryna Shcherbina <ishcherb@redhat.com> - 1.1.18-2.2
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.18-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Nov 16 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.18-2
- Make sure neither of pacemaker{,_remoted} is process-limited

* Wed Nov 15 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.18-1
- Update for new upstream tarball: Pacemaker-1.1.18,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.18
- Make -libs-devel package dependencies arch-qualified
  (-cts hasn't been switched at this time, pending further cleanup)

* Fri Nov 03 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.18-0.1.rc4
- Update for new upstream tarball for release candidate: Pacemaker-1.1.18-rc4,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.18-rc4

* Thu Oct 26 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.18-0.1.rc3
- Update for new upstream tarball for release candidate: Pacemaker-1.1.18-rc3,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.18-rc3

* Mon Oct 16 2017 Jan Pokorný <jpokorny+rpm-pacemaker@redhat.com> - 1.1.18-0.1.rc2
- Update for new upstream tarball for release candidate: Pacemaker-1.1.18-rc2,
  for full details, see included ChangeLog file or
  https://github.com/ClusterLabs/pacemaker/releases/tag/Pacemaker-1.1.18-rc2
- Fix check scriptlet so as to work properly also with rpm<4.14 (not strictly
  required since: https://github.com/rpm-software-management/rpm/pull/249,
  but pragmatically follow the upstream)

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
