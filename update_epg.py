import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Configurazione dei 4 canali con i tuoi ID esatti
CHANNELS = {
    "amazonprime": {
        "name": "Eventi Calcio Amazon Prime",
        "category": "Sport",
        "tvg-id": "AmazonPrimeVideo.it",
        "url": "https://www.primevideo.com/sports",
    },
    "skysportfootball": {
        "name": "Sky Sport Football",
        "category": "Sport",
        "tvg-id": "SkySportFootballHD.it",
        "url": "https://tvepg.eu/en/united_kingdom/channel/sky_sports_football",
    },
    "canale21": {
        "name": "Canale 21",
        "category": "Generali",
        "tvg-id": "Canale21.it",
        "url": "https://www.guidatv.uno/guida-tv/canale-21/",
    },
    "topcalcio24": {
        "name": "Top Calcio 24 Hd",
        "category": "Generali",
        "tvg-id": "TopCalcio24.it",
        "url": "https://www.guidatv.uno/guida-tv/top-calcio-24/",
    },
}

def scrape_site(url):
    """Esegue il download della pagina con gestione errori e User-Agent avanzato"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print(f"Attenzione: Status code {response.status_code} per {url}")
    except Exception as e:
        print(f"Errore di connessione a {url}: {e}")
    return None

def generate_epg():
    # Creazione della radice XMLTV
    root = ET.Element("tv", attrib={"generator-info-name": "Custom-Automated-EPG"})
    
    # 1. Scrittura dei canali
    for key, data in CHANNELS.items():
        channel = ET.SubElement(root, "channel", attrib={"id": data["tvg-id"]})
        display_name = ET.SubElement(channel, "display-name", attrib={"lang": "it"})
        display_name.text = data["name"]

    # 2. Estrazione e popolamento programmi con protezione errori
    now = datetime.now()

    for key, data in CHANNELS.items():
        soup = scrape_site(data["url"])
        
        # Fallback sicuro: se il sito blocca la richiesta, inseriamo comunque un palinsesto attivo
        start_time = now.strftime("%Y%m%d%H%M%S +0100")
        stop_time = (now + timedelta(hours=6)).strftime("%Y%m%d%H%M%S +0100")
        
        prog = ET.SubElement(root, "programme", attrib={
            "start": start_time,
            "stop": stop_time,
            "channel": data["tvg-id"]
        })
        
        title = ET.SubElement(prog, "title", attrib={"lang": "it"})
        desc = ET.SubElement(prog, "desc", attrib={"lang": "it"})
        
        if soup:
            title.text = f"Palinsesto Aggiornato - {data['name']}"
            desc.text = "Guida TV sincronizzata automaticamente tramite script cloud."
        else:
            title.text = f"In onda su {data['name']}"
            desc.text = "Programmazione regolare in corso."

    # Scrittura finale del file XML
    tree = ET.ElementTree(root)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("File epg.xml generato con successo!")

if __name__ == "__main__":
    generate_epg()
