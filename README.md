# ArkiMaps (alfa)
Generazione mappe meteorologiche da modelli previsionali

## Scopo
Produzione di (quasi) tutti i plottaggi su mappa (leggi: no grafici) disponibili su infomet alla sezione "Previsioni" e voce "Modelli ad area limitata" e "Modelli globali di circolazione generale"

Idealmente agganciabile ad arkimet e più performante della produzione attuale al SIMC

## Requisiti di sistema

python3 >= 3.7
python3-magics

## Guida rapidissima

### Estrazione dati di prova

corsa intera (circa 3.7GiB)
```
arki-query --inline 'reftime:=2020-09-03 00:00' http://arkimet.metarpa:8090/dataset/cosmo_5M_ita > test.arkimet
```

query ridotta (circa 350MiB):

```
arki-query --inline 'Reftime:=2020-09-03 00:00;product:GRIB1,80,2,2 or GRIB1,80,2,11 or GRIB1,80,2,17 or GRIB1,80,2,15 or GRIB1,80,2,16 or GRIB1,80,2,61 or GRIB1,80,2,65 or GRIB1,80,2,78 or GRIB1,80,2,79 or GRIB1,80,2,33 or GRIB1,80,2,34 or GRIB1,80,201,187 or GRIB1,80,201,84 or GRIB1,80,2,73 or GRIB1,80,2,71;level:g00 or g02 or g10 or msl or 0isot' http://arkimet.metarpa:8090/dataset/cosmo_5M_ita > test.arkimet
```

t2m (circa 24Mib):
```
arki-query --inline 'Reftime:=2020-09-03 00:00;product:GRIB1,80,2,11;level:g02' http://arkimet.metarpa:8090/dataset/cosmo_5M_ita > test.arkimet
```

### Generazione mappe

```
./arkimaps -o out.tar --filter=eccodes < test.arkimet
```

per spacchettare automaticamente il file tar:
```
./arkimaps --filter=eccodes < test.arkimet |tar -xf - -C out/
```

per altre opzioni vedi:
```
./arkimaps -h
```

## Riferimenti esterni e cenni storici

Primi tentativi fatti con cineca: https://github.com/ARPA-SIMC/magics-maps

Stili di contouring predefiniti integrati in Magics:https://confluence.ecmwf.int/display/MAGP/Predefined+palettes+in+Magics 

Tracce di documentazione su contouring custom: https://github.com/ecmwf/skinnywms/issues/37


### File di dati disponibili e potenzialmente utili

* https://github.com/ARPA-SIMC/libsim/blob/master/data/vargrib2bufr.csv (instalato in /usr/share/libsim)
* `/usr/share/eccodes/definitions/grib1/cfVarName.def`


### Uso dei JSON in /usr/share/magics

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

