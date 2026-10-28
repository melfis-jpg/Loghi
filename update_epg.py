import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

CHANNELS = {
    "amazonprime": {
        "name": "Eventi Calcio Amazon Prime",
        "category": "Sport",
        "tvg-id": "AmazonPrimeVideo.it",
    },
    "skysportfootball": {
        "name": "Sky Sport Football",
        "category": "Sport",
        "tvg-id": "SkySportFootballHD.it",
    },
    "canale21": {
        "name": "Canale 21",
        "category": "Generali",
        "tvg-id": "Canale21.it",
    },
    "topcalcio24": {
        "name": "Top Calcio 24 Hd",
        "category": "Generali",
        "tvg-id": "TopCalcio24.it",
    },
}

def clean_text(text):
    """Rimuove spazi vuoti eccessivi e caratteri di a capo"""
    if not text:
        return ""
    return " ".join(text.split())

def generate_epg():
    root = ET.Element("tv", attrib={"generator-info-name": "Custom-Clean-EPG"})
    
    # 1. Definizione Canali
    for key, data in CHANNELS.items():
        channel = ET.SubElement(root, "channel", attrib={"id": data["tvg-id"]})
        display_name = ET.SubElement(channel, "display-name", attrib={"lang": "it"})
        display_name.text = data["name"]

    now = datetime.now()

    # 2. Programmazione AMAZON PRIME (UEFA Champions League Mercoledì)
    # Genera la copertura per la giornata odierna e i prossimi giorni
    for day_offset in range(0, 3):
        target_date = now + timedelta(days=day_offset)
        is_wednesday = (target_date.weekday() == 2) # 2 = Mercoledì
        
        start_dt = target_date.replace(hour=20, minute=45, second=0, microsecond=0)
        stop_dt = target_date.replace(hour=23, minute=15, second=0, microsecond=0)
        
        prog = ET.SubElement(root, "programme", attrib={
            "start": start_dt.strftime("%Y%m%d%H%M%S +0100"),
            "stop": stop_dt.strftime("%Y%m%d%H%M%S +0100"),
            "channel": CHANNELS["amazonprime"]["tvg-id"]
        })
        
        title = ET.SubElement(prog, "title", attrib={"lang": "it"})
        desc = ET.SubElement(prog, "desc", attrib={"lang": "it"})
        
        if is_wednesday:
            title.text = "UEFA Champions League - Diretta Esclusiva"
            desc.text = "In diretta il miglior match del mercoledì di UEFA Champions League su Amazon Prime Video."
        else:
            title.text = "Amazon Prime Video - Programmazione Sport"
            desc.text = "Prossimo appuntamento di UEFA Champions League previsto per mercoledì alle 20:45."

    # 3. Programmazione SKY SPORT FOOTBALL UK
    for i in range(0, 4):
        st = now + timedelta(hours=i*3)
        sp = now + timedelta(hours=(i+1)*3)
        prog = ET.SubElement(root, "programme", attrib={
            "start": st.strftime("%Y%m%d%H%M%S +0000"),
            "stop": sp.strftime("%Y%m%d%H%M%S +0000"),
            "channel": CHANNELS["skysportfootball"]["tvg-id"]
        })
        t = ET.SubElement(prog, "title", attrib={"lang": "en"})
        d = ET.SubElement(prog, "desc", attrib={"lang": "en"})
        t.text = "Sky Sports Football - Live & Highlights"
        d.text = "English Football Coverage, Premier League & EFL matches."

    # 4. Programmazione CANALE 21 e TOP CALCIO 24
    for ch_key in ["canale21", "topcalcio24"]:
        for i in range(0, 4):
            st = now + timedelta(hours=i*3)
            sp = now + timedelta(hours=(i+1)*3)
            prog = ET.SubElement(root, "programme", attrib={
                "start": st.strftime("%Y%m%d%H%M%S +0100"),
                "stop": sp.strftime("%Y%m%d%H%M%S +0100"),
                "channel": CHANNELS[ch_key]["tvg-id"]
            })
            t = ET.SubElement(prog, "title", attrib={"lang": "it"})
            d = ET.SubElement(prog, "desc", attrib={"lang": "it"})
            t.text = f"Diretta {CHANNELS[ch_key]['name']}"
            d.text = f"Programmazione informativa e sportiva in onda su {CHANNELS[ch_key]['name']}."

    # Salvataggio file XML pulito
    tree = ET.ElementTree(root)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("EPG pulito ed essenziale generato correttamente.")

if __name__ == "__main__":
    generate_epg()
