# Master prompty — pridanie ďalšieho kraja do gastro mapy

Hotové: **BA** a **TT** kraj. Tento súbor obsahuje **1 spoločný master prompt** (parametrizovaný) + **sekcie pre 6 zostávajúcich krajov** (NR, TN, ZA, BB, PO, KE).

## Ako použiť
1. Otvor **nové okno Claude Code** v `/home/michal`.
2. Skopíruj **„SPOLOČNÝ MASTER PROMPT"** nižšie a hore doň doplň riadok `KRAJ = <názov>` (napr. `KRAJ = Nitriansky`).
3. Agent si sám prečíta sekciu daného kraja v tomto súbore (okresy + seed ciele) a spraví celý kraj end-to-end.
4. Rob **1 kraj = 1 okno**. Po dokončení over live a zavri.

---

## SPOLOČNÝ MASTER PROMPT (skopíruj celé)

```
KRAJ = <DOPLŇ: Nitriansky | Trenčiansky | Žilinský | Banskobystrický | Prešovský | Košický>

Si B2B research analytik + dev. Pokračuješ v existujúcom projekte „gastro mapa"
(/home/michal/gastro-ba-kraj/) — databáza VEĽKOKAPACITNEJ gastronómie + Leaflet mapa
na cielené B2B oslovenie (predaj surovín/služieb gastru). Hotové sú kraje BA a TT.
Tvoja úloha: spracovať kraj uvedený vyššie (KRAJ), rovnakým spôsobom.

KROK 0 — naštuduj projekt (NEHÁDAJ, prečítaj):
- README.md, build_map.py, deploy.sh
- gastro-databaza-TT-kraj.csv  (VZOR schémy, štýlu dát a kvality)
- MASTER_PROMPT_kraje.md → nájdi sekciu svojho KRAJA: má PRESNÝ zoznam okresov
  (hodnoty stĺpca Okres musia sedieť 1:1) + seed ciele (kotvy na research).

KROK 1 — RESEARCH (web search: FinStat.sk, weby firiem, ORSR, mapy):
Nájdi veľkokapacitné gastro ciele naprieč 5 kategóriami a VŠETKÝMI okresmi kraja.
Kategórie (POUŽI presne tieto stringy v stĺpci Kategoria):
  • "Catering dodavatel"            — cateringové/firemné stravovanie, event catering
  • "Vyvaren / catering kuchyna"    — vývarovne, dodávatelia závodného/školského stravovania
  • "Tackaren / zavodna jedalen"    — závodné jedálne veľkých zamestnávateľov (fabriky,
                                       automotive), nemocnice (vlastná kuchyňa), univerzity
  • "Velka restauracia / banketova sala" — 100+ miest, svadobné/banketové sály,
                                       hotely/rezorty/kúpele s eventovými priestormi
  • "Restauracna siet (3+ prevadzok)"    — siete 3+; KAŽDÚ daj 1× na SÍDLE firmy,
                                       NIE pobočky (1 bod = 1 sídlo)
Cieľ ~30–50 overených záznamov. Seed ciele zo sekcie kraja over a doplň o ďalšie.

KONVENCIE (dodrž, inak sa to rozbije):
- Text BEZ diakritiky (ASCII): "trzby 8,33 mil EUR (2024), 100-149 zam".
- ICO = reálne 8-ciferné z FinStat/ORSR; ak neoveríš, daj "doplnit ORSR".
  ŽIADNE vymyslené IČO/tržby/kontakty — radšej "" alebo "doplnit".
- Okres = PRESNE jedna z hodnôt zo zoznamu okresov tohto kraja (ASCII, bez diakritiky).
- Velkost_Trzby_Kapacita = tržby (rok) z FinStat ALEBO kapacita/počet zamestnancov/jedál.
- Telefon/Email/Web = reálne z webu firmy; inak "". Web bez https:// a www. (napr. "firma.sk").
- Zona_trasa = "" (alebo kód okresu). Poznamka = krátka B2B pozn.; "SILNY CIEL" pri top objemoch.
- Len VEĽKOKAPACITNÉ ciele (žiadne malé kaviarne <80 miest, pokiaľ nie sú súčasťou siete).

KROK 2 — CSV:
Vytvor /home/michal/gastro-ba-kraj/gastro-databaza-<CODE>-kraj.csv
s IDENTICKOU hlavičkou ako TT CSV (CODE = 2-písmenový kód kraja zo sekcie):
Kategoria,Firma,ICO,Adresa,Mesto_Stvrt,Okres,Velkost_Trzby_Kapacita,Telefon,Email,Web,Zona_trasa,Poznamka
Každé pole v úvodzovkách. Adresa = ulica+číslo kde vieš (lepšie geokódovanie), inak "doplnit".

KROK 3 — integrácia do buildu:
V build_map.py do zoznamu KRAJE pridaj riadok (presný formát ako BA/TT):
  ('<CODE>', '<NazovKraja>', f'{BASE}/gastro-databaza-<CODE>-kraj.csv', f'{BASE}/gastro-databaza-<CODE>-kraj.xml'),
[LEN ak je KRAJ = Košický: pridaj aj mapovanie mestských častí Košíc na okresy
 Kosice I–IV (vzor: existujúci BA_OKRES pre Bratislavu) a aplikuj ho v build slučke pre 'KE'.]

KROK 4 — BUILD + KONTROLA:
- python3 build_map.py   (geokóduje cez Nominatim, ~1s/dopyt)
- Over (napíš si malý python check):
  • každý Okres v nových dátach ∈ zoznam okresov kraja (žiadny „MIMO")
  • všetky body majú GPS (lat != null)
  • spot-check 3–4 top ciele — GPS padá do správneho mesta/okresu (nie inde v SR)

KROK 5 — CACHE + DEPLOY:
- V index.html zvýš verziu: data.js?v=2026XXXX<písmeno> (cache-bust).
- bash deploy.sh
- Over live: curl data.js obsahuje nové firmy a "kraj": "<CODE>".
- index.html UŽ obsahuje tento kraj v selektore Kraj, v zozname okresov (SK_OKRESY) aj
  štart bázu (krajské mesto) — NETREBA ho meniť okrem cache verzie.

KROK 6 — zápis výstupu:
- Krátky súhrn do claude_projects alebo do tohto repa: počet cieľov, top 5 podľa objemu,
  čo treba ešte doplniť (doplnit ORSR).

PRAVIDLÁ: 1 úloha naraz, pred „hotovo" over end-to-end (build + live curl), žiadne
halucinácie. Pri deploy je to GitHub Pages (mixall11/gastro-ba-kraj) — push cez deploy.sh.
```

