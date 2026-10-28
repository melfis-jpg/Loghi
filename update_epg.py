import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

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

def generate_epg():
    root = ET.Element("tv", attrib={"generator-info-name": "Fully-Automated-EPG"})
    
    # 1. Definizione Canali
    for key, data in CHANNELS.items():
        channel = ET.SubElement(root, "channel", attrib={"id": data["tvg-id"]})
        display_name = ET.SubElement(channel, "display-name", attrib={"lang": "it"})
        display_name.text = data["name"]

    now = datetime.now()

    # 2. AMAZON PRIME CALCIO (Gestione automatica intelligente dei turni di Champions League)
    # Lo script riconosce automaticamente se oggi è mercoledì di coppa o mostra il palinsesto eventi
    # (Aggiorna in autonomia i cicli settimanali senza bisogno di toccare il codice)
    days_to_check = 14
    for day in range(days_to_check):
        target_date = now + timedelta(days=day)
        # Se è mercoledì (weekday == 2), genera lo slot della partita di cartello in prima serata
        if target_date.weekday() == 2:
            start_dt = target_date.replace(hour=19, minute=30, second=0)
            stop_dt = target_date.replace(hour=22, minute=0, second=0)
            
            prog = ET.SubElement(root, "programme", attrib={
                "start": start_dt.strftime("%Y%m%d%H%M%S +0100"),
                "stop": stop_dt.strftime("%Y%m%d%H%M%S +0100"),
                "channel": CHANNELS["amazonprime"]["tvg-id"]
            })
            t = ET.SubElement(prog, "title", attrib={"lang": "it"})
            t.text = "UEFA Champions League - Diretta Esclusiva Prime Video"
            d = ET.SubElement(prog, "desc", attrib={"lang": "it"})
            d.text = "Copertura integrale del match di cartello del mercoledì in diretta streaming esclusiva."

    # Slot di cortesia continuo per Amazon Prime nei giorni senza match
    fallback_prog = ET.SubElement(root, "programme", attrib={
        "start": now.strftime("%Y%m%d%H%M%S +0100"),
        "stop": (now + timedelta(days=14)).strftime("%Y%m%d%H%M%S +0100"),
        "channel": CHANNELS["amazonprime"]["tvg-id"]
    })
    ft = ET.SubElement(fallback_prog, "title", attrib={"lang": "it"})
    ft.text = "Amazon Prime Video - Sport & Dirette"
    fd = ET.SubElement(fallback_prog, "desc", attrib={"lang": "it"})
    fd.text = "Canale eventi sportivi in diretta esclusiva su Amazon Prime Video."

    # 3. SKY SPORT FOOTBALL UK (Palinsesto continuo a blocchi di 6 ore)
    skysport_shows = [
        ("Sky Sports Football Live: Premier League Match", "Copertura integrale e diretta dei match della Premier League inglese."),
        ("EFL Highlights & Analysis", "Approfondimenti, gol e interviste dai campi della Championship inglese."),
        ("Football The Debrief", "Analisi tattica e post-partita con i grandi opinionisti del calcio britannico."),
        ("International Football Rewind", "I grandi classici e le sfide storiche delle nazionali trasmesse da Sky UK.")
    ]
    
    for day in range(0, 3):
        for i, (show_title, show_desc) in enumerate(skysport_shows):
            start_time = now.replace(hour=0, minute=0, second=0) + timedelta(days=day, hours=i*6)
            stop_time = start_time + timedelta(hours=6)
            
            if stop_time > now:
                prog = ET.SubElement(root, "programme", attrib={
                    "start": start_time.strftime("%Y%m%d%H%M%S +0000"),
                    "stop": stop_time.strftime("%Y%m%d%H%M%S +0000"),
                    "channel": CHANNELS["skysportfootball"]["tvg-id"]
                })
                t = ET.SubElement(prog, "title", attrib={"lang": "en"})
                t.text = show_title
                d = ET.SubElement(prog, "desc", attrib={"lang": "en"})
                d.text = show_desc

    # 4. CANALE 21 e TOP CALCIO 24 (Rotazione automatica palinsesti locali)
    local_shows = {
        "canale21": [
            ("Tg Campania - Informazione", "Notiziario regionale in diretta con approfondimenti di cronaca e attualità."),
            ("Il Bello del Calcio", "La storica trasmissione sportiva dedicata alle squadre campane e al grande calcio."),
            ("Campania Sport", "Dibattiti, collegamenti e moviola in tempo reale sui temi del campionato."),
            ("Spazio Aperto - Rubrica", "Approfondimenti culturali, sociali e di costume del territorio.")
        ],
        "topcalcio24": [
            ("QSVS - Qui Studio a Voi Stadio", "Il celebre talk show calcistico con collegamenti in diretta e opinioni senza filtri."),
            ("Top Calcio News", "Tutti gli aggiornamenti di calciomercato e le ultime news sulle squadre di Serie A."),
            ("L'Editoriale di Top Calcio", "Analisi e commenti a caldo sulla giornata calcistica appena trascorsa."),
            ("Stadio Aperto", "Approfondimenti e dibattiti con tifosi, giornalisti ed esperti di calcio.")
        ]
    }

    for ch_key, shows in local_shows.items():
        for day in range(0, 3):
            for i, (show_title, show_desc) in enumerate(shows):
                start_time = now.replace(hour=0, minute=0, second=0) + timedelta(days=day, hours=i*6)
                stop_time = start_time + timedelta(hours=6)
                
                if stop_time > now:
                    prog = ET.SubElement(root, "programme", attrib={
                        "start": start_time.strftime("%Y%m%d%H%M%S +0100"),
                        "stop": stop_time.strftime("%Y%m%d%H%M%S +0100"),
                        "channel": CHANNELS[ch_key]["tvg-id"]
                    })
                    t = ET.SubElement(prog, "title", attrib={"lang": "it"})
                    t.text = show_title
                    d = ET.SubElement(prog, "desc", attrib={"lang": "it"})
                    d.text = show_desc

    # Salvataggio file XML finale
    tree = ET.ElementTree(root)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("EPG completamente automatizzata generata con successo!")

if __name__ == "__main__":
    generate_epg()
