# Elenco prodotti attualmente pubblicati su infomet

*modelli censiti: cosmo 5M operativo, cosmo 5I backup, cosmo 5M AM, cleps det, cosmo 2I, cosmo 2I ruc, cosmo1ch, ifs_ita010*

Immagini di riferimento dei prodotti nella cartella "prodotti" che contiene anche questo README (output relativo al primo dei modelli citati)

Note sui preprocessing:
 - precipitazioni: differenza di unità di misura ecmwf/cosmo, precipitazioni incrementali tranne cosmo1ch che sono già "spacchettate"
 - filtro su pressione MSLP (boxregrid con risoluzione variabile a seconda del modello per smoothing isolinee)
 - l'umidità relativa è da calcolare con metodologie differenti a seconda del livello (da temperatura di rugiada a 2m, da umidità specifica in quota)
 - le isotache si ottengono con modulo di u e v

Note sul rendering delle immagini:
 - sulle griglie ruotate (cosmo) magics parrebbe comunque fare a livello di backend un'interpolazione su grigliato regolare. Per le precipitazioni e in generale i campi con distribuzione irregolare è necessaria l'opzione `contour_interpolation_ceiling` di `mcont` che però pare essere saltata in CentOS8 (da approfondire)
 - per i vettori del vento, fino a qualche tempo fa il `thinning_factor` non funzionava e veniva effettuato un thinning a monte (sui grib)
 - la legenda dinamica è una feature richiesta per non mostrare un range troppo esteso (stagionalità della temperatura, etc). Un possibile compromesso potrebbe essere calcolare un range min e max sull'intera corsa.

## Lista prodotti da fare


