import os
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# URL delle sorgenti ufficiali
URL_SKY_UK = "https://www.open-epg.com/files/unitedkingdom.xml.gz"
URL_DAZN_IT = "https://www.open-epg.com/files/italy8.xml.gz"
URL_EPG_IT1 = "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz"

def download_and_parse_xml(url):
    """Scarica e decomprime un file XML.GZ remoto in sicurezza"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=25) as response:
            with gzip.open(response, 'rt', encoding='utf-8', errors='ignore') as f:
                return ET.parse(f).getroot()
    except Exception as e:
        print(f"Avviso download/parsing {url}: {e}")
        return None

def add_programme(root, ch_id, start_dt, stop_dt, title, desc):
    """Aggiunge un tag <programme> formattato correttamente"""
    prog = ET.SubElement(root, "programme", attrib={
        "start": start_dt.strftime("%Y%m%d%H%M%S +0100"),
        "stop": stop_dt.strftime("%Y%m%d%H%M%S +0100"),
        "channel": ch_id
    })
    ET.SubElement(prog, "title", attrib={"lang": "it"}).text = title
    ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = desc

def generate_epg():
    root = ET.Element("tv", attrib={"generator-info-name": "Ultimate-Hybrid-EPG"})
    now = datetime.now()

    # 1. DAZN (Zonadazn 2, 3, 4)
    dazn_root = download_and_parse_xml(URL_DAZN_IT)
    if dazn_root is not None:
        try:
            for channel in dazn_root.findall("channel"):
                ch_id = channel.get("id", "").lower()
                if "dazn" in ch_id:
                    root.append(channel)
            for programme in dazn_root.findall("programme"):
                ch_ref = programme.get("channel", "").lower()
                if "dazn" in ch_ref:
                    root.append(programme)
        except Exception as e:
            print(f"Errore DAZN: {e}")

    # 2. SKY SPORTS FOOTBALL UK E SKY SPORT 1
    sky_root = download_and_parse_xml(URL_SKY_UK)
    it1_root = download_and_parse_xml(URL_EPG_IT1)
    
    for source in [it1_root, sky_root]:
        if source is not None:
            try:
                for channel in source.findall("channel"):
                    ch_id = channel.get("id", "").lower()
                    ch_name = "".join(channel.itertext()).lower()
                    if "skysportuno" in ch_id or "sky sport uno" in ch_name or "skysportsfootball" in ch_id or "football" in ch_id:
                        root.append(channel)
                for programme in source.findall("programme"):
                    ch_ref = programme.get("channel", "").lower()
                    if "skysportuno" in ch_ref or "skysportsfootball" in ch_ref:
                        root.append(programme)
            except Exception as e:
                print(f"Errore Sky Sport channels: {e}")

    # 3. CANALI SPECIALI, LOCALI E SKY PRIMAFILA (Vetrina + Da 1 a 18 + 4K)
    channels_data = {
        "man-ga.it": {
            "name": "Man-Ga",
            "shows": [
                ("Lady Georgie - Anime Classic", "Le avventure, i drammi e i romanzi nella Londra del XIX secolo con Georgie."),
                ("Capitan Harlock - Spazio Pirata", "Le epiche battaglie dell'Arcadia contro le Mazoniane per la salvezza della Terra."),
                ("Gotrinitron / Robot Storici", "I grandi classici dei robottoni giapponesi che hanno fatto la storia dell'animazione."),
                ("Anime Night - Selezione Cult", "Gli episodi più amati e le pietre miliari della golden age degli anime giapponesi.")
            ]
        },
        "TopCalcio24.it": {
            "name": "Top Calcio 24 Hd",
            "shows": [
                ("Apericalcio", "Un piacevole momento per gli appassionati di calcio di ogni età ed esperienza."),
                ("Azzurro Italia TG", "Servizi, approfondimenti, interviste e ultime notizie sul mondo del calciomercato italiano."),
                ("Alta quota", "Interviste, novità, servizi e tutte le ultime notizie relative al mondo del calcio."),
                ("Diretta stadio", "Commenti, collegamenti e dibattiti in tempo reale sulla giornata calcistica.")
            ]
        },
        "Canale21.it": {
            "name": "Canale 21",
            "shows": [
                ("Tg Campania - Informazione", "Notiziario regionale in diretta con approfondimenti di cronaca e attualità."),
                ("Il Bello del Calcio", "La storica trasmissione sportiva dedicata alle squadre campane e al grande calcio."),
                ("Campania Sport", "Dibattiti, collegamenti e moviola in tempo reale sui temi del campionato."),
                ("Spazio Aperto - Rubrica", "Approfondimenti culturali, sociali e di costume del territorio.")
            ]
        },
        "AmazonPrimeVideo.it": {
            "name": "Eventi Calcio Amazon Prime",
            "is_prime": True
        },
        # --- CONFIGURAZIONE SKY PRIMAFILA (Vetrina + 1 a 18) ---
        "Primafila.it": {
            "name": "Vetrina Sky Primafila",
            "movie": "Vetrina Sky Primafila - Lista film in primo piano",
            "desc": "Panoramica completa delle prime visioni e dei titoli in programmazione su Sky Primafila."
        },
        "Primafila1HD.it": {
            "name": "PRIMAFILA 1",
            "movie": "BLACK PHONE 2 2025",
            "desc": "Sky Primafila Premiere 1 HD - Prima visione cinematografica."
        },
        "Primafila2HD.it": {
            "name": "PRIMAFILA 2",
            "movie": "SUPERMAN 2025",
            "desc": "Sky Primafila Premiere 2 HD - Prima visione cinematografica."
        },
        "Primafila3HD.it": {
            "name": "PRIMAFILA 3",
            "movie": "MISSION IMPOSSIBLE 2025",
            "desc": "Sky Primafila Premiere 3 HD - Prima visione cinematografica."
        },
        "Primafila4HD.it": {
            "name": "PRIMAFILA 4",
            "movie": "WEAPONS 2025",
            "desc": "Sky Primafila Premiere 4 HD - Prima visione cinematografica."
        },
        "Primafila5HD.it": {
            "name": "PRIMAFILA 5",
            "movie": "TROLL 2025",
            "desc": "Sky Primafila Premiere 5 HD - Prima visione cinematografica."
        },
        "Primafila6.it": {
            "name": "PRIMAFILA 6",
            "movie": "E COLPA NOSTRA 2025",
            "desc": "Sky Primafila Premiere 6 HD - Prima visione cinematografica."
        },
        "Primafila7.it": {
            "name": "PRIMAFILA 7",
            "movie": "LILO E STITCH 2025",
            "desc": "Sky Primafila Premiere 7 HD - Prima visione cinematografica."
        },
        "Primafila8.it": {
            "name": "PRIMAFILA 8",
            "movie": "NOBODY 2 2025",
            "desc": "Sky Primafila Premiere 8 HD - Prima visione cinematografica."
        },
        "Primafila9.it": {
            "name": "PRIMAFILA 9",
            "movie": "JURASSIC WORLD 2025",
            "desc": "Sky Primafila Premiere 9 HD - Prima visione cinematografica."
        },
        "Primafila10.it": {
            "name": "PRIMAFILA 10",
            "movie": "THE CONJURING IL RITO 2025",
            "desc": "Sky Primafila Premiere 10 HD - Prima visione cinematografica."
        },
        "Primafila11.it": {
            "name": "PRIMAFILA 11",
            "movie": "LILO E STITCH 2025",
            "desc": "Sky Primafila 11 - Film in programmazione continuativa."
        },
        "Primafila12.it": {
            "name": "PRIMAFILA 12",
            "movie": "LILO E STITCH 2025",
            "desc": "Sky Primafila 12 - Film in programmazione continuativa."
        },
        "Primafila13.it": {
            "name": "PRIMAFILA 13",
            "movie": "LILO E STITCH 2025",
            "desc": "Sky Primafila 13 - Film in programmazione continuativa."
        },
        "Primafila14.it": {
            "name": "PRIMAFILA 14",
            "movie": "TROLL 2 2025",
            "desc": "Sky Primafila 14 - Film in programmazione continuativa."
        },
        "Primafila15.it": {
            "name": "PRIMAFILA 15",
            "movie": "TROLL 2 2025",
            "desc": "Sky Primafila 15 - Film in programmazione continuativa."
        },
        "Primafila16.it": {
            "name": "PRIMAFILA 16",
            "movie": "TROLL 2 2025",
            "desc": "Sky Primafila 16 - Film in programmazione continuativa."
        },
        "Primafila17.it": {
            "name": "PRIMAFILA 17",
            "movie": "TROLL 2 2025",
            "desc": "Sky Primafila 17 - Film in programmazione continuativa."
        },
        "Primafila18.it": {
            "name": "PRIMAFILA 18",
            "movie": "TROLL 2 2025",
            "desc": "Sky Primafila 18 - Film in programmazione continuativa."
        },
        # --- CONFIGURAZIONE SKY PRIMAFILA 4K ---
        "Primafila-4k.it": {
            "name": "Vetrina Sky Primafila 4k",
            "movie": "Vetrina Sky Primafila - Lista film in primo piano",
            "desc": "Panoramica completa delle prime visioni e dei titoli in programmazione su Sky Primafila."
        },
        "Primafila1-4k.it": {
            "name": "PRIMAFILA 1 4K",
            "movie": "SNAKE EYES: G.I. JOE - LE ORIGINI • THE SUICIDE SQUAD - MISSIONE SUICIDA",
            "desc": "In programmazione:\n• SNAKE EYES: G.I. JOE - LE ORIGINI\n• THE SUICIDE SQUAD - MISSIONE SUICIDA"
        },
        "Primafila2-4k.it": {
            "name": "PRIMAFILA 2 4K",
            "movie": "BLACK WIDOW • JUNGLE CRUISE",
            "desc": "In programmazione:\n• BLACK WIDOW\n• JUNGLE CRUISE"
        },
        "Primafila3-4k.it": {
            "name": "PRIMAFILA 3 4K",
            "movie": "FAST E FURIOS 9 - THE FAST SAGA",
            "desc": "Sky Primafila Premiere 3 HD - Prima visione cinematografica."
        },
        "Primafila4-4k.it": {
            "name": "PRIMAFILA 4 4K",
            "movie": "RITORNO AL CRIMINE • MIA MOGLIE È UN FANTASMA • I CROODS 2 - UNA NUOVA ERA",
            "desc": "In programmazione:\n• RITORNO AL CRIMINE\n• MIA MOGLIE È UN FANTASMA\n• I CROODS 2 - UNA NUOVA ERA"
        },
        "Primafila5-4k.it": {
            "name": "PRIMAFILA 5 4K",
            "movie": "SPACE JAM - NEW LEGENDS • PETER RABBIT 2: UN BIRBANTE IN FUGA",
            "desc": "In programmazione:\n• SPACE JAM - NEW LEGENDS\n• PETER RABBIT 2: UN BIRBANTE IN FUGA"
        },
        "Primafila6-4k.it": {
            "name": "PRIMAFILA 6 4K",
            "movie": "L'ULTIMO MERCENARIO • JOLT",
            "desc": "In programmazione:\n• L'ULTIMO MERCENARIO\n• JOLT"
        },
        "Primafila7-4k.it": {
            "name": "PRIMAFILA 7 4K",
            "movie": "LUCA • VIVO",
            "desc": "In programmazione:\n• LUCA\n• VIVO"
        },
        "Primafila8-4k.it": {
            "name": "PRIMAFILA 8 4K",
            "movie": "LA NOTTE DEL GIUDIZIO PER SEMPRE • BLOOD RED SKY",
            "desc": "In programmazione:\n• LA NOTTE DEL GIUDIZIO PER SEMPRE\n• BLOOD RED SKY"
        },
        "Primafila9-4k.it": {
            "name": "PRIMAFILA 9 4K",
            "movie": "COME TI AMMAZZO IL BODYGUARD 2 • LA GUERRA DI DOMANI",
            "desc": "In programmazione:\n• COME TI AMMAZZO IL BODYGUARD 2\n• LA GUERRA DI DOMANI"
        }
    }

    for ch_id, data in channels_data.items():
        ch_elem = ET.SubElement(root, "channel", attrib={"id": ch_id})
        display_name = ET.SubElement(ch_elem, "display-name", attrib={"lang": "it"})
        display_name.text = data["name"]

        # Aggiunta programmi ciclici per i canali standard (Man-Ga, Top Calcio, Canale 21)
        if "shows" in data:
            for day in range(-1, 4):
                for i, (title, desc) in enumerate(data["shows"]):
                    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day, hours=i*6)
                    stop_time = start_time + timedelta(hours=6)
                    if stop_time > now:
                        add_programme(root, ch_id, start_time, stop_time, title, desc)

        # Gestione Sky Primafila (Vetrina, da 1 a 18 e 4K) con blocchi giornalieri continui
        if "movie" in data:
            for day in range(-1, 5):
                base_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
                slots = [
                    ("00:00", "06:00", data["movie"], data["desc"]),
                    ("06:00", "12:00", data["movie"], data["desc"]),
                    ("12:00", "18:00", data["movie"], data["desc"]),
                    ("18:00", "23:59", data["movie"], data["desc"])
                ]
                for start_h, stop_h, title, desc in slots:
                    start_dt = datetime.strptime(f"{base_date.strftime('%Y-%m-%d')} {start_h}", "%Y-%m-%d %H:%M")
                    stop_dt = datetime.strptime(f"{base_date.strftime('%Y-%m-%d')} {stop_h}", "%Y-%m-%d %H:%M") if stop_h != "23:59" else base_date.replace(hour=23, minute=59, second=59)
                    if stop_dt >= now:
                        add_programme(root, ch_id, start_dt, stop_dt, title, desc)

        # Gestione Amazon Prime Video (ID: AmazonPrimeVideo.it) senza sovrapposizioni
        if data.get("is_prime"):
            prime_matches = [
                {"date": "2026-11-25", "time": "19:30", "title": "UEFA Champions League: PSG vs Roma", "desc": "Diretta esclusiva in streaming su Amazon Prime Video."},
                {"date": "2026-12-09", "time": "19:30", "title": "UEFA Champions League: Borussia Dortmund vs Inter", "desc": "Diretta esclusiva in streaming su Amazon Prime Video."}
            ]

            # Mappa partite attive (solo se non sono ancora terminate) per data YYYY-MM-DD
            matches_by_date = {}
            for match in prime_matches:
                match_start = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
                match_stop = match_start + timedelta(hours=2, minutes=30)
                if match_stop >= now:
                    matches_by_date[match["date"]] = (match_start, match_stop, match["title"], match["desc"])

            for day in range(-1, 25):
                base_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
                date_str = base_date.strftime("%Y-%m-%d")

                if date_str in matches_by_date:
                    m_start, m_stop, m_title, m_desc = matches_by_date[date_str]
                    day_start = base_date.replace(hour=0, minute=0, second=0)
                    day_end = base_date.replace(hour=23, minute=59, second=59)
                    morning_end = base_date.replace(hour=14, minute=0, second=0)

                    # Blocco notte/mattina/primo pomeriggio fino all'inizio della partita
                    if m_start > morning_end:
                        if morning_end > now:
                            add_programme(root, ch_id, day_start, morning_end, "Amazon Prime Video - Serie e Cinema", "Panoramica delle produzioni originali e cataloghi in streaming.")
                        if m_start > now:
                            add_programme(root, ch_id, max(morning_end, day_start), m_start, "Amazon Prime Video - Intrattenimento", "Show, film e programmi in onda sulla piattaforma.")
                    elif m_start > day_start and m_start > now:
                        add_programme(root, ch_id, day_start, m_start, "Amazon Prime Video - Programmazione Prime", "Film, serie TV ed eventi in streaming esclusivo.")

                    # Evento partita (apparirà solo finché non è terminato)
                    if m_stop >= now:
                        add_programme(root, ch_id, m_start, m_stop, m_title, m_desc)

                    # Blocco post-partita fino a fine giornata
                    if day_end > m_stop and day_end > now:
                        add_programme(root, ch_id, m_stop, day_end, "Amazon Prime Video - Serata Prime", "Cinema in prima serata e grandi eventi sportivi in esclusiva.")
                else:
                    # Giorno normale senza partita: blocchi standard puliti
                    slots = [
                        ("00:00", "06:00", "Amazon Prime Video - Contenuti On Demand", "Film, serie TV ed eventi in streaming esclusivo."),
                        ("06:00", "14:00", "Amazon Prime Video - Serie e Cinema", "Panoramica delle produzioni originali e cataloghi in streaming."),
                        ("14:00", "20:00", "Amazon Prime Video - Intrattenimento", "Show, film e programmi in onda sulla piattaforma."),
                        ("20:00", "23:59", "Amazon Prime Video - Serata Prime", "Cinema in prima serata e grandi eventi sportivi in esclusiva.")
                    ]
                    for start_h, stop_h, title, desc in slots:
                        start_dt = datetime.strptime(f"{date_str} {start_h}", "%Y-%m-%d %H:%M")
                        stop_dt = datetime.strptime(f"{date_str} {stop_h}", "%Y-%m-%d %H:%M") if stop_h != "23:59" else base_date.replace(hour=23, minute=59, second=59)
                        if stop_dt >= now:
                            add_programme(root, ch_id, start_dt, stop_dt, title, desc)

    # Salvataggio file XML finale
    tree = ET.ElementTree(root)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("File epg.xml generato con successo!")

if __name__ == "__main__":
    generate_epg()
