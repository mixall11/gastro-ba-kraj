#!/usr/bin/env python3
"""Geokóduje VŠETKY prevádzky z CSV a vygeneruje XML + data.js pre Leaflet mapu."""
import csv, json, time, os, urllib.request, urllib.parse
from xml.sax.saxutils import escape

BASE = '/home/michal/gastro-ba-kraj'
CSV_IN = f'{BASE}/gastro-databaza-BA-kraj.csv'
CACHE = f'{BASE}/geocache.json'
XML_OUT = f'{BASE}/gastro-databaza-BA-kraj.xml'
JS_OUT = f'{BASE}/data.js'

cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def save_cache():
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)

def geocode(query):
    if query in cache:
        return cache[query]
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(
        {'q': query, 'format': 'json', 'limit': 1, 'countrycodes': 'sk'})
    req = urllib.request.Request(url, headers={'User-Agent': 'gastro-ba-map/1.0 (michal.raffay@gmail.com)'})
    res = None
    try:
        data = json.load(urllib.request.urlopen(req, timeout=20))
        if data:
            res = {'lat': float(data[0]['lat']), 'lon': float(data[0]['lon'])}
    except Exception as e:
        print('  ! geocode error:', e)
    cache[query] = res
    save_cache()
    time.sleep(1.1)
    return res

def clean_addr(a):
    return a.split('(')[0].strip().rstrip(',')

def city_clean(m):
    # multi-mesto (Minit "Bratislava + okresy") -> centrum BA
    if '+' in m or '/' in m:
        return 'Bratislava'
    return m.replace('-', ', ')

rows = list(csv.DictReader(open(CSV_IN, newline='', encoding='utf-8')))
print(f'Záznamov spolu: {len(rows)}')

out = []
for r in rows:
    addr = clean_addr(r['Adresa'])
    mesto = r['Mesto_Stvrt']
    addr_l = addr.lower()
    # adresu nepoužij ak je to sídlo mimo prevádzky alebo nedoplnená
    use_addr = addr and 'doplnit' not in addr_l and not addr_l.startswith('sidlo')
    print(f"Geo: {r['Firma'][:38]:38} | {addr[:28] if use_addr else '(mesto)':28} | {mesto}")
    loc = None
    if use_addr:
        loc = geocode(f'{addr}, {city_clean(mesto)}, Slovakia')
    if not loc:
        loc = geocode(f'{city_clean(mesto)}, Slovakia')
    if not loc:
        loc = geocode(f"{r['Okres'].split('/')[0]}, Slovakia")
    rec = dict(r)
    rec['lat'] = loc['lat'] if loc else None
    rec['lon'] = loc['lon'] if loc else None
    out.append(rec)

ok = sum(1 for r in out if r['lat'])
print(f'Geokódovaných: {ok}/{len(out)}')

# --- XML (kompletný export) ---
with open(XML_OUT, 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(f'<gastro_databaza kraj="Bratislavsky" typ="vsetky" pocet="{len(out)}">\n')
    for r in out:
        f.write(f'  <prevadzka kategoria="{escape(r["Kategoria"])}" zona="{escape(r["Zona_trasa"])}">\n')
        for tag, key in [('firma','Firma'),('ico','ICO'),('adresa','Adresa'),
                         ('mesto','Mesto_Stvrt'),('okres','Okres'),('velkost','Velkost_Trzby_Kapacita'),
                         ('telefon','Telefon'),('email','Email'),('web','Web'),('poznamka','Poznamka')]:
            f.write(f'    <{tag}>{escape(r.get(key,"") or "")}</{tag}>\n')
        if r['lat']:
            f.write(f'    <gps lat="{r["lat"]}" lon="{r["lon"]}"/>\n')
        f.write('  </prevadzka>\n')
    f.write('</gastro_databaza>\n')

# --- data.js ---
slim = [{
    'kat': r['Kategoria'], 'firma': r['Firma'], 'ico': r['ICO'], 'adresa': r['Adresa'],
    'mesto': r['Mesto_Stvrt'], 'okres': r['Okres'], 'velkost': r['Velkost_Trzby_Kapacita'],
    'tel': r['Telefon'], 'email': r['Email'], 'web': r['Web'], 'zona': r['Zona_trasa'],
    'pozn': r['Poznamka'], 'lat': r['lat'], 'lon': r['lon'],
} for r in out]
with open(JS_OUT, 'w', encoding='utf-8') as f:
    f.write('const GASTRO_DATA = ' + json.dumps(slim, ensure_ascii=False, indent=1) + ';\n')

print('Hotovo:', XML_OUT, JS_OUT)
