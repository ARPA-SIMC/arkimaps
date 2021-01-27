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

### Help

per una descrizione delle opzioni vedi:
```
./arkimaps -h
```

è disponibile un ulteriore descrizione per ogni subcommand, ad es.:

```
./arkimaps process -h
```

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


## Struttura del codice

* `Kitchen` contiene il contesto generale del run
* `Pantry` è l'interfaccia per l'accesso ai GRIB in input
* `Recipe` è la ricetta caricata da YAML
* `Mixer` è l'implementazione dei vari passi possibili per le ricette
* `Order` è un prodotto in output

## Riferimenti esterni e cenni storici

Primi tentativi fatti con cineca: https://github.com/ARPA-SIMC/magics-maps

Stili di contouring predefiniti integrati in Magics:https://confluence.ecmwf.int/display/MAGP/Predefined+palettes+in+Magics 

Tracce di documentazione su contouring custom: https://github.com/ecmwf/skinnywms/issues/37

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

arkimaps is Free Software, licensed under the terms of the GNU General Public License version
2.