---

## Sekcie krajov (okresy = presné hodnoty stĺpca Okres + seed ciele)

### Nitriansky  (CODE = NR, štart báza: Nitra)
**Okresy (7):** Komarno, Levice, Nitra, Nove Zamky, Sala, Topolcany, Zlate Moravce
**Seed ciele (over a doplň):**
- Nitra: **Jaguar Land Rover Slovakia** (automobilka, tisíce zam. → závodná jedáleň, SILNY CIEL) · priemyselný park Nitra-Sever (dodávatelia) · **Fakultná nemocnica Nitra** · **SPU + UKF** (univerzity, menzy) · agrokomplex (eventy)
- Šaľa: **Duslo Šaľa** (chemička, veľký zamestnávateľ → jedáleň)
- Levice: **Slovenské elektrárne — AE Mochovce** (jadrová elektráreň, jedáleň) · nemocnica Levice
- Nové Zámky: nemocnica (Forlife) · potravinárstvo
- Komárno: lodenice (SLKB) · nemocnica · termálne kúpele
- Topoľčany: **Heineken / Topvar** (pivovar) · nemocnica
- cateringy a svadobné sály v okolí Nitry (vinohradnícky región)

### Trenčiansky  (CODE = TN, štart báza: Trenčín)
**Okresy (9):** Banovce nad Bebravou, Ilava, Myjava, Nove Mesto nad Vahom, Partizanske, Povazska Bystrica, Prievidza, Puchov, Trencin
**Seed ciele:**
- Púchov: **Continental Matador Rubber** (pneumatikáreň, 5000+ zam. → závodná jedáleň, SILNY CIEL)
- Trenčín: **Fakultná nemocnica Trenčín** · **TnUAD** (univerzita) · priemysel
- Prievidza: **Brose Prievidza** · Hornonitrianske bane (HBP) · nemocnica
- Ilava/Dubnica n. Váhom: **ZVS / ZTS** strojárstvo
- Nové Mesto nad Váhom: **Emerson**, priemyselné parky
- Považská Bystrica: strojárstvo · nemocnica
- Partizánske, Bánovce, Myjava: regionálne fabriky + sály

