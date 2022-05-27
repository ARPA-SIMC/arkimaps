# Elenco aree implementate

| Sigla    | Descrizione         | Proiezione          | Bounding box            |
| -------- | ------------------- | ------------------- | ----------------------- |
| `ita`    | Italia              | cylindrical         | 50.0N 35.0N 20.0E  2.5E |
| `ita_small` | Italia (ridotta) | cylindrical         | 48.0N 35.0N 20.0E  5.0E |
| `emro`   | Emilia-Romagna      | polar_stereographic | 45.2N 43.4N 13.2E  9.0E |
| `nord`   | Nord Italia         | mercator            | 47.5N 43.0N 15.0E  5.1E |
| `centro` | Centro Italia       | polar_stereographic | 44.0N 38.5N 19.8E  7.8E |
| `sud`    | Sud Italia          | polar_stereographic | 41.5N 36.0N 19.0E  8.0E |
| `medit`  | Area mediterranea   | mercator            | 52.0N 30.0N 35.0E  8.0W |
| `euratl` | Area euroatlantica  | polar_stereographic | 60.0N 25.0N 65.0E 25.0W |
| `ita_web`| Italia (layer)      | EPSG:3857 | 50.0N 35.0N 20.0E  2.5E |

Nota: le aree `*_web` sono scontornate e prive di sfondi o riferimenti cartografici per un'eventuale
georeferenziazione, al momento non implementata in arkimaps ma ottenibile postprocessando gli output
ad es. via gdal:

```
gdal_translate -of Gtiff -a_srs 'EPSG:3857' -a_ullr 389618.2177764575 6446275.841017158 2226389.8158654715 4163881.144064294 plot.png out.tiff
```

# Elenco prodotti implementati

