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
    """Scarica e decomprime un file XML.GZ remoto restituendo l'albero XML"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
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
    if dazn_root is not None:
        for channel in dazn_root.findall("channel"):
            ch_id = channel.get("id", "")
            if any(target in ch_id.upper() for target in ["DAZN2", "DAZN3", "DAZN4", "ZONADAZN2", "ZONADAZN3", "ZONADAZN4"]):
                root.append(channel)
        for programme in dazn_root.findall("programme"):
            ch_ref = programme.get("channel", "")
            if any(target in ch_ref.upper() for target in ["DAZN2", "DAZN3", "DAZN4", "ZONADAZN2", "ZONADAZN3", "ZONADAZN4"]):
                root.append(programme)

    # 2. SCARICAMENTO E ESTRAZIONE SKY SPORTS FOOTBALL UK
    sky_root = download_and_parse_xml(URL_SKY_UK)
    if sky_root is not None:
        for channel in sky_root.findall("channel"):
            if "football" in channel.get("id", "").lower() or "skysportsfootball" in channel.get("id", "").lower():
                root.append(channel)
        for programme in sky_root.findall("programme"):
            ch_ref = programme.get("channel", "")
            if "football" in ch_ref.lower() or "skysportsfootball" in ch_ref.lower():
                root.append(programme)

    # 3. SCARICAMENTO E ESTRAZIONE CANALE 21, TOP CALCIO 24 E MAN-GA DA EPG_RIPPER_IT1
    it1_root = download_and_parse_xml(URL_EPG_IT1)
    if it1_root is not None:
        for channel in it1_root.findall("channel"):
            ch_id = channel.get("id", "").lower()
            if "canale21" in ch_id or "topcalcio" in ch_id or "top calcio" in ch_id or "man-ga" in ch_id or "manga" in ch_id:
                root.append(channel)
        for programme in it1_root.findall("programme"):
            ch_ref = programme.get("channel", "").lower()
            if "canale21" in ch_ref or "topcalcio" in ch_ref or "top calcio" in ch_ref or "man-ga" in ch_ref or "manga" in ch_ref:
                root.append(programme)

    # 4. AGGIUNTA MANUALE DI AMAZON PRIME (Eventi Champions League)
    amazon_channel = ET.SubElement(root, "channel", attrib={"id": "AmazonPrimeVideo.it"})
    display_name = ET.SubElement(amazon_channel, "display-name", attrib={"lang": "it"})
    display_name.text = "Eventi Calcio Amazon Prime"

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
            ET.SubElement(prog, "title", attrib={"lang": "it"}).text = match["title"]
            ET.SubElement(prog, "desc", attrib={"lang": "it"}).text = match["desc"]

    # Schermata di cortesia Amazon Prime
    fallback_prime = ET.SubElement(root, "programme", attrib={
        "start": now.strftime("%Y%m%d%H%M%S +0100"),
        "stop": (now + timedelta(days=30)).strftime("%Y%m%d%H%M%S +0100"),
        "channel": "AmazonPrimeVideo.it"
    })
    ET.SubElement(fallback_prime, "title", attrib={"lang": "it"}).text = "Amazon Prime Video - Eventi in Diretta"
    ET.SubElement(fallback_prime, "desc", attrib={"lang": "it"}).text = "Canale dedicato alle dirette e ai match di UEFA Champions League in esclusiva."

    # Salvataggio file XML finale
    tree = ET.ElementTree(root)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("EPG ibrida con Man-Ga automatico generata con successo!")

if __name__ == "__main__":
    generate_epg()
