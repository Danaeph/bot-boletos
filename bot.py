import os
import time
import random
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

# 🔥 IMPORTANTE para Railway
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

# 🔥 ESTA ES LA LÍNEA NUEVA
os.system("playwright install --with-deps chromium")

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = {
    "07 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-07-05-2026/event/1400642AA1B78268",
    "09 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-09-05-2026/event/1400642AA32C84D5",
    "10 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7"
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def enviar(msg):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
        log(f"Telegram status: {r.status_code}")
    except Exception as e:
        log(f"Error Telegram: {e}")

def revisar(page, url):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

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

        # Detecta fila virtual
        if "queue-it" in current:
            ok = True

        return ok and not bad

    except Exception as e:
        log(f"Error revisando página: {e}")
        return False

def main():
    estado = {k: False for k in URLS}

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process"
            ]
        )

        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )

        log("🚀 BOT INICIADO")

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

            espera = random.uniform(8, 15)
            log(f"⏳ Esperando {round(espera,1)}s")
            time.sleep(espera)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"ERROR CRÍTICO: {e}")
        time.sleep(10)