| Sigla   | Descrizione                               | Esempio   | Doc. Ricetta |
| ------- | ----------------------------------------- | --------- | ------------ |
| `t2m`   | Temperatura a 2 metri dal suolo           | [t2m.png](t2m.png "Temperatura a 2 metri") | [t2m.md](../recipes/t2m.md) |
| `rh2m`  | Umidità relativa a 2 metri dal suolo      | [rh2m.png](rh2m.png "Umidità relativa a 2 metri") | [rh2m.md](../recipes/rh2m.md) |
| `vis`   | Visibilità                                | [vis.png](vis.png "Visibilità")           | [vis.md](../recipes/vis.md) |
| `hzero` | Altezza dello zero termico                | [hzero.png](hzero.png "Altezza dello zero termico") | [hzero.md](../recipes/hzero.md) |
| `tcc`   | Copertura nuvolosa totale                 | [tcc.png](tcc.png "Copertura nuvolosa")   | [tcc.md](../recipes/tcc.md) |
| `hcc`   | Copertura nubi alte                       | [hcc.png](hcc.png "Copertura nubi alte")  | [hcc.md](../recipes/tiles/hcc.md) |
| `mcc`   | Copertura nubi medie                      | [mcc.png](mcc.png "Copertura nubi medie") | [mcc.md](../recipes/tiles/mcc.md) |
| `lcc`   | Copertura nubi basse                      | [lcc.png](lcc.png "Copertura nubi basse") | [lcc.md](../recipes/tiles/lcc.md) |
| `cc`    | Copertura nubi strati (alte/medie/basse)  | [cc.png](cc.png "Copertura nubi strati")  | [cc.md](../recipes/standalone/cc.md)   |
| `ztw500`| Geopotenziale, temperatura e vento a 500 hPa | [ztw500.png](ztw500.png)               | [ztw500.md](../recipes/standalone/ztw500.md) |
| `ztw700`| Geopotenziale, temperatura e vento a 700 hPa | [ztw700.png](ztw700.png)               | [ztw700.md](../recipes/standalone/ztw700.md) |
| `ztw850`| Geopotenziale, temperatura e vento a 850 hPa | [ztw850.png](ztw850.png)               | [ztw850.md](../recipes/standalone/ztw850.md) |
| `ztw925`| Geopotenziale, temperatura e vento a 925 hPa | [ztw925.png](ztw925.png)               | [ztw925.md](../recipes/standalone/ztw925.md) |
| `z500t850`| Geopotenziale a 500 hPa, temperatura a 850 hPa | [z500t850.png](z500t850.png)       | [z500t850.md](../recipes/standalone/z500t850.md) |
| `tp1h`    | Precipitazione cumulata su 1h con frazione nevosa e vento a 10m || [tp1h.png](tp1h.png) | [tp1h.md](../recipes/standalone/tp1h.md)   |
| `tp3h` `tp6h` `tp12h` `tp24h` | Precipitazione totale cumulata su 3/6/12/24h con frazione nevosa  | [tp24h.png](tp24h.png) | [tp3h.md](../recipes/standalone/tp3h.md) [tp6h.md](../recipes/standalone/tp6h.md) [tp12h.md](../recipes/standalone/tp12h.md) [tp24h.md](../recipes/standalone/tp24h.md) |
| `cp3h` `cp6h` `cp12h` `cp24h` | Precipitazione convettiva cumulata su 3/6/12/24h | [cp24h.png](cp24h.png)  |  [cp3h.md](../recipes/cp3h.md) [cp6h.md](../recipes/cp6h.md) [cp12h.md](../recipes/cp12h.md) [cp24h.md](../recipes/cp24h.md) |
| `sf1h` `sf3h` `sf6h` `sf12h` `sf24h` | Precipitazione nevosa totale cumulata su 1/3/6/12/24h     | [sf24h.png](sf24h.png)  |  [sf1h.md](../recipes/sf1h.md) [sf3h.md](../recipes/sf3h.md) [sf6h.md](../recipes/sf6h.md) [sf12h.md](../recipes/sf12h.md) [sf24h.md](../recipes/sf24h.md) |
| `litota3` | Densità media fulminazioni nelle ultime 3h | [litota3.png](litota3.png "Densità fulminazioni 3h") | [litota3.md](../recipes/litota3.md) |
| `viwvn`  | Vertical integral of northward water vapour flux | [viwvn.png](viwvn.png) | [viwvn.md](../recipes/viwvn.md) |
| `viwvn`  | Vertical integral of eastward water vapour flux  | [viwve.png](viwve.png) | [viwve.md](../recipes/viwve.md) |
| `wmax`   | Raffica massima vento                          | [wmax.png](wmax.png)   | [wmax.md](../recipes/tiles/wmax.md)   |
| `t2mavg` | Media giornaliera temperatura a 2 metri dal suolo  | [t2mavg.png](t2mavg.png) | [t2mavg.md](../recipes/t2mavg.md) |
| `jet`    | Geopotenziale, vento, isotache a 250hPa          | [jet.png](jet.png)     | [jet.md](../recipes/standalone/jet.md)     |
| `rhw700` | Umidità relativa e vento a 700hPa                | [rhw700.png](rhw700.png) | [rhw700.md](../recipes/standalone/rhw700.md) |
| `rhw850` | Umidità relativa e vento a 850hPa                | [rhw850.png](rhw850.png) | [rhw850.md](../recipes/standalone/rhw850.md) |
| `rhw925` | Umidità relativa e vento a 925hPa                | [rhw925.png](rhw925.png) | [rhw925.md](../recipes/standalone/rhw925.md) |
| `mslpw10m` | Pressione a livello del mare e vento a 10m     | [mslpw10m.png](mslpw10m.png) | [mslpw10m.md](../recipes/standalone/msalpw10m.md) |
| `w10mbeaufort` | Vento a 10m scala Beaufort                 | [w10mbeaufort.png](w10mbeaufort.png) | [w10mbeaufort.md](../recipes/standalone/w10mbeaufort.md) |
| `kindex`   | Indice K                                       | [kindex.png](kindex.png)     | [kindex.md](../recipes/kindex.md) |
| `thomindex` | Indice di disagio bioclimatico di Thom        | [thomindex.png](thomindex.png)     | [thomindex.md](../recipes/thomindex.md) |
| `thetaePV` `thetae850`  | Temperatura equivalente potenziale | [thetaePV.png](thetaePV.png) | [thetaePV.md](../recipes/standalone/thetaePV.md) |
| `cape` `capecin` | Convective Available Potential Energy, Convective Inhibition (CIN) | [capecin.png](capecin.png) | [capecin.md](../recipes/standalone/capecin.md) |
| `capeshear` | Convective Available Potential Energy Shear | [capeshear.png](capeshear.png) | [capeshear.md](../recipes/capeshear.md) |
| `sst`    | Temperatura superficiale del mare              | [sst.png](sstm.png) | [sst.md](../recipes/sst.md) |
| `tcw`    | Contenuto totale acqueo                        | [tcw.png](tcw.png)  | [tcw.md](../recipes/tcw.md) |
| `tcwwind`  | Contenuto totale acqueo e vento a 500hPa e 850hPa | [tcwwind.png](tcwwind.png)  | [tcwwind.md](../recipes/standalone/tcwwind.md) |
| `frzrain`  | Freezing rain                                | [frzrain.png](frzrain.png)  | [frzrain.md](../recipes/frzrain.md) |

# Censimento prodotti attualmente pubblicati su infomet

Nota: L'elenco che segue riguarda una lista di prodotti di riferimento sulla piattaforma "infomet" di ARPAE-SIMC