### Žilinský  (CODE = ZA, štart báza: Žilina)
**Okresy (11):** Bytca, Cadca, Dolny Kubin, Kysucke Nove Mesto, Liptovsky Mikulas, Martin, Namestovo, Ruzomberok, Turcianske Teplice, Tvrdosin, Zilina
**Seed ciele:**
- Žilina: **KIA Slovakia** (Teplička nad Váhom, automobilka, tisíce zam. → jedáleň, SILNY CIEL) · **UNIZA** · **FN Žilina**
- Martin: **Univerzitná nemocnica Martin** · **JLF UK**
- Ružomberok: **Mondi SCP** (papiereň) · **Ústredná vojenská nemocnica** · Katolícka univerzita
- Kysucké Nové Mesto: **Schaeffler Kysuce / INA** (ložiská, veľký zamestnávateľ)
- Liptovský Mikuláš: **Tatralandia / Aquapark**, **Jasná** hotely (rezorty, catering) · Akadémia OS
- Čadca, Dolný Kubín, Námestovo, Tvrdošín: regionálne fabrexport. + nemocnice + hotely (Orava)

### Banskobystrický  (CODE = BB, štart báza: Banská Bystrica)
**Okresy (13):** Banska Bystrica, Banska Stiavnica, Brezno, Detva, Krupina, Lucenec, Poltar, Revuca, Rimavska Sobota, Velky Krtis, Zvolen, Zarnovica, Ziar nad Hronom
**Seed ciele:**
- Banská Bystrica: **FNsP F. D. Roosevelta** (veľká nemocnica, SILNY CIEL) · **UMB** (univerzita) · cateringy
- Žiar nad Hronom: **Slovalco / Nemak** (hliník/automotive → jedáleň)
- Detva: **PPS Group** (strojárstvo)
- Zvolen: **Technická univerzita TUZVO** · **Nemocnica Zvolen** · Bučina
- Lučenec, Rimavská Sobota, Brezno: regionálne nemocnice + sály
- Banská Štiavnica, Krupina, Veľký Krtíš: hotely/eventy (turizmus, vinohrady)

### Prešovský  (CODE = PO, štart báza: Prešov)
**Okresy (13):** Bardejov, Humenne, Kezmarok, Levoca, Medzilaborce, Poprad, Presov, Sabinov, Snina, Stara Lubovna, Stropkov, Svidnik, Vranov nad Toplou
**Seed ciele:**
- Prešov: **FNsP J. A. Reimana** (nemocnica) · **Prešovská univerzita** · priemysel
- Poprad: **Tatry turizmus** — Aqua City, Grand Hotel Kempinski (Štrbské Pleso), hotely Vysoké Tatry (rezorty/catering, SILNY CIEL) · **Whirlpool / Tatramat** · nemocnica Poprad
- Humenné: **Chemes / Nexis Fibers** · nemocnica
- Bardejov: **Bardejovské kúpele** (kúpele, catering) · nemocnica
- Kežmarok, Stará Ľubovňa, Vranov n. Topľou, Svidník, Snina: regionálne nemocnice + sály

### Košický  (CODE = KE, štart báza: Košice)
**Okresy (11):** Gelnica, Kosice I, Kosice II, Kosice III, Kosice IV, Kosice-okolie, Michalovce, Roznava, Sobrance, Spisska Nova Ves, Trebisov
**POZOR:** mesto Košice = 4 okresy (Kosice I–IV). Každú košickú prevádzku zaraď do správneho
okresu podľa mestskej časti (vzor: BA_OKRES pre Bratislavu). Hrubé delenie:
- Kosice I — Staré Mesto, Sever, Džungľa, Kavečany, Sídlisko Ťahanovce, Ťahanovce
- Kosice II — Západ (KVP), Myslava, Pereš, Lorinčík, Luník IX, Sídlisko Ťahanovce(časť), Šaca, Poľov, Barca, Železiarne (U.S. Steel je v Šaci → Kosice II)
- Kosice III — Dargovských hrdinov (Furča), Košická Nová Ves
- Kosice IV — Juh, Nad jazerom, Krásna, Šebastovce, Vyšné Opátske
**Seed ciele:**
- Košice: **U.S. Steel Košice** (oceliareň, ~10 000 zam. → obrovská závodná jedáleň, NAJVÄČŠÍ CIEL; okres Kosice II/Šaca) · **UNLP — Univerzitná nemocnica L. Pasteura** · **UPJŠ + TUKE** (univerzity, menzy) · **BSH Drives**, priemyselné parky · veľké hotely/sály (DoubleTree, Yasmin, eventové centrá)
- Spišská Nová Ves: **Embraco** · nemocnica · Spiš turizmus
- Michalovce, Trebišov, Rožňava: regionálne nemocnice + svadobné sály
- Gelnica, Sobrance: menšie, regionálne ciele
