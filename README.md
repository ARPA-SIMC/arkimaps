# ArkiMaps (alfa)
Generazione mappe meteorologiche da modelli previsionali

## Scopo
Produzione di (quasi) tutti i plottaggi su mappa (leggi: no grafici) disponibili su infomet alla sezione "Previsioni" e voce "Modelli ad area limitata" e "Modelli globali di circolazione generale"

Idealmente agganciabile ad arkimet e più performante della produzione attuale al SIMC

## Requisiti di sistema

python3 >= 3.7
python3-magics

## Uso rapido

### Estrazione dati di prova

corsa intera (circa 3.7GiB)
```
arki-query --inline 'reftime:=today 00:00' http://arkimet.metarpa:8090/dataset/cosmo_5M_ita > test.arkimet
```

query ridotta (circa 840MiB):
```
arki-query --inline 'Reftime:=today 00:00;product:GRIB1,,2,75 or GRIB1,,2,73 or GRIB1,,2,74 or GRIB1,,2,2 or GRIB1,,1,11 or GRIB1,,2,11 or GRIB1,,3,11 or GRIB2,,,11,,3 or GRIB1,,2,71 or GRIB1,,201,187 or GRIB1,,2,6' http://arkiope.metarpa:8090/dataset/cosmo_5M_ita > test.arkimet
```

t2m (circa 24Mib):
```
arki-query --inline 'Reftime:=2020-09-03 00:00;product:GRIB1,80,2,11;level:g02' http://arkimet.metarpa:8090/dataset/cosmo_5M_ita > test.arkimet
```

### Generazione mappe

```
./arkimaps --filter eccodes -o out/out.tar
```

(vedi `./arkimaps -h` per tutte le opzioni)


## Riferimenti

Primi tentativi fatti con cineca: https://github.com/ARPA-SIMC/magics-maps

Stili di contouring predefiniti integrati in Magics:https://confluence.ecmwf.int/display/MAGP/Predefined+palettes+in+Magics 

Tracce di documentazione su contouring custom: https://github.com/ecmwf/skinnywms/issues/37

## File di dati disponibili e potenzialmente utili

* https://github.com/ARPA-SIMC/libsim/blob/master/data/vargrib2bufr.csv (instalato in /usr/share/libsim)
* `/usr/share/eccodes/definitions/grib1/cfVarName.def`


## Uso dei JSON in /usr/share/magics

* `/usr/share/magics/styles/palettes.json`: corrisponde a
  `contour_shade_palette_name` in <https://confluence.ecmwf.int/display/MAGP/Contouring>
* `contour_automatic_setting` in
  <https://confluence.ecmwf.int/display/MAGP/Contouring> è usato per attivare
  il match delle regole di contouring. V. anche [questo commento in skinnywms](https://github.com/ecmwf/skinnywms/issues/37#issuecomment-562215449)

Per scegliere stili diversi, `contour_automatic_setting` deve rimanere settato
sempre a `"ecmwf"`, e serve invece cambiare il path in `MAGICS_STYLE_PATH`:

```py
# Questo è quello che fa skinnywms
if args.style != "":
    os.environ["MAGICS_STYLE_PATH"] = args.style + ":ecmwf"
```

## Creazione di nuove ricette

In `arkimapslib/chef.py` sono definiti e commentati i vari `step` possibili. I
parametri passati agli `step` diventano parametri alle funzioni metodo della
classe `Chef`.

Per velocizzare le prove, ci sono alcune opzioni di `arkimaps`:

 * `./arkimaps --verbose --dispatch --workdir workdir` per smistare l'input in
   una directory di lavoro
 * `./arkimaps --verbose --workdir workdir --preview t2m+000` per fare la preview
   di un output solo data una directory di lavoro già smistata

La preview viene fatta con `xdg-open`, che usa l'applicazione preferita
configurata nel sistema. Solitamente si può usare il file manager per cambiarla
se quella di default non è l'ideale.


## Struttura del codice

* `Kitchen` contiene il contesto generale del run
* `Pantry` è l'interfaccia per l'accesso ai GRIB in input
* `Recipe` è la ricetta caricata da YAML
* `Chef` è l'implementazione dei vari passi possibili per le ricette
* `Order` è un prodotto in output
