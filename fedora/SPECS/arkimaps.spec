%global releaseno 2
# Note: define _srcarchivename in Travis build only.
%{!?srcarchivename: %global srcarchivename %{name}-%{version}-%{releaseno}}

Name:           arkimaps
Version:        1.33
Release:        %{releaseno}
Summary:        Meteo plot generator from grib data

License:        GPLv2+
URL:            https://github.com/ARPA-SIMC/%{name}
Source0:        https://github.com/ARPA-SIMC/%{name}/archive/v%{version}-%{releaseno}.tar.gz#/%{srcarchivename}.tar.gz

BuildRequires:  python3
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
BuildRequires:  python3-pyyaml
BuildRequires:  python3-gdal
BuildRequires:  python3-pillow
BuildRequires:  python3-pydantic

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
Requires:       python3-pyyaml
Requires:       python3-gdal
Requires:       python3-pillow
Requires:       python3-pydantic


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
install -d -m0755 %{buildroot}%{_datadir}/%{name}/
cp -R recipes %{buildroot}%{_datadir}/%{name}/

#generate recipes doc
mkdir -p %{buildroot}%{_docdir}/%{name}/
%{python3} arkimaps document-recipes --destdir %{buildroot}%{_docdir}/%{name}/

%check
%{python3} -m unittest discover --start-directory tests --verbose

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
* Mon Apr  7 2025 Daniele Branchini <dbranchini@arpae.it> - 1.33-2
- Renamed precipitation_type to precipitationtype

* Fri Apr  4 2025 Daniele Branchini <dbranchini@arpae.it> - 1.33-1
- Added precipitation_type product for IFS

