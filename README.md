# ArkiMaps (β)
Generazione mappe meteorologiche da modelli previsionali.

Attualmente implementati:
 * COSMO-LAMI
 * IFS-ECMWF (nella versione distribuita ai Centri Funzionali)
 * ERG5 (https://dati.arpae.it/dataset/erg5-interpolazione-su-griglia-di-dati-meteo)

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
./arkimaps process -o out.tar --grib < test_data.grib
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

#### Ritagli su aree diverse

È possibile usare l'opzione `--flavours` per specificare diverse modalità di output.

Ad esempio, per plot ritagliati sull'Emilia-Romagna:
```
./arkimaps process --filter=eccodes --flavours=emro < test.arkimet
```

L'elenco completo delle aree implementate è disponibile nella directory [prodotti](../master/prodotti/README.md).
È possibile aggiungere nuove aree modificando il contenuto del file [recipes/flavours/default.yaml](../master/recipes/flavours/default.yaml).

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

## Contact and copyright information

arkimaps is Copyright (C) 2020-2021 ARPAE-SIMC <urpsim@arpae.it>

arkimaps is Free Software, licensed under the terms of the GNU General Public
License version 3.
