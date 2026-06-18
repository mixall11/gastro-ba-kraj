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
    ('TN', 'Trenciansky',  f'{BASE}/gastro-databaza-TN-kraj.csv', f'{BASE}/gastro-databaza-TN-kraj.xml'),
    ('NR', 'Nitriansky',   f'{BASE}/gastro-databaza-NR-kraj.csv', f'{BASE}/gastro-databaza-NR-kraj.xml'),
    ('BB', 'Banskobystricky', f'{BASE}/gastro-databaza-BB-kraj.csv', f'{BASE}/gastro-databaza-BB-kraj.xml'),
    ('ZA', 'Zilinsky',     f'{BASE}/gastro-databaza-ZA-kraj.csv', f'{BASE}/gastro-databaza-ZA-kraj.xml'),
    ('PO', 'Presovsky',    f'{BASE}/gastro-databaza-PO-kraj.csv', f'{BASE}/gastro-databaza-PO-kraj.xml'),
    ('KE', 'Kosicky',      f'{BASE}/gastro-databaza-KE-kraj.csv', f'{BASE}/gastro-databaza-KE-kraj.xml'),
]

# manualne GPS opravy (ICO -> lat,lon) tam, kde Nominatim trafi vedlajsiu budovu
MANUAL_GPS = {
    # McDonald's ICO 31392229 ZRUSENY z MANUAL_GPS — firma ma viacero prevadzok v roznych krajoch
    # BA coords seednute do geocache["Einsteinova 33, Bratislava, Petrzalka, Slovakia"]
    # PO coords seednute do geocache["Vihorlatska 13591/2B, Presov, Slovakia"]
    '35826487': (48.15663, 17.89696),  # Duslo Sala (adresa "Administrativna budova ev.c.1236" trafila vychod SR)
    '36709557': (49.10310, 18.31760),  # Continental Tires Slovakia Puchov (Nominatim trafil centrum Puchova ~2,4km, realny zavod je v Hornych Kockovciach)
    '31701931': (48.74745, 21.20827),  # Hotel Bankov Kosice (adresa "Dolny Bankov 2" padla na centroid Kosice-Sever; realny hotel v lese Bankov)
    '36200514': (48.67892, 21.28906),  # VAMEX Kosice, Lubina 1 (Nad jazerom; "Kosice-Sever" centroid bol zly)
}

# mestske casti BA -> oficialny okres Bratislava I-V (pre BA kraj)
BA_OKRES = {
    'Bratislava-Stare Mesto':'Bratislava I',
    'Bratislava-Ruzinov':'Bratislava II','Bratislava-Vrakuna':'Bratislava II','Bratislava-Podunajske Biskupice':'Bratislava II',
    'Bratislava-Nove Mesto':'Bratislava III','Bratislava-Raca':'Bratislava III','Bratislava-Kramare':'Bratislava III',
    'Bratislava-Karlova Ves':'Bratislava IV','Bratislava-Dubravka':'Bratislava IV','Bratislava-Devinska Nova Ves':'Bratislava IV',
    'Bratislava-Petrzalka':'Bratislava V',
    'Bratislava':'Bratislava I',
}

# mestske casti Kosice -> oficialny okres Kosice I-IV (pre KE kraj)
KE_OKRES = {
    'Kosice-Stare Mesto':'Kosice I','Kosice-Sever':'Kosice I','Kosice-Dzungla':'Kosice I',
    'Kosice-Kavecany':'Kosice I','Kosice-Tahanovce':'Kosice I','Kosice-Sidlisko Tahanovce':'Kosice I',
    'Kosice-Zapad':'Kosice II','Kosice-KVP':'Kosice II','Kosice-Myslava':'Kosice II',
    'Kosice-Peres':'Kosice II','Kosice-Lorincik':'Kosice II','Kosice-Lunik IX':'Kosice II',
    'Kosice-Saca':'Kosice II','Kosice-Polov':'Kosice II','Kosice-Barca':'Kosice II',
    'Kosice-Dargovskych hrdinov':'Kosice III','Kosice-Furca':'Kosice III','Kosice-Kosicka Nova Ves':'Kosice III',
    'Kosice-Juh':'Kosice IV','Kosice-Nad jazerom':'Kosice IV','Kosice-Krasna':'Kosice IV',
    'Kosice-Sebastovce':'Kosice IV','Kosice-Vysne Opatske':'Kosice IV',
    'Kosice':'Kosice I',
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
                             ('telefon','Telefon'),('email','Email'),('web','Web'),
                             ('konatel','Konatel'),('poznamka','Poznamka')]:
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
        if kod == 'BA':
            r['Okres'] = BA_OKRES.get(r['Mesto_Stvrt'], r['Okres'])
        if kod == 'KE':
            r['Okres'] = KE_OKRES.get(r['Mesto_Stvrt'], r['Okres'])
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
            'konatel': r.get('Konatel', ''),
            'lat': r['lat'], 'lon': r['lon'],
        })

with open(JS_OUT, 'w', encoding='utf-8') as f:
    f.write('const GASTRO_DATA = ' + json.dumps(all_slim, ensure_ascii=False, indent=1) + ';\n')

print(f'\nHotovo: {JS_OUT} ({len(all_slim)} prevadzok spolu)')
