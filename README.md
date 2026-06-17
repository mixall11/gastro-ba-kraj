# Gastro mapa — Bratislavský + Trnavský kraj

Interaktívna mapa a databáza veľkokapacitnej gastronómie v **Bratislavskom a Trnavskom kraji**. B2B nástroj na cielené oslovenie (predaj surovín/služieb gastru).

**Živá mapa:** https://mixall11.github.io/gastro-ba-kraj/

## Obsah
- **`index.html`** — interaktívna Leaflet mapa: prepínač **kraja (BA / TT / Oba)**, **letecký režim** (satelit Esri), 5 kategórií, filtre podľa typu a okresu, hľadanie, popupy s kontaktom, **trasa autom po ceste (OSRM)** s optimalizovaným poradím + km/čas a **navigácia cez Google Maps**
- **`data.js`** — dáta mapy (131 prevádzok s GPS: 82 BA + 49 TT, pole `kraj`)
- **`gastro-databaza-BA-kraj.csv` / `.xml`** — databáza Bratislavský kraj (82)
- **`gastro-databaza-TT-kraj.csv` / `.xml`** — databáza Trnavský kraj (49)
- **`roadmapa-auto.md`** — návrh trasy autom, BA kraj (štart Petržalka)
- **`roadmapa-auto-TT.md`** — návrh trasy autom, TT kraj (štart Trnava, 2 dni juh/sever, ~439 km)
- **`build_map.py`** — regenerácia XML + `data.js` z oboch CSV (geokódovanie cez Nominatim/OSM)

## Kategórie
Catering / firemné stravovanie · vývarovne / catering kuchyne · táckárne / závodné jedálne · veľké reštaurácie / sály · reštauračné siete (3+ prevádzok).

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
