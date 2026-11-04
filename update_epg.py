import os
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

URL_SKY_UK = "https://www.open-epg.com/files/unitedkingdom.xml.gz"
URL_DAZN_IT = "https://www.open-epg.com/files/italy8.xml.gz"

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

    # 2. SKY SPORTS FOOTBALL UK
    sky_root = download_and_parse_xml(URL_SKY_UK)
    if sky_root is not None:
        try:
            for channel in sky_root.findall("channel"):
                ch_id = channel.get("id", "").lower()
                if "football" in ch_id or "skysports" in ch_id:
                    root.append(channel)
            for programme in sky_root.findall("programme"):
                ch_ref = programme.get("channel", "").lower()
                if "football" in ch_ref or "skysports" in ch_ref:
                    root.append(programme)
        except Exception as e:
            print(f"Errore Sky UK: {e}")

    # 3. CANALI LOCALI E SPECIALI (Man-Ga, Top Calcio 24, Canale 21, Amazon Prime)
    # Definiamo i canali con i loro ID ufficiali standard per le IPTV
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
        }
    }

    for ch_id, data in channels_data.items():
        # Aggiunta tag canale
        ch_elem = ET.SubElement(root, "channel", attrib={"id": ch_id})
        display_name = ET.SubElement(ch_elem, "display-name", attrib={"lang": "it"})
        display_name.text = data["name"]

        # Aggiunta programmi per Man-Ga, Top Calcio 24 e Canale 21
        if "shows" in data:
            for day in range(0, 3):
                for i, (title, desc) in enumerate(data["shows"]):
                    start_time = now.replace(hour=0, minute=0, second=0) + timedelta(days=day, hours=i*6)
                    stop_time = start_time + timedelta(hours=6)
                    if stop_time > now:
                        prog = ET.SubElement(root, "programme", attrib={
                            "start": start_time.strftime("%Y%m%d%H%M%S +0100"),
                            "stop": stop_time.strftime("%Y%m%d%H%M%S +0100"),
                            "channel": ch_id
                        })
                        ET.SubElement(prog, "title", attrib={"lang": "it"}).text = title
                        ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = desc

        # Aggiunta programmi per Amazon Prime
        if data.get("is_prime"):
            prime_matches = [
                {"date": "2026-11-04", "time": "19:30", "title": "UEFA Champions League: Porto vs Napoli", "desc": "Diretta esclusiva in streaming su Amazon Prime Video."},
                {"date": "2026-11-25", "time": "19:30", "title": "UEFA Champions League: PSG vs Roma", "desc": "Diretta esclusiva in streaming su Amazon Prime Video."}
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

            fallback_prime = ET.SubElement(root, "programme", attrib={
                "start": now.strftime("%Y%m%d%H%M%S +0100"),
                "stop": (now + timedelta(days=30)).strftime("%Y%m%d%H%M%S +0100"),
                "channel": ch_id
            })
            ET.SubElement(fallback_prime, "title", attrib={"lang": "it"}).text = "Amazon Prime Video - Eventi in Diretta"
            ET.SubElement(fallback_prime, "desc", attrib={"lang": "it"}).text = "Canale dedicato alle dirette e ai match di UEFA Champions League in esclusiva."

    # Salvataggio file XML finale
    tree = ET.ElementTree(root)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("File epg.xml generato con successo e canali garantiti!")

if __name__ == "__main__":
    generate_epg()
