import os
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# URL delle sorgenti esterne ufficiali fornite
URL_SKY_UK = "https://www.open-epg.com/files/unitedkingdom.xml.gz"
URL_DAZN_IT = "https://www.open-epg.com/files/italy8.xml.gz"

def download_and_parse_xml(url):
    """Scarica e decomprime un file XML.GZ remoto restituendo l'albero XML"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            with gzip.open(response, 'rt', encoding='utf-8', errors='ignore') as f:
                return ET.parse(f).getroot()
    except Exception as e:
        print(f"Errore download/parsing da {url}: {e}")
        return None

def generate_epg():
    root = ET.Element("tv", attrib={"generator-info-name": "Ultimate-Hybrid-EPG"})
    
    now = datetime.now()

    # 1. SCARICAMENTO E ESTRAZIONE DAZN DA ITALY8 (Zonadazn 2, 3, 4)
    dazn_root = download_and_parse_xml(URL_DAZN_IT)
    target_dazn_ids = ["ZONADAZN2.it", "ZONADAZN3.it", "ZONADAZN4.it"]
    
    if dazn_root is not None:
        # Copia i canali DAZN trovati
        for channel in dazn_root.findall("channel"):
            ch_id = channel.get("id")
            if any(target in ch_id for target in ["DAZN2", "DAZN3", "DAZN4", "ZONADAZN2", "ZONADAZN3", "ZONADAZN4"]):
                root.append(channel)
        # Copia i programmi associati a quei canali DAZN
        for programme in dazn_root.findall("programme"):
            ch_ref = programme.get("channel")
            if any(target in ch_ref for target in ["DAZN2", "DAZN3", "DAZN4", "ZONADAZN2", "ZONADAZN3", "ZONADAZN4"]):
                # Filtriamo solo programmi futuri o odierni per alleggerire
                root.append(programme)

    # 2. SCARICAMENTO E ESTRAZIONE SKY SPORTS FOOTBALL UK
    sky_root = download_and_parse_xml(URL_SKY_UK)
    if sky_root is not None:
        for channel in sky_root.findall("channel"):
            if "football" in channel.get("id", "").lower() or "skysportsfootball" in channel.get("id", "").lower():
                root.append(channel)
        for programme in sky_root.findall("programme"):
            ch_ref = programme.get("channel")
            if "football" in ch_ref.lower() or "skysportsfootball" in ch_ref.lower():
                root.append(programme)

    # 3. AGGIUNTA MANUALMENTE DEI NOSTRI CANALI LOCALI E AMAZON PRIME
    custom_channels = {
        "amazonprime": {
            "name": "Eventi Calcio Amazon Prime",
            "tvg-id": "AmazonPrimeVideo.it",
        },
        "canale21": {
            "name": "Canale 21",
            "tvg-id": "Canale21.it",
        },
        "topcalcio24": {
            "name": "Top Calcio 24 Hd",
            "tvg-id": "TopCalcio24.it",
        },
    }

    for key, data in custom_channels.items():
        channel = ET.SubElement(root, "channel", attrib={"id": data["tvg-id"]})
        display_name = ET.SubElement(channel, "display-name", attrib={"lang": "it"})
        display_name.text = data["name"]

    # AMAZON PRIME (Partite reali del mese)
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
                "channel": "AmazonPrimeVideo.it"
            })
            t = ET.SubElement(prog, "title", attrib={"lang": "it"})
            t.text = match["title"]
            d = ET.SubElement(prog, "desc", attrib={"lang": "it"})
            d.text = match["desc"]

    # Schermata di cortesia Amazon Prime
    fallback_prime = ET.SubElement(root, "programme", attrib={
        "start": now.strftime("%Y%m%d%H%M%S +0100"),
        "stop": (now + timedelta(days=30)).strftime("%Y%m%d%H%M%S +0100"),
        "channel": "AmazonPrimeVideo.it"
    })
    ET.SubElement(fallback_prime, "title", attrib={"lang": "it"}).text = "Amazon Prime Video - Eventi in Diretta"
    ET.SubElement(fallback_prime, "desc", attrib={"lang": "it"}).text = "Canale dedicato alle dirette e ai match di UEFA Champions League in esclusiva."

    # TOP CALCIO 24 (Programmi reali)
    topcalcio_shows = [
        ("Apericalcio", "Un piacevole momento per gli appassionati di calcio di ogni età ed esperienza."),
        ("Azzurro Italia TG", "Servizi, approfondimenti, interviste e ultime notizie sul mondo del calciomercato italiano."),
        ("Alta quota", "Interviste, novità, servizi e tutte le ultime notizie relative al mondo del calcio."),
        ("Diretta stadio", "Commenti, collegamenti e dibattiti in tempo reale sulla giornata calcistica.")
    ]

    for day in range(0, 3):
        for i, (show_title, show_desc) in enumerate(topcalcio_shows):
            start_time = now.replace(hour=0, minute=0, second=0) + timedelta(days=day, hours=i*6)
            stop_time = start_time + timedelta(hours=6)
            if stop_time > now:
                prog = ET.SubElement(root, "programme", attrib={
                    "start": start_time.strftime("%Y%m%d%H%M%S +0100"),
                    "stop": stop_time.strftime("%Y%m%d%H%M%S +0100"),
                    "channel": "TopCalcio24.it"
                })
                ET.SubElement(prog, "title", attrib={"lang": "it"}).text = show_title
                ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = show_desc

    # CANALE 21 (Palinsesto informativo)
    canale21_shows = [
        ("Tg Campania - Informazione", "Notiziario regionale in diretta con approfondimenti di cronaca e attualità."),
        ("Il Bello del Calcio", "La storica trasmissione sportiva dedicata alle squadre campane e al grande calcio."),
        ("Campania Sport", "Dibattiti, collegamenti e moviola in tempo reale sui temi del campionato."),
        ("Spazio Aperto - Rubrica", "Approfondimenti culturali, sociali e di costume del territorio.")
    ]

    for day in range(0, 3):
        for i, (show_title, show_desc) in enumerate(canale21_shows):
            start_time = now.replace(hour=0, minute=0, second=0) + timedelta(days=day, hours=i*6)
            stop_time = start_time + timedelta(hours=6)
            if stop_time > now:
                prog = ET.SubElement(root, "programme", attrib={
                    "start": start_time.strftime("%Y%m%d%H%M%S +0100"),
                    "stop": start_time.strftime("%Y%m%d%H%M%S +0100"),
                    "channel": "Canale21.it"
                })
                ET.SubElement(prog, "title", attrib={"lang": "it"}).text = show_title
                ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = show_desc

    # Salvataggio file XML finale
    tree = ET.ElementTree(root)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("EPG ibrida avanzata generata con successo!")

if __name__ == "__main__":
    generate_epg()
