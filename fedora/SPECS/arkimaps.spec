%global releaseno 1
# Note: define _srcarchivename in Travis build only.
%{!?srcarchivename: %global srcarchivename %{name}-%{version}-%{releaseno}}

Name:           arkimaps
Version:        1.0
Release:        %{releaseno}%{dist}
Summary:        Meteo plot generator from grib data

License:        GPLv2+
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
BuildRequires:  eccodes-devel

Requires:       python3
Requires:       python3-Magics
Requires:       python3-eccodes
# not strictly necessary, for code formatting
# (also: not available on CentOS8)
%{?fedora:Requires: python3-yapf}

%description
Automated framework to render GRIB1/2 data with ECMWF's Magics,
using a repository of simple YAML recipes.

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
mkdir -p %{buildroot}%{_datadir}/%{name}/recipes/standalone
install -D -m664 recipes/standalone/*.yaml %{buildroot}%{_datadir}/%{name}/recipes/standalone/
mkdir -p %{buildroot}%{_datadir}/%{name}/recipes/tiles
install -D -m664 recipes/tiles/*.yaml %{buildroot}%{_datadir}/%{name}/recipes/tiles/

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
Automated framework to render GRIB1/2 data with ECMWF's Magics,
using a repository of simple YAML recipes.
Postprocessor for arkimet.

%files -n arkimet-postprocess-%{name}
%defattr(-,root,root,-)
%{_libdir}/arkimet/%{name}

%changelog
* Thu Dec 22 2022 Daniele Branchini <dbranchini@arpae.it> - 1.0
- Added legend to tile output (#46)
- Added `product.json` output with a recap of the rendered contents (#124)
- Added the possibility to have custom field in recipes (#124)
- Added output files and tools to analyze production times (#125)
- Improved performance (Render using generated render scripts instead of multiprocessing.Pool) #128
- Allow to override `comp_stat_proc`, `comp_frac_valid`, and `comp_full_steps`,
  in `decumulate` and `average` derived inputs (#112, #122)
- Implemented [recipe inheritance](doc/derived_recipe.md) (#123)
- Various cosmetic improvements to recipes

* Wed Jun 29 2022 Daniele Branchini <dbranchini@arpae.it> - 0.11-1
- Added wmax grib2
- Switching language (and README.md) in English

* Wed May 25 2022 Daniele Branchini <dbranchini@arpae.it> - 0.10-1
- Aggiunti prodotti grib2 (t2m, uv10m, mslp, tp, 2d/rh2m, cc, sf)
- Aggiunta area `ita_small`
- Verifica formato `recipes_filter` per i flavour (#116)

* Fri May  6 2022 Daniele Branchini <dbranchini@arpae.it> - 0.9-3
- included standalone and tiles recipes subdir

* Wed Apr 27 2022 Daniele Branchini <dbranchini@arpae.it> - 0.9-2
- Aggiunto prodotto e input type snow fraction (#38)
- Aggiunti filtri per calcolare variabili derivate solo da modelli specifici
- Correzione bug minori

* Wed Apr 13 2022 Daniele Branchini <dbranchini@arpae.it> - 0.8-1
- Nuovi prodotti (vedere doc/prodotti/README.md per dettagli) :
  hzero (#5)
  vis (#103)
  cc (#104)
  thomindex (#105)
  kindex (#106)
  cape (#107)
  capecin (#107)
  capeshear (#107)
  thetaePV (#108)
  thetae925 (#108)
  t2mavg (#109)
- Nuovi tipi di input (vedere doc/INPUTS.rst per dettagli):
  groundtomsl
  expr
  average
- Estesa documentazione

* Thu Mar 17 2022 Daniele Branchini <dbranchini@arpae.it> - 0.7-1
- Nuovi prodotti (vedere README.md nella dir doc/prodotti per dettagli) :
  rhw700/850/900 (#94), jet (#93), wmaxw10m, sf, mslpw10m (#95), w10mbeaufort (#96)
- Migliorata spazializzazione flag vento (#98)
- Bug fix minori

* Mon Jan 17 2022 Daniele Branchini <dbranchini@arpae.it> - 0.6-2
- Rimossa dipendenza python3-yapf per centos8
- Correzioni a ricette geopotenziale per IFS+eccodes

* Thu Dec 23 2021 Daniele Branchini <dbranchini@arpae.it> - 0.6-1
- Aggiunto il rendering di tile (#45)
- Differenziati plot per reftime permettendo gestione corse multiple e analisi (#88, #77)
- Modificata sintassi della modalità preview (#89)
- Modificata struttura output e nomi dei file prodotti (#42, #77)

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
