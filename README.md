# Táckárne & vývarovne — Bratislavský kraj

Interaktívna mapa a databáza veľkokapacitných stravovacích prevádzok (vývarovne / catering kuchyne + závodné jedálne / táckárne) v Bratislavskom kraji. B2B nástroj na cielené oslovenie.

## Obsah
- **`index.html`** — interaktívna Leaflet mapa (filtre podľa typu a okresu, hľadanie, popupy s kontaktom)
- **`data.js`** — dáta mapy (29 prevádzok s GPS)
- **`tackarne-vyvarovne.xml`** — XML export (vývarovne + táckárne)
- **`gastro-databaza-BA-kraj.csv`** — celá databáza (76 prevádzok: + reštaurácie, siete, catering dodávatelia)
- **`roadmapa-auto.md`** — návrh trasy autom na objazd (štart Petržalka)
- **`build_map.py`** — regenerácia XML + `data.js` z CSV (geokódovanie cez Nominatim/OSM)

## Lokálny náhľad
```bash
python3 -m http.server 8791
# http://localhost:8791/
```

## Regenerácia dát
```bash
python3 build_map.py   # prečíta CSV, geokóduje, prepíše XML + data.js
```

## Zdroje
FinStat.sk (IČO, tržby), weby firiem (kontakty), OpenStreetMap/Nominatim (geokódovanie). Dáta sú orientačné — pred oslovením over kontakt.
