#!/usr/bin/env python3
"""Geokoduje VSETKY prevadzky z CSV (BA + TT kraj) a vygeneruje XML + data.js pre Leaflet mapu."""
import csv, json, time, os, urllib.request, urllib.parse
from xml.sax.saxutils import escape

BASE = '/home/michal/gastro-ba-kraj'
CACHE = f'{BASE}/geocache.json'
JS_OUT = f'{BASE}/data.js'

# kraj kod, nazov, vstupny CSV, vystupny XML
KRAJE = [
    ('BA', 'Bratislavsky', f'{BASE}/gastro-databaza-BA-kraj.csv', f'{BASE}/gastro-databaza-BA-kraj.xml'),
    ('TT', 'Trnavsky',     f'{BASE}/gastro-databaza-TT-kraj.csv', f'{BASE}/gastro-databaza-TT-kraj.xml'),
]

# manualne GPS opravy (ICO -> lat,lon) tam, kde Nominatim trafi vedlajsiu budovu
MANUAL_GPS = {
    '31392229': (48.13244, 17.10755),  # McDonald's, Einsteinova 33 (Nominatim trafil budovu ERNI ~550m vedla)
}

cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def save_cache():
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)

def geocode(query):
    if query in cache:
        return cache[query]
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(
        {'q': query, 'format': 'json', 'limit': 1, 'countrycodes': 'sk'})
    req = urllib.request.Request(url, headers={'User-Agent': 'gastro-map/1.0 (michal.raffay@gmail.com)'})
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
    if '+' in m or '/' in m:   # multi-mesto -> centrum
        return m.split('+')[0].split('/')[0].strip()
    return m.replace('-', ', ')

def geocode_row(r):
    addr = clean_addr(r['Adresa'])
    mesto = r['Mesto_Stvrt']
    addr_l = addr.lower()
    use_addr = addr and 'doplnit' not in addr_l and not addr_l.startswith('sidlo')
    loc = None
    if use_addr:
        loc = geocode(f'{addr}, {city_clean(mesto)}, Slovakia')
    if not loc:
        loc = geocode(f'{city_clean(mesto)}, Slovakia')
    if not loc:
        loc = geocode(f"{r['Okres'].split('/')[0]}, Slovakia")
    return (loc['lat'], loc['lon']) if loc else (None, None)

def write_xml(path, kraj_nazov, rows):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f'<gastro_databaza kraj="{escape(kraj_nazov)}" typ="vsetky" pocet="{len(rows)}">\n')
        for r in rows:
            f.write(f'  <prevadzka kategoria="{escape(r["Kategoria"])}" zona="{escape(r["Zona_trasa"])}">\n')
            for tag, key in [('firma','Firma'),('ico','ICO'),('adresa','Adresa'),
                             ('mesto','Mesto_Stvrt'),('okres','Okres'),('velkost','Velkost_Trzby_Kapacita'),
                             ('telefon','Telefon'),('email','Email'),('web','Web'),('poznamka','Poznamka')]:
                f.write(f'    <{tag}>{escape(r.get(key,"") or "")}</{tag}>\n')
            if r['lat']:
                f.write(f'    <gps lat="{r["lat"]}" lon="{r["lon"]}"/>\n')
            f.write('  </prevadzka>\n')
        f.write('</gastro_databaza>\n')

all_slim = []
for kod, nazov, csv_in, xml_out in KRAJE:
    rows = list(csv.DictReader(open(csv_in, newline='', encoding='utf-8')))
    print(f'\n=== {nazov} kraj ({kod}) — zaznamov: {len(rows)} ===')
    for r in rows:
        la, lo = MANUAL_GPS.get(r['ICO']) or geocode_row(r)
        r['lat'], r['lon'] = la, lo
        flag = 'OK ' if la else '!! '
        print(f"  {flag}{r['Firma'][:42]:42} | {r['Mesto_Stvrt']}")
    ok = sum(1 for r in rows if r['lat'])
    print(f'  geokodovanych: {ok}/{len(rows)}')
    write_xml(xml_out, nazov, rows)
    for r in rows:
        all_slim.append({
            'kraj': kod, 'kat': r['Kategoria'], 'firma': r['Firma'], 'ico': r['ICO'],
            'adresa': r['Adresa'], 'mesto': r['Mesto_Stvrt'], 'okres': r['Okres'],
            'velkost': r['Velkost_Trzby_Kapacita'], 'tel': r['Telefon'], 'email': r['Email'],
            'web': r['Web'], 'zona': r['Zona_trasa'], 'pozn': r['Poznamka'],
            'lat': r['lat'], 'lon': r['lon'],
        })

with open(JS_OUT, 'w', encoding='utf-8') as f:
    f.write('const GASTRO_DATA = ' + json.dumps(all_slim, ensure_ascii=False, indent=1) + ';\n')

print(f'\nHotovo: {JS_OUT} ({len(all_slim)} prevadzok spolu)')