| Prodotto       | Variabili | Modello |
| -------------- | --------- | ------- |
| Z500 + T500    | Geopotenziale(500 hPa), Temperatura generica(500 hPa), Vento(500 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| Z700 + T700    | Geopotenziale(700 hPa), Temperatura generica(700 hPa), Vento(700 hPa) | cosmo 5M, cleps det, ifs (ita) |
| Z850 + T850    | Geopotenziale(850 hPa), Temperatura generica(850 hPa), Vento(850 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| Z925 + T925    | Geopotenziale(925 hPa), Temperatura generica(925 hPa), Vento(925 hPa) | cosmo 5M, ifs (ita) |
| Z500 + T850    | Geopotenziale(500 hPa), Temperatura generica(850 hPa) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| Altezza zero termico | Altezza zero termico (al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC, ifs (ita) |
| Jet              | Geopotenziale(250 hPa), Vento(250 hPa), Isotache(250 hPa) | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| U% + vento 700   | Umidità rel.(700 hPa), Vento(700 hPa) | cosmo 5M, cosmo 5I backup, ifs (ita), ifs (atl) |
| U% + vento 850   | Umidità rel.(850 hPa), Vento(850 hPa) | ifs (ita) |
| U% + vento 925   | Umidità rel.(925 hPa), Vento(925 hPa) | ifs (ita) |
| MSLP + vento 10m | Pressione(slm), Vento(10m), Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC, ifs (ita), ifs (atl) |
| Isotache scala Beaufort | Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 5M am, ifs (ita) |
| Vento massimo | non chiaro, ipotesi: vmax(10m), Isotache(10m) | cosmo 5M, cosmo 5I backup, cosmo 2I, , ifs (ita) (triorario) |
| Precipitazione totale (passi 1,3,6,12,24h)   | Preci tot cum(al suolo), Preci nev cum(al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det (no 1h), cosmo 2I, cosmo 2I RUC (no 24h), cosmo1 CH (solo 3h), ifs (ita) (no 1h), ifs (atl) (no 1, 3h) |
| Precipitazione nevosa (passi 1,3,6,12,24h)   | Preci nev cum(al suolo)  | cosmo 5M, cosmo 5I backup, cosmo 5M am (solo 6,12,24h), cleps det (no 1h), cosmo 2I, cosmo 2I RUC (no 12 e 24h), cosmo1 CH (solo 3h), ifs (ita) (no 3h), ifs (atl) (solo 24h) |
| Precipitazione convettiva (passi 3,6,12,24h) | Preci conv cum(al suolo) | cosmo 5M, cosmo 5I backup, cosmo 5M am (solo 6,12h), cleps det, ifs (ita) (no 3h) |
| Nubi strati       | Copertura nubi basse, Copertura nubi medie, Copertura nubi alte | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, cosmo 2I RUC, ifs (ita) |
| Nuvolosità totale | Copertura nuovolosa totale | cosmo 5M, cosmo 5I backup, cleps det, cosmo 2I, ifs (ita), ifs (atl) |
| Temp 2 metri      | Temperatura a 2m | cosmo 5M, cosmo 5I backup, cosmo 5M am, cleps det, cosmo 2I, cosmo 2I RUC, cosmo1 CH, ifs (ita), ifs (atl) |
| Indice di Thom    | Indice di Thom | cosmo 5M |
| U% 2 metri        | Umidità relativa 2 metri | cosmo 5M, cosmo 5I backup, cosmo 5M am, cosmo 2I |
| Visibilità        | Visibilità(m) | cosmo 5M, cosmo 2I, , ifs (ita) |
| Topografia relativa tra 1000 e 850 hPa | Spessore(1000 hPa), Spessore(850 hPa) | cosmo 5M, ifs (ita) |
| Topografia relativa tra 850 e 700 hPa  | Spessore(850 hPa), Spessore(700 hPa)  | cosmo 5M, ifs (ita) |


## Opzionali, complessi, a bassa priorità

 - I modelli probabilistici necessiterebbero di mappe multi panel
 - I modelli triorari (cosmo 2I RUC, cosmo 1 CH) avrebbero pannelli di confronto di preci trioraria fra corse 


Gli indici che seguono (legati prevalentemente a temporali e dintorni) hanno preprocessing particolarmente complesso:


| Prodotto       | Variabili | Modello |
| -------------- | --------- | ------- |
| Temperatura media giornaliera | media temperatura a 2m | cosmo 5M, ifs (ita) |
| Variazione Z500 12 ore | Variazione Geopotenziale 500hPa (dam/12 ore)   | cosmo 5M |
| Delta T500 12 ore      | Variazione temperatura 500hPa (°K/12 ore)      | cosmo 5M |
| LLJ+Jet                | Jet Streak 200 hPa, Low level Jet 925hPa       | cosmo 5M |
| Shear bassa troposfera | Shear del vento nei primi 3000 metri (m/s)     | cosmo 5M |
| Shear media troposfera | Shear del vento fra 500 e 925 hPa (m/s)        | cosmo 5M |
| MCS index              | Mesoscale Convective System Index (n)          | cosmo 5M |
| Velocità verticale 700 hPa | Velocità verticale (omega) a 700hPa (Pa/s) | cosmo 5M |
| Lifted index           | Lifted index (n)                               | cosmo 5M |
| Avvezione termica 700 hPa  | Avvezione termica (°K/s) e Geopotenziale a 700hPa | cosmo 5M |
| Contenuto totale di vapore | Acqua precipitabile (mm), Vento 850hPa, Vento 500hPa | cosmo 5M, ifs (atl) |
| CAPE+CIN Nord Italia   | C.A.P.E. (j/Kg), energia potenziale | cosmo 5M, cosmo 5I backup, cosmo 2I, cosmo 2I RUC |
| Cape Italia            | C.A.P.E. (j/Kg)                     | cosmo 5M, cosmo1 CH (area: nord italia), ifs (ita), ifs (atl) |
| indice K               | Indice K (n)                        | cosmo 5M, cosmo 5I backup, ifs (ita) |
| Vorticità assoluta a 500 hPa | Vorticità assoluta e Geopotenziale a 500 hPa | cosmo 5M |
| TetaE 925 hPa          | Temperatura equivalente potenziale a 925hPa        | cosmo 5M |
| Vorticità 2PV           | TetaE + Vento + Pressione | ifs (ita), ifs (atl) |
| Cape+Shear media troposfera | Surface geopotential (S), Convective Available Potential Energy, mean layer | cosmo 5M |
| Altezza temperatura bulbo bagnato 0 | Wet Bulb Zero Height (m) | cosmo 5M |
| Downward CAPE               | Downburst Available Potential Energy | cosmo 5M |
| Wet Microburst Index        | Wet Microburst Severity Index (WMSI)  | cosmo 5M |
| Dry Microburst Index        | Dry Microburst Index (DMI) | cosmo 5M |
