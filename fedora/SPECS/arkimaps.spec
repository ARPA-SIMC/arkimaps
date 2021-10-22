%global releaseno 1
# Note: define _srcarchivename in Travis build only.
%{!?srcarchivename: %global srcarchivename %{name}-%{version}-%{releaseno}}

Name:           arkimaps
Version:        1.0
Release:        1%{?dist}
Summary:        Meteo plot generator from grib data

License:        GPLv3+
URL:            https://github.com/arpa-simc/%{name}
#Source0:        https://github.com/arpa-simc/%{name}/archive/v%{version}-%{releaseno}.tar.gz#/%{srcarchivename}.tar.gz
Source0:        https://github.com/arpa-simc/%{name}/tarball/issue76#/%{srcarchivename}.tar.gz

BuildRequires:  python3
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
Requires:       python3
Requires:       python3-Magics

%description
Meteo plot generator from grib data

%global debug_package %{nil}

%prep
#autosetup -n %{srcarchivename}
%autosetup -n ARPA-SIMC-arkimaps-917f264


%build
%py3_build


%install
rm -rf $RPM_BUILD_ROOT
%py3_install
#TODO: install arkimet-postprocessor in /usr/lib64/arkimet
#TODO: install (generate?) recipes doc


%check
#TODO: fix test data
#{__python3} setup.py test

%files
%{_bindir}/%{name}
%{python3_sitelib}/%{name}*



%changelog
* Fri Oct 22 2021 Daniele Branchini <dbranchini@arpa.emr.it>
- First build
