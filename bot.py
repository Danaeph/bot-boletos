import os
import time
import random
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = {
    "07 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-07-05-2026/event/1400642AA1B78268?referrer=https%3A%2F%2Fwww.ticketmaster.com.mx%2Fbts-boletos%2Fartist%2F2110227",
    "09 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-09-05-2026/event/1400642AA32C84D5?referrer=https%3A%2F%2Fwww.ticketmaster.com.mx%2Fbts-boletos%2Fartist%2F2110227",
    "10 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7?referrer=https%3A%2F%2Fwww.ticketmaster.com.mx%2Fbts-boletos%2Fartist%2F2110227"
}

def enviar(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=10
    )

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def revisar(page, url):
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content().lower()
        current = page.url.lower()

        palabras = [
            "buscar boletos",
            "buy tickets",
            "join queue",
            "queue",
            "fila virtual",
            "waiting room",
            "ticket availability"
        ]

        bloqueado = [
            "agotado",
            "sold out",
            "coming soon"
        ]

        ok = any(x in html for x in palabras)
        bad = any(x in html for x in bloqueado)

        if "queue-it" in current:
            ok = True

        return ok and not bad

    except:
        return False

estado = {k: False for k in URLS}

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
    )

    page = browser.new_page()

    log("BOT INICIADO")

    while True:

        for fecha, url in URLS.items():

            disponible = revisar(page, url)

            if disponible:

                log(f"🔥 DISPONIBLE {fecha}")

                if not estado[fecha]:

                    for i in range(5):
                        enviar(f"🚨 BTS DISPONIBLE 🚨\n{fecha}\n{url}")
                        time.sleep(1)

                estado[fecha] = True

            else:
                log(f"❌ Cerrado {fecha}")
                estado[fecha] = False

        espera = random.uniform(8,15)
        log(f"Esperando {round(espera,1)}s")
        time.sleep(espera)