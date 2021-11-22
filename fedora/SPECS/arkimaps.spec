%global releaseno 1
# Note: define _srcarchivename in Travis build only.
%{!?srcarchivename: %global srcarchivename %{name}-%{version}-%{releaseno}}

Name:           arkimaps
Version:        0.5
Release:        %{releaseno}%{dist}
Summary:        Meteo plot generator from grib data

License:        GPLv3+
URL:            https://github.com/ARPA-SIMC/%{name}
Source0:        https://github.com/ARPA-SIMC/%{name}/archive/v%{version}-%{releaseno}.tar.gz#/%{srcarchivename}.tar.gz

BuildRequires:  python3
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
BuildRequires:  python3-pyyaml

# for tests
BuildRequires:  arkimet
BuildRequires:  python3-Magics
BuildRequires:  libsim
# for documenting recipes
BuildRequires:  python3-eccodes

Requires:       python3
Requires:       python3-Magics
Requires:       python3-eccodes


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

#install recipes in /usr/share/arkimaps/
mkdir -p %{buildroot}%{_datadir}/%{name}/recipes
install -D -m664 recipes/*.yaml %{buildroot}%{_datadir}/%{name}/recipes/
mkdir -p %{buildroot}%{_datadir}/%{name}/recipes/flavours
install -D -m664 recipes/flavours/*.yaml %{buildroot}%{_datadir}/%{name}/recipes/flavours/

#generate recipes doc
mkdir -p %{buildroot}%{_docdir}/%{name}/
%{__python3} arkimaps document-recipes --destdir %{buildroot}%{_docdir}/%{name}/

%check
%{__python3} setup.py test

%files
%{_bindir}/%{name}
%{python3_sitelib}/%{name}*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
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
* Mon Nov 22 2021 Daniele Branchini <dbranchini@arpae.it> - 0.5-1
- added input validation (#85)

* Wed Nov 10 2021 Daniele Branchini <dbranchini@arpae.it> - 0.4-4
- refactored test suite to isolate Magics (#84)

* Tue Nov  9 2021 Daniele Branchini <dbranchini@arpae.it> - 0.4-3
- fixed recipes installation

* Mon Nov  8 2021 Daniele Branchini <dbranchini@arpae.it> - 0.4-2
- added workaround for proj issue (#83)

* Mon Oct 25 2021 Daniele Branchini <dbranchini@arpae.it> - 0.4-1
- First build
