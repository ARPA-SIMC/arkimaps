# New in version 1.25

* Merge step values recursing into dicts (#175)
* Fix building magics command for add_grib (#176)

# New in version 1.24

* added `snowlmt` product

# New in version 1.23

* support `-` to represent stdin in arkimaps dispatch (#171)
* fixed tests on new eccodes versions (#174)
* fixed matching eccodes output when no problems have been found

# New in version 1.22

* added arkimapslib.polyfill to the packaged modules (#173)

# New in version 1.21

* restored stdin (#171)
* fixed errors in contour lists in cape/capecin/thetae925 recipes
* added tsnowp variable for ICON model

# New in version 1.20

* capture and log noisy `grib_filter` stderr
* detailed validation and linting of recipe definitions, including Magics
  macro parameters (#165)
* added TCW product for ICON model
* fixed total snowfall calculation for ICON model
* improved linting process via pydantic (#164)

# New in version 1.19

* fixed extremes for bic product

# New in version 1.18

* extended extremes for bic product
* fixed custom boundaries for wmax product

# New in version 1.17

* extended extremes for dda, et, eta, ta, tclim, tpaperc, tpclim products
* fixed LPI legend

# New in version 1.16

* Added LPI product
* Fixed recipes for litota3 and hzero products
* Documented output bundle json structure (#162)
* Fixed preview after order refactoring (#163)
* Better validation of the output of a render script (#164)

# New in version 1.15

* Minor fixes in ICON products definitions

# New in version 1.14

* Added initial documentation for outputbundle (#159)
* Updated emro shapefile

# New in version 1.13

* Added info about legend and georeferencing in `products.json` (#149)
* Added Python API to read PNG and metadata (#149)
* Map cylindrical projection to EPSG:4326 (#158)

# New in version 1.12

* Updated contouring for snow fall

# New in version 1.11

* Updated contouring for total precipitation

# New in version 1.10

* Do not dispatch inputs not needed by recipes selected by flavour (#87)
* Deal with time units in arkimet timeranges (#157)
* Fixed serialization of ModelStep steps (#154)

# New in version 1.9

* Added `tground` product
* Added hzero, visibility for icon
* Fixed t2m query for grib2 data

# New in version 1.8

* Fixed redundancy in product summary (#153)

# New in version 1.7

* Support GDAL < 3.3.0 version check in Python API

# New in version 1.6

* Implemented [recipe inheritance](doc/derived_recipe.md) (#123)
* Added `arkimaps lint` to do consistency checking of recipes (#146)
* Added postprocessors
* Added postprocessor "cutshape" (#74)

# New in version 1.5

* Added `emro_web` flavour

# New in version 1.4

* Implemented `arkimet: skip` and `eccodes: skip` (#147)
* Add `$recipe_dir/static` directories to static paths (#144)
* Added json output documentation (#143)
* Added multiple PRAGA products
* Added some ADRIAC products (#141)

# New in version 1.3

* Added GRIB2 products (variables at various hPa levels)

# New in version 1.2

* Implemented rectangular tiles (#135)
* Fixed a bug in `arkimaps preview`

# New in version 1.1

* Implemented macrotiles processing (8x8) (#126)
* Added products (wind speed for various hPa levels)
* Minor fixes in descriptions and palettes

# New in version 1.0

* Added legend to tile output (#46)
* Added `product.json` output with a recap of the rendered contents (#124)
* Added the possibility to have custom field in recipes (#124)
* Added output files and tools to analyze production times (#125)
* Improved performance (Render using generated render scripts instead of multiprocessing.Pool) #128
* Allow to override `comp_stat_proc`, `comp_frac_valid`, and `comp_full_steps`,
  in `decumulate` and `average` derived inputs (#112, #122)
* Various cosmetic improvements to recipes

# New in version 0.11

* Added wmax grib2
* Switching language (and README.md) in English

# Novità nella versione 0.10

* Aggiunti prodotti grib2 (t2m, uv10m, mslp, tp, 2d/rh2m, cc, sf)
* Aggiunta area `ita_small`
* Verifica formato `recipes_filter` per i flavour (#116)
* Nuovi prodotti (vedere doc/prodotti/README.md per dettagli) :
  * sst (sea surface temperature)
  * tcw (total column water)
  * tcwwind (total column water + wind 850hPa 500hPa)
  * frzrain (freezing rain)

# Novità nella versione 0.9

* Aggiunto prodotto snow fraction (#38)
* Aggiunto tipo di input sffraction
* Aggiunti filtri per calcolare variabili derivate solo da modelli specifici
* Correzione bug minori

# Novità nella versione 0.8

* Nuovi prodotti (vedere doc/prodotti/README.md per dettagli) :
  * hzero (#5)
  * vis (#103)
  * cc (#104)
  * thomindex (#105)
  * kindex (#106)
  * cape (#107)
  * capecin (#107)
  * capeshear (#107)
  * thetaePV (#108)
  * thetae925 (#108)
  * t2mavg (#109)
* Nuovi tipi di input (vedere doc/INPUTS.rst per dettagli):
  * groundtomsl
  * expr
  * average
* Estesa documentazione

# Novità nella versione 0.7

* Nuovi prodotti (vedere README.md nella dir doc/prodotti per dettagli) :
  * rhw700/850/900 (#94)
  * jet (#93)
  * wmaxw10m
  * sf
  * mslpw10m (#95)
  * w10mbeaufort (#96)
* Migliorata spazializzazione flag vento (#98)
* Bug fix minori

# Novità nella versione 0.6

* Aggiunto il rendering di tile (#45)
* Differenziati plot per reftime permettendo gestione corse multiple e analisi (#88, #77)
* Modificata sintassi della modalità preview (#89)
* Modificata struttura output e nomi dei file prodotti (#42, #77)

# Novità nella versione 0.5

* Introdotta validazione input (#85)
* `askimaps preview` permette di omettere lo step, e di specificare il reference time (#89)

# Novità nella versione 0.4

* Aggiunti file per pacchettizzazione e distribuzione (#76)
* Test suite (#52)
* Aggiunto glossario e workflow ricette
* Corretta la documentazione degli input delle ricette (#79)

# Novità nella versione 0.3

* Aggiunta opzione `--grib` per rendering diretto di grib
* Migliorata documentazione
* Parzialmente introdotti campi erg5

# Novità nella versione 0.2

* Aggiunta di varianti ("flavour") per il rendering
* Implementato un set di aree per i plottaggi incluso una versione per visualizzazioni a layer priva di riferimenti cartografici e georeferenziabile
* Aggiunta di tipologie di prodotti:
  * precipitazione
  * vento
  * plot combinati (es.: geopotenziale, temperatura e vento a vari livelli di pressione)
* Implementata una modalità `preview` che permette di testare le singole ricette generando contestualmente uno script python autoconsistente utile per isolare/analizzare problematiche

# New in version 0.1

This is a pre-release featuring png outputs with a static area and fixed backround for the following plots:
* total cloud cover
* high/medium/low cloud cover
* mean sea level pressure
* temperature at 2 metres
* maximum wind gust
* temperature at 500/750/800/925 hPa
* geopotential at 500/750/800/925 hPa
