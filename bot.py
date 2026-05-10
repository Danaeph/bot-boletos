import asyncio
import random
import time
import requests

from playwright.async_api import async_playwright

# =========================
# CONFIG
# =========================

URL = "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7?referrer=https%3A%2F%2Fwww.ticketmaster.com.mx%2Fbts-boletos%2Fartist%2F2110227"

TOKEN = "TU_TOKEN_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"

# =========================
# LOGS
# =========================

def log(msg):
    hora = time.strftime("%H:%M:%S")
    print(f"[{hora}] {msg}")

# =========================
# TELEGRAM
# =========================

def enviar_telegram(mensaje):
    try:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": mensaje
            },
            timeout=10
        )
    except Exception as e:
        log(f"Telegram error: {e}")

# =========================
# MAIN
# =========================

async def main():

    log("🚀 BOT INICIADO")

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        # =========================
        # ENTRAR SOLO UNA VEZ
        # =========================

        await page.goto(URL, wait_until="domcontentloaded")

        while True:

            try:

                contenido = (await page.content()).lower()

                # =========================
                # FILA
                # =========================

                if "queue" in page.url.lower():

                    log("🟡 EN FILA")

                    await asyncio.sleep(10)

                    continue

                # =========================
                # DETECTAR MAPA
                # =========================

                try:

                    disponibles = page.locator(
                        'svg [fill="#0056FF"], '
                        'svg [fill="#1E90FF"], '
                        '[class*="available"], '
                        '[aria-label*="Available"]'
                    )

                    cantidad = await disponibles.count()

                    if cantidad > 0:

                        log(f"🎟️ SECCIONES DISPONIBLES: {cantidad}")

                        enviar_telegram(
                            f"🎟️ Posibles boletos detectados\n{URL}"
                        )

                    else:

                        log("❌ SIN BOLETOS")

                except Exception as mapa_error:

                    log(f"Mapa error: {mapa_error}")

                # =========================
                # REFRESH SIN REFORMARSE
                # =========================

                espera = random.uniform(3, 6)

                log(f"⏳ Esperando {espera:.1f}s")

                await asyncio.sleep(espera)

                await page.reload(
                    wait_until="domcontentloaded",
                    timeout=60000
                )

            except Exception as e:

                log(f"ERROR CRÍTICO: {e}")

                try:
                    await page.reload(
                        wait_until="domcontentloaded",
                        timeout=60000
                    )
                except:
                    pass

                await asyncio.sleep(15)

# =========================
# START
# =========================

asyncio.run(main())
