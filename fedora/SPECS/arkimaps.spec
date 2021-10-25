%global releaseno 1
# Note: define _srcarchivename in Travis build only.
%{!?srcarchivename: %global srcarchivename %{name}-%{version}-%{releaseno}}

Name:           arkimaps
Version:        0.4
Release:        %{releaseno}%{dist}
Summary:        Meteo plot generator from grib data

License:        GPLv3+
URL:            https://github.com/arpa-simc/%{name}
Source0:        https://github.com/arpa-simc/%{name}/archive/v%{version}-%{releaseno}.tar.gz#/%{srcarchivename}.tar.gz
Source1:        https://github.com/ARPA-SIMC/arkimaps/files/5844942/testsuite.tar.gz

BuildRequires:  python3
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
Requires:       python3
Requires:       python3-Magics

%description
Meteo plot generator from grib data

%global debug_package %{nil}

%prep
%autosetup -n %{srcarchivename}

%build
%py3_build


%install
[ "%{buildroot}" != / ] && rm -rf "%{buildroot}"
%py3_install

#install arkimet-postprocessor in /usr/lib64/arkimet
install -D -m0755 arkimet-postprocessor %{buildroot}%{_libdir}/arkimet/%{name}

#generate recipes doc
mkdir -p %{buildroot}%{_docdir}/%{name}/
%{__python3} arkimaps document-recipes --destdir %{buildroot}%{_docdir}/%{name}/

%check
#TODO: fix test data
mkdir testdata
tar xf %SOURCE1 -C testdata/
%{__python3} setup.py test

%files
%{_bindir}/%{name}
%{python3_sitelib}/%{name}*
%doc %{_docdir}/%{name}/*

%package -n arkimet-postprocess-%{name}
Summary: arkimaps postprocessor for arkimet
BuildArch: noarch
Requires: arkimet
Requires: %{name}

%description -n arkimet-postprocess-%{name}
Meteo plot generator from grib data postprocessor for arkimet

%files -n arkimet-postprocess-%{name}
%defattr(-,root,root,-)
%{_libdir}/arkimet/%{name}

%changelog
* Mon Oct 25 2021 Daniele Branchini <dbranchini@arpae.it> - 0.4-1
- First build
