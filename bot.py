import asyncio
import random
import time
import requests
import os

from playwright.async_api import async_playwright

# =========================
# CONFIG
# =========================

URL = "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7"

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# LOGS
# =========================

def log(msg):
    hora = time.strftime("%H:%M:%S")
    print(f"[{hora}] {msg}", flush=True)

# =========================
# TELEGRAM
# =========================

def enviar_telegram(mensaje):

    if not TOKEN or not CHAT_ID:
        log("⚠️ TOKEN o CHAT_ID no configurados")
        return

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

print("ARCHIVO INICIADO", flush=True)

async def main():

    log("🚀 BOT NUEVO FUNCIONANDO")
    log(f"🌐 URL: {URL}")

    enviar_telegram("✅ BOT CONECTADO")

    async with async_playwright() as p:

        log("🟡 Iniciando Chromium...")

        browser = await p.chromium.launch(
            headless=True,
            timeout=30000,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        log("✅ Chromium iniciado")

        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        log("🌐 Entrando a Ticketmaster...")

        await page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        log(f"📍 URL actual: {page.url}")

        # =========================
        # LOOP PRINCIPAL
        # =========================

        while True:

            try:

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

                    log(f"⚠️ Error mapa: {mapa_error}")

                # =========================
                # REFRESH
                # =========================

                espera = random.uniform(3, 6)

                log(f"⏳ Esperando {espera:.1f}s")

                await asyncio.sleep(espera)

                log("🔄 Recargando página...")

                await page.reload(
                    wait_until="domcontentloaded",
                    timeout=60000
                )

            except Exception as e:

                log(f"❌ ERROR CRÍTICO: {e}")

                try:

                    await page.reload(
                        wait_until="domcontentloaded",
                        timeout=60000
                    )

                except Exception as reload_error:

                    log(f"⚠️ Error reload: {reload_error}")

                await asyncio.sleep(15)

# =========================
# START
# =========================

asyncio.run(main())
