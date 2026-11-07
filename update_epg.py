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

    # 2. SKY SPORTS FOOTBALL UK E SKY SPORT 1 (Risoluzione problema "no data")
    sky_root = download_and_parse_xml(URL_SKY_UK)
    it1_root = download_and_parse_xml(URL_EPG_IT1)
    
    # Cerchiamo Sky Sport 1 e Sky Sport Football nelle sorgenti disponibili
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

    # 3. CANALI SPECIALI, LOCALI E SKY PRIMAFILA (Vetrina + Da 1 a 18)
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
        "Primafila1.it": {
            "name": "PRIMAFILA 1",
            "movie": "BLACK PHONE 2 2025",
            "desc": "Sky Primafila Premiere 1 HD - Prima visione cinematografica."
        },
        "Primafila2.it": {
            "name": "PRIMAFILA 2",
            "movie": "SUPERMAN 2025",
            "desc": "Sky Primafila Premiere 2 HD - Prima visione cinematografica."
        },
        "Primafila3.it": {
            "name": "PRIMAFILA 3",
            "movie": "MISSION IMPOSSIBLE 2025",
            "desc": "Sky Primafila Premiere 3 HD - Prima visione cinematografica."
        },
        "Primafila4.it": {
            "name": "PRIMAFILA 4",
            "movie": "WEAPONS 2025",
            "desc": "Sky Primafila Premiere 4 HD - Prima visione cinematografica."
        },
        "Primafila5.it": {
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
        }
    }

    for ch_id, data in channels_data.items():
        # Aggiunta tag canale
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
                        prog = ET.SubElement(root, "programme", attrib={
                            "start": start_time.strftime("%Y%m%d%H%M%S +0100"),
                            "stop": stop_time.strftime("%Y%m%d%H%M%S +0100"),
                            "channel": ch_id
                        })
                        ET.SubElement(prog, "title", attrib={"lang": "it"}).text = title
                        ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = desc

        # Gestione Sky Primafila (Vetrina e da 1 a 18) con blocchi giornalieri continui
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
                        prog = ET.SubElement(root, "programme", attrib={
                            "start": start_dt.strftime("%Y%m%d%H%M%S +0100"),
                            "stop": stop_dt.strftime("%Y%m%d%H%M%S +0100"),
                            "channel": ch_id
                        })
                        ET.SubElement(prog, "title", attrib={"lang": "it"}).text = title
                        ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = desc

        # Aggiunta programmi e blocchi per Amazon Prime Video (ID: AmazonPrimeVideo.it)
        if data.get("is_prime"):
            prime_matches = [
                {"date": "2026-11-25", "time": "19:30", "title": "UEFA Champions League: PSG vs Roma", "desc": "Diretta esclusiva in streaming su Amazon Prime Video."},
            ]
            for match in prime_matches:
                match_date = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
                start_dt = match_date
                stop_dt = match_date + timedelta(hours=2, minutes=30)
                if stop_dt >= now:
                    prog = ET.SubElement(root, "programme", attrib={
                        "start": start_dt.strftime("%Y%m%d%H%M%S +0100"),
                        "stop": stop_dt.strftime("%Y%m%d%H%M%S +0100"),
                        "channel": ch_id
                    })
                    ET.SubElement(prog, "title", attrib={"lang": "it"}).text = match["title"]
                    ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = match["desc"]

            # Blocchi giornalieri continui per Amazon Prime
            for day in range(-1, 5):
                base_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day)
                slots = [
                    ("00:00", "06:00", "Amazon Prime Video - Contenuti On Demand", "Film, serie TV ed eventi in streaming esclusivo."),
                    ("06:00", "14:00", "Amazon Prime Video - Serie e Cinema", "Panoramica delle produzioni originali e cataloghi in streaming."),
                    ("14:00", "20:00", "Amazon Prime Video - Intrattenimento", "Show, film e programmi in onda sulla piattaforma."),
                    ("20:00", "23:59", "Amazon Prime Video - Serata Prime", "Cinema in prima serata e grandi eventi sportivi in esclusiva.")
                ]
                for start_h, stop_h, title, desc in slots:
                    start_dt = datetime.strptime(f"{base_date.strftime('%Y-%m-%d')} {start_h}", "%Y-%m-%d %H:%M")
                    stop_dt = datetime.strptime(f"{base_date.strftime('%Y-%m-%d')} {stop_h}", "%Y-%m-%d %H:%M") if stop_h != "23:59" else base_date.replace(hour=23, minute=59, second=59)
                    
                    if stop_dt >= now:
                        prog = ET.SubElement(root, "programme", attrib={
                            "start": start_dt.strftime("%Y%m%d%H%M%S +0100"),
                            "stop": stop_dt.strftime("%Y%m%d%H%M%S +0100"),
                            "channel": ch_id
                        })
                        ET.SubElement(prog, "title", attrib={"lang": "it"}).text = title
                        ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = desc

    # Salvataggio file XML finale
    tree = ET.ElementTree(root)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("File epg.xml generato con successo e Primafila configurati!")

if __name__ == "__main__":
    generate_epg()