* Tue Mar 25 2025 Daniele Branchini <dbranchini@arpae.it> - 1.32-1
- Added Products.by_recipe accessor (#183)

* Fri Mar 21 2025 Daniele Branchini <dbranchini@arpae.it> - 1.31-1
- Use curly brackets instead of null for empty recipe info in products.json

* Thu Mar 20 2025 Daniele Branchini <dbranchini@arpae.it> - 1.30-1
- Fixed validation for add_symbols (#179)
- Fixed and added test on JSON outputs (#181)

* Thu Mar 20 2025 Daniele Branchini <dbranchini@arpae.it> - 1.29-1
- Re-added typeOfStatisticalProcessing filter for tpclim product

* Tue Dec 24 2024 Daniele Branchini <dbranchini@arpae.it> - 1.28-1
- Improved t_inputs and tp_inputs definitions for praga and icon models

* Fri Dec 06 2024 Emanuele Di Giacomo <edigiacomo@arpae.it> - 1.27-1
- Removed deprecated test functions

* Wed Nov 13 2024 Daniele Branchini <dbranchini@arpae.it> - 1.26-1
- Fixed contouring inheritance from recipes

* Tue Nov 12 2024 Daniele Branchini <dbranchini@arpae.it> - 1.25-1
- Merge step values recursing into dicts (#175)
- Fix building magics command for add_grib (#176)

* Fri Nov  8 2024 Daniele Branchini <dbranchini@arpae.it> - 1.24-1
- Added snowlmt product

* Mon Oct  7 2024 Daniele Branchini <dbranchini@arpae.it> - 1.23-1
- support `-` to represent stdin in arkimaps dispatch (#171)
- fixed tests on new eccodes versions (#174)
- fixed matching eccodes output when no problems have been found

* Tue Sep 24 2024 Daniele Branchini <dbranchini@arpae.it> - 1.22-1
- added arkimapslib.polyfill to the packaged modules (#173)

* Thu Sep  5 2024 Daniele Branchini <dbranchini@arpae.it> - 1.21-1
- restored stdin (#171)
- fixed errors in contour lists in cape/capecin/thetae925 recipes
- added tsnowp variable for ICON model

* Wed Sep  4 2024 Daniele Branchini <dbranchini@arpae.it> - 1.20-3
- added pydantic dependency

* Tue Sep  3 2024 Daniele Branchini <dbranchini@arpae.it> - 1.20-2
- fixed build errors (#170)
- improved linting process via pydantic (#164)

* Tue Jun 18 2024 Daniele Branchini <dbranchini@arpae.it> - 1.20-1
- capture and log noisy `grib_filter` stderr
- detailed validation and linting of recipe definitions, including Magics
  macro parameters (#165)
- added TCW product for ICON model
- fixed total snowfall calculation for ICON model

* Mon Apr  8 2024 Daniele Branchini <dbranchini@arpae.it> - 1.19-1
- fixed extremes for bic product

* Mon Apr  8 2024 Daniele Branchini <dbranchini@arpae.it> - 1.18-1
- extended extremes for bic product
- fixed custom boundaries for wmax product

* Fri Mar 15 2024 Daniele Branchini <dbranchini@arpae.it> - 1.17-1
- extended extremes for dda, et, eta, ta, tclim, tpaperc, tpclim products
- fixed LPI legend

* Wed Mar  6 2024 Daniele Branchini <dbranchini@arpae.it> - 1.16-1
- Added LPI product
- Fixed recipes for litota3 and hzero products
- Documented output bundle json structure (#162)
- Fixed preview after order refactoring (#163)
- Better validation of the output of a render script (#164)

* Thu Jan 25 2024 Emanuele Di Giacomo <edigiacomo@arpae.it> - 1.15-2
- Remove pyproject-rpm-macros

* Thu Jan 25 2024 Daniele Branchini <dbranchini@arpae.it> - 1.15-1
- Minor fixes in ICON products definitions

* Wed Jan 24 2024 Daniele Branchini <dbranchini@arpae.it> - 1.14-1
- Added initial documentation for outputbundle (#159)
- Updated emro shapefile

* Wed Dec 27 2023 Emanuele Di Giacomo <edigiacomo@arpae.it> - 1.13-1
- Added info about legend and georeferencing in `products.json` (#149)
- Added Python API to read PNG and metadata (#149)
- Map cylindrical projection to EPSG:4326 (#158)

* Wed Dec 20 2023 Daniele Branchini <dbranchini@arpae.it> - 1.12-1
- Updated contouring for snow fall

* Fri Dec 15 2023 Daniele Branchini <dbranchini@arpae.it> - 1.11-1
- Updated contouring for total precipitation

* Mon Dec 11 2023 Daniele Branchini <dbranchini@arpae.it> - 1.10-1
- Do not dispatch inputs not needed by recipes selected by flavour (#87)
- Deal with time units in arkimet timeranges (#157)
- Fixed serialization of ModelStep steps (#154)

* Tue Dec  5 2023 Daniele Branchini <dbranchini@arpae.it> - 1.9-1
- Added `tground` product
- Added hzero, visibility for icon
- Fixed t2m query for grib2 data

* Thu Oct 26 2023 Daniele Branchini <dbranchini@arpae.it> - 1.8-1
- Fix redundancy in product summary (#153)

* Thu Oct 12 2023 Emanuele Di Giacomo <edigiacomo@arpae.it> - 1.7-2
- Add dependency to python3-pillow

* Thu Oct  5 2023 Emanuele Di Giacomo <edigiacomo@arpae.it> - 1.7-1
- Support GDAL < 3.3.0 version check in Python API

* Mon Sep 11 2023 Emanuele Di Giacomo <edigiacomo@arpae.it> - 1.6-2
- Fix recipes installation

* Fri Sep  8 2023 Emanuele Di Giacomo <edigiacomo@arpae.it> - 1.6-1
- Implemented recipe inheritance (#123)
- Added `arkimaps lint` to do consistency checking of recipes (#146)
- Added postprocessors
- Added postprocessor "cutshape" (#74)

* Fri May 26 2023 Daniele Branchini <dbranchini@arpae.it> - 1.4-2
- Added emro_web flavour

* Wed May 24 2023 Daniele Branchini <dbranchini@arpae.it> - 1.4-1
- Implemented `arkimet: skip` and `eccodes: skip` (#147)
- Add `$recipe_dir/static` directories to static paths (#144)
- Added json output documentation (#143)
- Added multiple PRAGA products
- Added some ADRIAC products (#141)

* Fri Feb 24 2023 Daniele Branchini <dbranchini@arpae.it> - 1.3-1
- Added GRIB2 products (variables at various hPa levels)

* Wed Feb 15 2023 Daniele Branchini <dbranchini@arpae.it> - 1.2-1
- Implemented rectangular tiles (#135)
- Fixed a bug in `arkimaps preview`

* Thu Jan 19 2023 Daniele Branchini <dbranchini@arpae.it> - 1.1-1
- Implemented macrotiles processing (8x8) (#126)
- Added products (wind speed for various hPa levels)
- Minor fixes in descriptions and palettes

* Thu Dec 22 2022 Daniele Branchini <dbranchini@arpae.it> - 1.0-1
- Added legend to tile output (#46)
- Added `product.json` output with a recap of the rendered contents (#124)
- Added the possibility to have custom field in recipes (#124)
- Added output files and tools to analyze production times (#125)
- Improved performance (Render using generated render scripts instead of multiprocessing.Pool) #128
- Allow to override `comp_stat_proc`, `comp_frac_valid`, and `comp_full_steps`,
  in `decumulate` and `average` derived inputs (#112, #122)
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
