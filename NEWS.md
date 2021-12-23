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
