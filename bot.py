import os
import time
import random
import requests
from datetime import datetime

os.system("playwright install chromium")

from playwright.sync_api import sync_playwright

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def enviar(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": msg
            },
            timeout=10
        )
    except Exception as e:
        log(f"Error Telegram: {e}")


def revisar(page):

    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=45000)

        time.sleep(5)

        html = page.content().lower()
        current = page.url.lower()

        en_fila = (
            "queue-it" in current
            or "waiting room" in html
            or "join queue" in html
            or "fila virtual" in html
            or "queue" in html
        )

        disponible = (
            "buscar boletos" in html
            or "buy tickets" in html
            or "ticket availability" in html
            or "find tickets" in html
        )

        agotado = (
            "sold out" in html
            or "agotado" in html
            or "coming soon" in html
        )

        return {
            "fila": en_fila,
            "boletos": disponible and not agotado,
            "url_actual": current
        }

    except Exception as e:

        log(f"Error revisando: {e}")

        return {
            "fila": False,
            "boletos": False,
            "url_actual": ""
        }


def main():

    aviso_fila = False
    aviso_boletos = False

    with sync_playwright() as p:

        browser = p.chromium.launch(
            executable_path="/root/.cache/ms-playwright/chromium-1105/chrome-linux/chrome",
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"
        )

        page = context.new_page()

        log("🚀 BOT INICIADO")

        while True:

            data = revisar(page)

            if data["fila"]:

                log("🟡 EN FILA")

                if not aviso_fila:

                    enviar(
                        f"🟡 BOT EN FILA TM\n\n{data['url_actual']}"
                    )

                    aviso_fila = True

            else:
                aviso_fila = False

            if data["boletos"]:

                log("🔥 BOLETOS DETECTADOS")

                if not aviso_boletos:

                    for i in range(8):

                        enviar(
                            f"🚨 BOLETOS DISPONIBLES 🚨\n\n{URL}"
                        )

                        time.sleep(1)

                    aviso_boletos = True

            else:

                log("❌ SIN BOLETOS")

                aviso_boletos = False

            espera = random.uniform(10, 18)

            log(f"⏳ Esperando {round(espera, 1)}s")

            time.sleep(espera)


if __name__ == "__main__":

    while True:

        try:
            main()

        except Exception as e:

            log(f"ERROR CRÍTICO: {e}")

            time.sleep(15)
