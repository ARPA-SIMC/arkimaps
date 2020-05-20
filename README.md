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
arki-query --inline 'reftime:=yesterday 00:00' http://arkimet.metarpa:8090/dataset/cleps_grib1 > test.arkimet
```
