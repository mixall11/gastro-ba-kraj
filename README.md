# Gastro mapa — BA · TT · NR · TN · BB kraj

Interaktívna mapa a databáza veľkokapacitnej gastronómie v **Bratislavskom, Trnavskom, Nitrianskom, Trenčianskom a Banskobystrickom kraji**. B2B nástroj na cielené oslovenie (predaj surovín/služieb gastru).

**Živá mapa:** https://mixall11.github.io/gastro-ba-kraj/

## Obsah
- **`index.html`** — interaktívna Leaflet mapa: prepínač **kraja (BA / TT / NR / Oba)**, **letecký režim** (satelit Esri), 5 kategórií, filtre podľa typu a okresu, hľadanie, popupy s kontaktom, **trasa autom po ceste (OSRM)** s optimalizovaným poradím + km/čas a **navigácia cez Google Maps**
- **`data.js`** — dáta mapy (293 prevádzok s GPS: 81 BA + 49 TT + 51 NR + 53 TN + 59 BB, pole `kraj`)
- **`gastro-databaza-BA-kraj.csv` / `.xml`** — databáza Bratislavský kraj (81)
- **`gastro-databaza-TT-kraj.csv` / `.xml`** — databáza Trnavský kraj (49)
- **`gastro-databaza-NR-kraj.csv` / `.xml`** — databáza Nitriansky kraj (51, okresy Nitra/Komarno/Levice/Nove Zamky/Sala/Topolcany/Zlate Moravce)
- **`gastro-databaza-TN-kraj.csv` / `.xml`** — databáza Trenčiansky kraj (53)
- **`gastro-databaza-BB-kraj.csv` / `.xml`** — databáza Banskobystrický kraj (59, všetkých 13 okresov, zóny B1–B7)
- **`roadmapa-auto.md`** — návrh trasy autom, BA kraj (štart Petržalka)
- **`roadmapa-auto-TT.md`** — návrh trasy autom, TT kraj (štart Trnava, 2 dni juh/sever, ~439 km)
- **`build_map.py`** — regenerácia XML + `data.js` z oboch CSV (geokódovanie cez Nominatim/OSM)

## Kategórie
Catering / firemné stravovanie · vývarovne / catering kuchyne · táckárne / závodné jedálne · veľké reštaurácie / sály · reštauračné siete (3+ prevádzok) · **štátne firmy a úrady** (veľkí štátni zamestnávatelia/úrady s jedálňou alebo verejným obstarávaním stravy).

## Funkcie mapy
- **Kraj** — prepni medzi BA, TT alebo zobraz oba naraz (mapa sa autocentruje, okresy sa prispôsobia)
- **🛰️ Letecký režim** — prepínač vpravo hore (satelitné dlaždice Esri + popisky)
- **Filtre** — typ prevádzky, okres, fulltext hľadanie
- **🚗 Trasa autom po ceste** — reálna cesta po cestách (OSRM), poradie optimalizované na najkratšiu jazdu, zobrazí km + čas. Štart: Petržalka (BA) / Trnava (TT)
- **🧭 Google Maps** — globálne tlačidlo otvorí trasu cez viditeľné body (max ~10 zastávok v optimalizovanom poradí), v popupe každého bodu „Navigovať sem"

## Lokálny náhľad / regenerácia
```bash
python3 -m http.server 8791        # http://localhost:8791/
python3 build_map.py               # prečíta oba CSV, geokóduje, prepíše XML + data.js
```

## Zdroje
FinStat.sk (IČO, tržby), weby firiem (kontakty), OpenStreetMap/Nominatim (geokódovanie), OSRM (trasovanie), Esri (letecké dlaždice). Dáta orientačné — pred oslovením over kontakt.