*modelli censiti: cosmo 5M operativo, cosmo 5I backup, cosmo 5M AM, cleps det, cosmo 2I, cosmo 2I ruc, cosmo1ch, ifs_ita010*

## Prodotti infomet (già implementati)

| cod.int. | Prodotto       | Variabili | Modello |
| ----- | -------------- | --------- | ------- |
| alt0 | Altezza zero termico | Altezza zero termico (al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC, ifs (ita) |
| ztw | Z500 + T500    | Geopotenziale(500 hPa), Temperatura generica(500 hPa), Vento(500 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| ztw | Z700 + T700    | Geopotenziale(700 hPa), Temperatura generica(700 hPa), Vento(700 hPa) | cosmo 5M, cleps det, ifs (ita) |
| ztw  | Z850 + T850    | Geopotenziale(850 hPa), Temperatura generica(850 hPa), Vento(850 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| ztw | Z925 + T925    | Geopotenziale(925 hPa), Temperatura generica(925 hPa), Vento(925 hPa) | cosmo 5M, ifs (ita) |
| syn | Z500 + T850    | Geopotenziale(500 hPa), Temperatura generica(850 hPa) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| jet  | Jet              | Geopotenziale(250 hPa), Vento(250 hPa), Isotache(250 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| u700 | U% + vento 700   | Umidità rel.(700 hPa), Vento(700 hPa) | cosmo 5M, cosmo 5I backup, ifs (ita), ifs (atl) |
| u700 | U% + vento 850   | Umidità rel.(850 hPa), Vento(850 hPa) | ifs (ita) |
| u700 | U% + vento 925   | Umidità rel.(925 hPa), Vento(925 hPa) | ifs (ita) |
| mslp | MSLP + vento 10m | Pressione(slm), Vento(10m), Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC, ifs (ita), ifs (atl) |
| beau | Isotache scala Beaufort | Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 5M am, ifs (ita) |
| vmax | Vento massimo | vmax(10m), Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 2I, , ifs (ita) (triorario) |
| rain | Precipitazione totale (passi 1,3,6,12,24h)   | Preci tot cum(al suolo), Preci nev cum(al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det (no 1h), cosmo 2I, cosmo 2I RUC (no 24h), cosmo1 CH (solo 3h), ifs (ita) (no 1h), ifs (atl) (no 1, 3h) |
| neve | Precipitazione nevosa (passi 1,3,6,12,24h)   | Preci nev cum(al suolo)  | cosmo 5M, cosmo 5I backup, cosmo 5M am (solo 6,12,24h), cleps det (no 1h), cosmo 2I, cosmo 2I RUC (no 12 e 24h), cosmo1 CH (solo 3h), ifs (ita) (no 3h), ifs (atl) (solo 24h) |
| conv | Precipitazione convettiva (passi 3,6,12,24h) | Preci conv cum(al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am (solo 6,12h), cleps det, ifs (ita) (no 3h) |
| nTot | Nuvolosità totale | Copertura nuovolosa totale | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| t2m  | Temp 2 metri      | Temperatura a 2m | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC, cosmo1 CH, ifs (ita), ifs (atl) |
| umid | U% 2 metri        | Umidità relativa 2 metri | cosmo 5M, cosmo 5I backup, cosmo 5M am, cosmo 2I |
| visi | Visibilità        | Visibilità(m) | cosmo 5M, cosmo 2I, , ifs (ita) |
| nubS | Nubi strati       | Copertura nubi basse, Copertura nubi medie, Copertura nubi alte | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, cosmo 2I RUC, ifs (ita) |
| indK | indice K          | Indice K (n) | cosmo 5M, cosmo 5I backup, ifs (ita) |
| 2PV  | tetaE alla 2 PV   | TetaE + Vento + Pressione | ifs (ita), ifs (atl) |
| cape | CAPE+CIN Nord Italia | C.A.P.E. (j/Kg), energia potenziale | cosmo 5M, cosmo 5I backup, cosmo 2I, cosmo 2I RUC |
| cape | Cape Italia          | C.A.P.E. (j/Kg)                     | cosmo 5M, cosmo1 CH (area: nord italia), ifs (ita), ifs (atl) |
|      | Temperatura media giornaliera | media temperatura a 2m | cosmo 5M, ifs (ita)  |
| thom | Indice di disagio-bioclimatico di Thom | Indice di Thom | cosmo 5M |
| sst  | Temperatura superficiale del mare | temperatura superificiale del mare | ifs (ita) |
| tcw/tcw  | total column water | total column water + vento a 850 e 500 hPa | ruc (no vento), ifs (ita), ifs (atl) |
| fzrnEc   | freezing rain      | freezing rain | ifs (ita) |
