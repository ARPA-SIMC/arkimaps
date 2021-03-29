# ArkiMaps (α)
Generazione mappe meteorologiche da modelli previsionali.

Attualmente implementati:
 * COSMO-LAMI
 * IFS-ECMWF (nella versione distribuita ai Centri Funzionali)

Funziona sia come programma standalone che come postprocessatore per https://github.com/ARPA-SIMC/arkimet

## Requisiti di sistema

 - python3 >= 3.7
 - python3-magics
 - eccodes

opzionali:
 
 - https://github.com/ARPA-SIMC/libsim (per alcuni preprocessing specifici - es.: precipitazione)
 - https://github.com/ARPA-SIMC/arkimet

## Guida rapida

### Generazione mappe da file grib

```
./arkimaps process -o out.tar --filter=eccodes < test_data.grib
```

### Generazione mappe da estrazione arkimet

```
# esempio per temperatura a 2 metri
arki-query --inline 'Reftime:=today 00:00;product:GRIB1,80,2,11;level:g02' http://arkimet.metarpa:8090/dataset/cosmo_5M_ita > test_data.arkimet
./arkimaps process -o out.tar < test_data.arkimet
```

Per ottenere i parametri arki-query di tutte le ricette attualmente disponibili:

```
./arkimaps print-arki-query
```

### Output

L'output è un file `tar` che contiene una directory per ogni recipe name; all'interno di ogni directory è presente un plot per ogni scadenza.

Per spacchettare automaticamente il file tar:
```
./arkimaps process --filter=eccodes < test.arkimet |tar -xf - -C out/
```

### Documentazione

Informazioni sull'inventario di aree e prodotti implementati sono
disponibili nella directory [prodotti](../master/prodotti/README.md)

Per una descrizione delle opzioni vedi:
```
./arkimaps -h
```

É anche disponibile un ulteriore descrizione per ogni subcommand, ad es.:

```
./arkimaps process -h
```

## Informazioni sulle ricette

Gli input definiti nelle ricette sono comuni a tutte le ricette: un input con
lo stesso nome definito in piú ricette dà errore. Una ricetta può usare input
definiti in un'altra ricetta. È possibile fare ricette senza step solo per
definire degli input comuni.

## Creazione di nuove ricette

In `arkimapslib/mixer.py` sono definiti e commentati i vari `step` possibili. I
parametri passati agli `step` diventano parametri alle funzioni metodo della
classe `Mixer`.

Per velocizzare le prove, ci sono alcune opzioni di `arkimaps`:

 * `./arkimaps --debug dispatch workdir` per smistare l'input in
   una directory di lavoro
 * `./arkimaps --debug preview workdir --preview t2m+000` per fare la preview
   di un output solo data una directory di lavoro già smistata

La preview viene fatta con `xdg-open`, che usa l'applicazione preferita
configurata nel sistema. Solitamente si può usare il file manager per cambiarla
se quella di default non è l'ideale.

### Creazione di test per nuove ricette

1. Fare dispatch di un output di modello per avere i dati di input grezzi
   (ripetere per COSMO e IFS)
2. Prendere un campione di dati dalle workdir in `pantry/nomericetta`
3. Processarli con `arki-scan --inline file.grib > file.arkimet`
4. Salvarli in `testdata/nomericetta`

## Creazione di varianti (flavour) per il rendering

Nei file `.yaml` dentro a `recipes/` è possibile aggiungere una sezione
`flavors` che introduce varianti di rendering. I comandi di `arkimaps` che
fanno rendering hanno un'opzione `--flavors` che permette di scegliere quali
varianti usare.

La struttura di una variante è:

* `name`: nome della variante
* `recipes_filter`: lista di nomi di ricette. Se presente, solo le ricette
  elencate saranno renderizzate per questo flavour. Sono permessi glob (es.
  `tp*`)
* `steps`: configurazione dei singoli step

La configurazione di uno step può avere:

* `skip: yes`: ignora quello step. Utile per esempio per disattivare il
  rendering di linee di costa e boundary, e lasciare solo il layer con i dati
* `params`: valore da usare come `params` se non esplicitamente specificato
  nella ricetta

## Struttura del codice

* `Kitchen` contiene il contesto generale del run
* `Pantry` è l'interfaccia per l'accesso ai GRIB in input
* `Recipe` è la ricetta caricata da YAML
* `Mixer` è l'implementazione dei vari passi possibili per le ricette
* `Order` è un prodotto in output

## Note su uso dei JSON in /usr/share/magics

* `/usr/share/magics/styles/palettes.json`: corrisponde a `contour_shade_palette_name` in 
<https://confluence.ecmwf.int/display/MAGP/Contouring>, documentazione completa disponibile qui: https://confluence.ecmwf.int/display/MAGP/Predefined+palettes+in+Magics 
* `contour_automatic_setting` in  <https://confluence.ecmwf.int/display/MAGP/Contouring> è usato per attivare
  il match delle regole di contouring. V. anche [questo commento in skinnywms](https://github.com/ecmwf/skinnywms/issues/37#issuecomment-562215449)

Per scegliere stili diversi, `contour_automatic_setting` deve rimanere settato
sempre a `"ecmwf"`, e serve invece cambiare il path in `MAGICS_STYLE_PATH`:

```py
# Questo è quello che fa skinnywms
if args.style != "":
    os.environ["MAGICS_STYLE_PATH"] = args.style + ":ecmwf"
```
## Contact and copyright information

arkimaps is Copyright (C) 2020-2021 ARPAE-SIMC <urpsim@arpae.it>

arkimaps is Free Software, licensed under the terms of the GNU General Public
License version 3.
