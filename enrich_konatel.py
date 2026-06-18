#!/usr/bin/env python3
"""Obohatí databázu o meno konateľa / manažéra z ORSR.sk podľa IČO.

Výstup:
  - konatel_cache.json  — cache podľa IČO (aby sa neopakovalo)
  - všetky CSV dostanú stĺpec Konatel (ak ešte nemajú)
  - data.js dostane pole "konatel" pri každom zázname
"""
import csv, json, re, time, os, urllib.request, urllib.error, urllib.parse, sys

BASE = '/home/michal/gastro-ba-kraj'
CACHE_FILE = f'{BASE}/konatel_cache.json'
DATA_JS = f'{BASE}/data.js'

KRAJE_CSV = [
    f'{BASE}/gastro-databaza-BA-kraj.csv',
    f'{BASE}/gastro-databaza-TT-kraj.csv',
    f'{BASE}/gastro-databaza-TN-kraj.csv',
    f'{BASE}/gastro-databaza-NR-kraj.csv',
    f'{BASE}/gastro-databaza-BB-kraj.csv',
    f'{BASE}/gastro-databaza-ZA-kraj.csv',
    f'{BASE}/gastro-databaza-PO-kraj.csv',
    f'{BASE}/gastro-databaza-KE-kraj.csv',
]

HEADERS = {'User-Agent': 'gastro-map/1.0 (michal.raffay@gmail.com)'}
SLEEP = 1.3  # Nominatim-style slušnosť voči ORSR

cache = json.load(open(CACHE_FILE, encoding='utf-8')) if os.path.exists(CACHE_FILE) else {}

def save_cache():
    json.dump(cache, open(CACHE_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def fetch(url, encoding='windows-1250'):
    req = urllib.request.Request(url.replace('&amp;', '&'), headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode(encoding, errors='replace')
    except Exception as e:
        print(f'    ! chyba pri {url}: {e}')
        return None

TITLE_RE = re.compile(
    r'<span class=.ro.>\s*((?:Ing|Mgr|JUDr|RNDr|MUDr|PhDr|Bc|MBA|MSc|PhD|Doc|Prof)\.)\s*</span>\s*'
    r'<a[^>]+href=["\']?hladaj_osoba\.asp\?([^"\'> ]+)',
    re.IGNORECASE,
)
LINK_RE = re.compile(
    r'<a[^>]+href=["\']?hladaj_osoba\.asp\?([^"\'> ]+)',
    re.IGNORECASE,
)

def extract_names(detail_html):
    """Vráti zoznam konateľov z detail stránky ORSR."""
    # Orezáme na sekciu Štatutárny orgán → do najbližšieho </table></table>
    m = re.search(r'[Šš]tatut[áa]rny\s+org[áa]n', detail_html)
    if not m:
        return []
    section = detail_html[m.start(): m.start() + 6000]

    names = []
    pos = 0
    while True:
        m_title = TITLE_RE.search(section, pos)
        m_link  = LINK_RE.search(section, pos)
        if not m_link:
            break
        if m_title and m_title.start() < m_link.start():
            title = m_title.group(1)
            params_str = m_title.group(2)
            pos = m_title.end()
        else:
            title = ''
            params_str = m_link.group(1)
            pos = m_link.end()

        params = dict(urllib.parse.parse_qsl(params_str))
        meno = params.get('MENO', '').strip()
        pr   = params.get('PR', '').strip()
        if meno and pr:
            full = f'{title} {meno} {pr}'.strip() if title else f'{meno} {pr}'
            names.append(full)

    # deduplikácia (konateľ môže byť citovaný 2× v zmenách)
    seen, result = set(), []
    for n in names:
        key = n.lower()
        if key not in seen:
            seen.add(key)
            result.append(n)
    return result

def orsr_lookup(ico):
    """Vráti reťazec so menom/mená konateľa alebo '' ak nenájde."""
    search_url = f'http://orsr.sk/hladaj_ico.asp?ICO={ico}&SID=0&ROK=0'
    html = fetch(search_url)
    if not html:
        return ''

    links = re.findall(r'href="(vypis\.asp\?[^"]+)"', html, re.IGNORECASE)
    if not links:
        return ''  # firma nie je v ORSR (živnostník, zahraničná...)

    detail_url = f'http://orsr.sk/{links[0]}'
    detail = fetch(detail_url)
    if not detail:
        return ''

    names = extract_names(detail)
    return ', '.join(names) if names else ''

def lookup(ico):
    """Cache-first lookup."""
    ico = ico.strip()
    if not ico:
        return ''
    if ico in cache:
        return cache[ico]
    print(f'  IČO {ico} ... ', end='', flush=True)
    result = orsr_lookup(ico)
    print(result or '—')
    cache[ico] = result
    save_cache()
    time.sleep(SLEEP)
    return result

# ─────────────────────────────────────────────
# 1. Obohaciť CSVs
# ─────────────────────────────────────────────
def enrich_csvs():
    for path in KRAJE_CSV:
        if not os.path.exists(path):
            continue
        rows = list(csv.DictReader(open(path, newline='', encoding='utf-8')))
        if not rows:
            continue
        kraj = os.path.basename(path).split('-')[2].upper()
        print(f'\n=== {kraj} kraj: {len(rows)} firiem ===')

        for r in rows:
            if r.get('Konatel'):  # už má hodnotu → preskočiť
                continue
            r['Konatel'] = lookup(r.get('ICO', ''))

        # zapísať späť
        fields = list(rows[0].keys())
        if 'Konatel' not in fields:
            fields.append('Konatel')
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f'  Uložené: {path}')

# ─────────────────────────────────────────────
# 2. Aktualizovať data.js
# ─────────────────────────────────────────────
def update_data_js():
    print('\n=== Aktualizácia data.js ===')
    src = open(DATA_JS, encoding='utf-8').read()
    m = re.match(r'const GASTRO_DATA = (\[.*\]);?\s*$', src, re.DOTALL)
    if not m:
        print('! Nepodarilo sa parsovať data.js')
        return
    data = json.loads(m.group(1))

    for entry in data:
        ico = entry.get('ico', '')
        if not entry.get('konatel') and ico in cache:
            entry['konatel'] = cache[ico] or ''

    with open(DATA_JS, 'w', encoding='utf-8') as f:
        f.write('const GASTRO_DATA = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    filled = sum(1 for e in data if e.get('konatel'))
    print(f'  Hotovo: {filled}/{len(data)} záznamov má konateľa')

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == '__main__':
    test_mode = '--test' in sys.argv
    if test_mode:
        # Otestuj prvých 5 IČO z BA CSV
        rows = list(csv.DictReader(open(KRAJE_CSV[0], newline='', encoding='utf-8')))
        print('=== TEST MODE — prvých 5 firiem ===')
        for r in rows[:5]:
            ico = r['ICO']
            result = lookup(ico)
            print(f'  {r["Firma"][:40]:40} → {result or "—"}')
    else:
        enrich_csvs()
        update_data_js()
        print('\nDone. Spusti build_map.py ak chceš pregenerovať aj XML.')
