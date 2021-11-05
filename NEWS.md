# Novità nella versione 0.4

* Aggiunti file per pacchettizzazione e distribuzione (#76)
* Test suite (#52)
* Aggiunto glossario e workflow ricette
* Corretta la documentazione degli input delle ricette (#79)

# Novità nella versione 0.3

* aggiunta opzione `--grib` per rendering diretto di grib
* migliorata documentazione
* parzialmente introdotti campi erg5

# Novità nella versione 0.2

* aggiunta di varianti ("flavour") per il rendering
* implementato un set di aree per i plottaggi incluso una versione per visualizzazioni a layer priva di riferimenti cartografici e georeferenziabile
* aggiunta di tipologie di prodotti:
  * precipitazione
  * vento
  * plot combinati (es.: geopotenziale, temperatura e vento a vari livelli di pressione)
* implementata una modalità `preview` che permette di testare le singole ricette generando contestualmente uno script python autoconsistente utile per isolare/analizzare problematiche

# New in version 0.1

This is a pre-release featuring png outputs with a static area and fixed backround for the following plots:
* total cloud cover
* high/medium/low cloud cover
* mean sea level pressure
* temperature at 2 metres
* maximum wind gust
* temperature at 500/750/800/925 hPa
* geopotential at 500/750/800/925 hPa
