# arkimaps (alfa)
Generazione mappe meteorologiche da modelli previsionali

## scopo
Produzione di (quasi) tutti i plottaggi su mappa (leggi: no grafici) disponibili su infomet alla sezione "Previsioni" e voce "Modelli ad area limitata" e "Modelli globali di circolazione generale"

Idealmente agganciabile ad arkimet e più performante della produzione attuale al SIMC

## riferimenti
Primi tentativi fatti con cineca: https://github.com/ARPA-SIMC/magics-maps

Stili di contouring predefiniti integrati in Magics:https://confluence.ecmwf.int/display/MAGP/Predefined+palettes+in+Magics 

Tracce di documentazione su contouring custom: https://github.com/ecmwf/skinnywms/issues/37


## Note sulle prove

Estrazione dati di prova:

```
# Nota: questo estrae circa 3.7GiB
arki-query --inline 'reftime:=yesterday 00:00' http://arkimet.metarpa:8090/dataset/cosmo_5M_ita > test.arkimet
```


## File di dati disponibili e potenzialmente utili

* https://github.com/ARPA-SIMC/libsim/blob/master/data/vargrib2bufr.csv (instalato in /usr/share/libsim)
* `/usr/share/eccodes/definitions/grib1/cfVarName.def`


## Uso dei JSON in /usr/share/magics

* `/usr/share/magics/styles/palettes.json`: corrisponde a
  `contour_shade_palette_name` in <https://confluence.ecmwf.int/display/MAGP/Contouring>
* `contour_automatic_setting` in
  <https://confluence.ecmwf.int/display/MAGP/Contouring> è usato per attivare
  il match delle regole di contouring. V. anche [questo commento in skinnywms](https://github.com/ecmwf/skinnywms/issues/37#issuecomment-562215449)

## Requisiti di sistema

python3 >= 3.7
python3-magics
