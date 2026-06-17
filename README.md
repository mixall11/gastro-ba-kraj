# Gastro mapa — Bratislavský kraj

Interaktívna mapa a databáza veľkokapacitnej gastronómie v Bratislavskom kraji. B2B nástroj na cielené oslovenie.

**Živá mapa:** https://mixall11.github.io/gastro-ba-kraj/

## Obsah
- **`index.html`** — interaktívna Leaflet mapa: 5 kategórií, filtre podľa typu a okresu, hľadanie, popupy s kontaktom, **trasa objazdu ako čiara** a **navigácia cez Google Maps**
- **`data.js`** — dáta mapy (82 prevádzok s GPS)
- **`gastro-databaza-BA-kraj.xml`** — XML export (všetky prevádzky)
- **`gastro-databaza-BA-kraj.csv`** — databáza (82 prevádzok)
- **`roadmapa-auto.md`** — návrh trasy autom na objazd (štart Petržalka)
- **`build_map.py`** — regenerácia XML + `data.js` z CSV (geokódovanie cez Nominatim/OSM)

## Kategórie
Catering / firemné stravovanie · vývarovne / catering kuchyne · táckárne / závodné jedálne · veľké reštaurácie / sály · reštauračné siete (3+ prevádzok).

## Funkcie mapy
- **Filtre** — typ prevádzky, okres, fulltext hľadanie
- **🛣️ Trasa objazdu** — čiara cez aktuálne viditeľné body (nearest-neighbor zo štartu v Petržalke)
- **🧭 Google Maps** — globálne tlačidlo otvorí trasu cez viditeľné body (max ~10 zastávok), v popupe každého bodu „Navigovať sem"

## Lokálny náhľad / regenerácia
```bash
python3 -m http.server 8791        # http://localhost:8791/
python3 build_map.py               # prečíta CSV, geokóduje, prepíše XML + data.js
```

## Zdroje
FinStat.sk (IČO, tržby), weby firiem (kontakty), OpenStreetMap/Nominatim (geokódovanie). Dáta orientačné — pred oslovením over kontakt.
