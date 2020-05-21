# Elenco prodotti attualmente pubblicati su infomet

*Lista in aggiornamento*

*completati: cosmo 5M operativo, cosmo 5I backup, cosmo 5M AM, cleps det, cosmo 2I, cosmo 2I ruc*

*da fare: cosmo1ch, ifs*

Immagini di riferimento dei prodotti nella cartella "images" (output cosmo 5M)

TODO (da approfondire):
 - variabili: al momento derivate da descrizione infomet
 - rapporti modelli/dataset (cambia solo l'area di riferimento o ci sono variabili diverse?)
 - legenda dinamica: è feature globale/necessaria?
 - modelli probabilistici esclusi (necessitano di mappe multi panel)

| Prodotto       | Variabili | Modello |
| -------------- | --------- | ------- |
| Z500 + T500    | Geopotenziale(500 hPa), Temperatura generica(500 hPa), Vento(500 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I |
| Z700 + T700    | Geopotenziale(700 hPa), Temperatura generica(700 hPa), Vento(700 hPa) | cosmo 5M, cleps det |
| Z850 + T850    | Geopotenziale(850 hPa), Temperatura generica(850 hPa), Vento(850 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I |
| Z925 + T925    | Geopotenziale(925 hPa), Temperatura generica(925 hPa), Vento(925 hPa) | cosmo 5M |
| Z500 + T850    | Geopotenziale(500 hPa), Temperatura generica(850 hPa) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I |
| Altezza zero termico | Altezza zero termico (al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC |
| Jet              | Geopotenziale(250 hPa), Vento(250 hPa), Isotache(250 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I |
| U% + vento 700   | Umidità rel.(700 hPa), Vento(700 hPa) | cosmo 5M, cosmo 5I backup |
| MSLP + vento 10m | Pressione(slm), Vento(10m), Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC |
| Isotache scala Beaufort | Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 5M am | 
| Vento massimo | non chiaro, ipotesi: vmax(10m), Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 2I |
| Precipitazione totale (passi 1,3,6,12,24h)   | Preci tot cum(al suolo), Preci nev cum(al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det (no 1h), cosmo 2I, cosmo 2I RUC (no 24h) |
| Precipitazione nevosa (passi 1,3,6,12,24h)   | Preci nev cum(al suolo)  | cosmo 5M, cosmo 5I backup, cosmo 5M am (solo 6,12,24h), cleps det (no 1h), cosmo 2I, cosmo 2I RUC (no 12 e 24h) |
| Precipitazione convettiva (passi 3,6,12,24h) | Preci conv cum(al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am (solo 6,12h), cleps det |
| Nubi strati       | Copertura nubi basse, Copertura nubi medie, Copertura nubi alte | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, cosmo 2I RUC |
| Nuvolosità totale | Copertura nuovolosa totale | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I |
| Temp 2 metri      | Temperatura a 2m | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC |
| Indice di Thom    | Indice di Thom | cosmo 5M |
| U% 2 metri        | Umidità relativa 2 metri | cosmo 5M, cosmo 5I backup, cosmo 5M am, cosmo 2I |
| Topografia relativa tra 1000 e 850 hPa | Spessore(1000 hPa), Spessore(850 hPa) | cosmo 5M |
| Topografia relativa tra 850 e 700 hPa  | Spessore(850 hPa), Spessore(700 hPa)  | cosmo 5M |
| Visibilità        | Visibilità(m) | cosmo 5M, cosmo 2I |
| Temperatura media giornaliera | media temperatura a 2m | cosmo 5M |
| Variazione Z500 12 ore | Variazione Geopotenziale 500hPa (dam/12 ore)   | cosmo 5M |
| Delta T500 12 ore      | Variazione temperatura 500hPa (°K/12 ore)      | cosmo 5M |
| LLJ+Jet                | Jet Streak 200 hPa, Low level Jet 925hPa       | cosmo 5M |
| Shear bassa troposfera | Shear del vento nei primi 3000 metri (m/s)     | cosmo 5M |
| Shear media troposfera | Shear del vento fra 500 e 925 hPa (m/s)        | cosmo 5M |
| MCS index              | Mesoscale Convective System Index (n)          | cosmo 5M |
| Velocità verticale 700 hPa | Velocità verticale (omega) a 700hPa (Pa/s) | cosmo 5M |
| Lifted index           | Lifted index (n)                               | cosmo 5M |
| Avvezione termica 700 hPa  | Avvezione termica (°K/s) e Geopotenziale a 700hPa | cosmo 5M |
| Contenuto totale di vapore | Acqua precipitabile (mm), Vento 850hPa, Vento 500hPa | cosmo 5M |
| CAPE+CIN Nord Italia   | C.A.P.E. (j/Kg), energia potenziale | cosmo 5M, cosmo 5I backup, cosmo 2I, cosmo 2I RUC |
| Cape Italia            | C.A.P.E. (j/Kg)                     | cosmo 5M |
| indice K               | Indice K (n)                        | cosmo 5M, cosmo 5I backup |
| Vorticità assoluta a 500 hPa | Vorticità assoluta e Geopotenziale a 500 hPa | cosmo 5M |
| TetaE 925 hPa          | Temperatura equivalente potenziale a 925hPa        | cosmo 5M |
| Cape+Shear media troposfera | Surface geopotential (S), Convective Available Potential Energy, mean layer | cosmo 5M |
| Altezza temperatura bulbo bagnato 0 | Wet Bulb Zero Height (m) | cosmo 5M |
| Downward CAPE               | Downburst Available Potential Energy | cosmo 5M |
| Wet Microburst Index        | Wet Microburst Severity Index (WMSI)  | cosmo 5M |
| Dry Microburst Index        | Dry Microburst Index (DMI) | cosmo 5M |


