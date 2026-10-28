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
    root = ET.Element("tv", attrib={"generator-info-name": "Custom-Dynamic-EPG"})
    
    # 1. Definizione Canali
    for key, data in CHANNELS.items():
        channel = ET.SubElement(root, "channel", attrib={"id": data["tvg-id"]})
        display_name = ET.SubElement(channel, "display-name", attrib={"lang": "it"})
        display_name.text = data["name"]

    now = datetime.now()

    # 2. AMAZON PRIME CALCIO (Partite di Champions League mirate)
    prime_matches = [
        {"date": "2026-10-28", "title": "UEFA Champions League: Milan vs Real Madrid", "desc": "Diretta esclusiva in prima serata su Amazon Prime Video."},
        {"date": "2026-11-04", "title": "UEFA Champions League: Inter vs Arsenal", "desc": "Diretta esclusiva in prima serata su Amazon Prime Video."},
        {"date": "2026-11-11", "title": "UEFA Champions League: Paris Saint-Germain vs Bayern Monaco", "desc": "Diretta esclusiva in prima serata su Amazon Prime Video."},
        {"date": "2026-11-18", "title": "UEFA Champions League: Manchester City vs Barcelona", "desc": "Diretta esclusiva in prima serata su Amazon Prime Video."},
    ]

    for match in prime_matches:
        match_date = datetime.strptime(match["date"], "%Y-%m-%d")
        start_dt = match_date.replace(hour=20, minute=45, second=0)
        stop_dt = match_date.replace(hour=23, minute=15, second=0)
        
        prog = ET.SubElement(root, "programme", attrib={
            "start": start_dt.strftime("%Y%m%d%H%M%S +0100"),
            "stop": stop_dt.strftime("%Y%m%d%H%M%S +0100"),
            "channel": CHANNELS["amazonprime"]["tvg-id"]
        })
        t = ET.SubElement(prog, "title", attrib={"lang": "it"})
        t.text = match["title"]
        d = ET.SubElement(prog, "desc", attrib={"lang": "it"})
        d.text = match["desc"]

    # Fallback Prime
    fallback_prog = ET.SubElement(root, "programme", attrib={
        "start": now.strftime("%Y%m%d%H%M%S +0100"),
        "stop": (now + timedelta(days=7)).strftime("%Y%m%d%H%M%S +0100"),
        "channel": CHANNELS["amazonprime"]["tvg-id"]
    })
    ft = ET.SubElement(fallback_prog, "title", attrib={"lang": "it"})
    ft.text = "Amazon Prime Video - Sport & Champions League"
    fd = ET.SubElement(fallback_prog, "desc", attrib={"lang": "it"})
    fd.text = "In attesa della prossima diretta di UEFA Champions League del mercoledì."

    # 3. SKY SPORT FOOTBALL UK (Palinsesto dinamico a blocchi di 2 ore)
    skysport_shows = [
        ("Sky Sports Football Live: Premier League Match", "Copertura integrale e diretta dei match della Premier League inglese."),
        ("EFL Highlights & Analysis", "Approfondimenti, gol e interviste dai campi della Championship e delle serie minori inglesi."),
        ("Football The Debrief", "Analisi tattica e post-partita con i grandi opinionisti del calcio britannico."),
        ("International Football Rewind", "I grandi classici e le sfide storiche delle nazionali trasmesse da Sky UK."),
        ("Sky Sports Match Choice", "Repliche integrali delle sfide più emozionanti del fine settimana calcistico.")
    ]
    
    # Generiamo palinsesto continuo per le prossime 48 ore
    for day in range(0, 3):
        for i, (show_title, show_desc) in enumerate(skysport_shows):
            start_time = now.replace(hour=0, minute=0, second=0) + timedelta(days=day, hours=i*5)
            stop_time = start_time + timedelta(hours=5)
            
            if stop_time > now: # Includiamo solo programmi attuali o futuri
                prog = ET.SubElement(root, "programme", attrib={
                    "start": start_time.strftime("%Y%m%d%H%M%S +0000"),
                    "stop": stop_time.strftime("%Y%m%d%H%M%S +0000"),
                    "channel": CHANNELS["skysportfootball"]["tvg-id"]
                })
                t = ET.SubElement(prog, "title", attrib={"lang": "en"})
                t.text = show_title
                d = ET.SubElement(prog, "desc", attrib={"lang": "en"})
                d.text = show_desc

    # 4. CANALE 21 e TOP CALCIO 24 (Palinsesti locali e sportivi dinamici)
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
    print("EPG dinamica e dettagliata generata con successo!")

if __name__ == "__main__":
    generate_epg()
