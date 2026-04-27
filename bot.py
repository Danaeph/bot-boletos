import os
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = {
    "07 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-07-05-2026/event/1400642AA1B78268",
    "09 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-09-05-2026/event/1400642AA32C84D5",
    "10 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def enviar(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": msg,
                "disable_notification": False
            },
            timeout=10
        )
    except Exception as e:
        print("Error Telegram:", e)

def check(url):
    try:
        r = SESSION.get(url, timeout=10)
        t = r.text.lower()

        disponible = ("buscar boletos" in t or "buy tickets" in t)
        bloqueado = any(x in t for x in [
            "agotado", "sold out", "próximamente", "coming soon"
        ])

        return disponible and not bloqueado

    except Exception as e:
        print("Error request:", e)
        return False

def revisar_todo():
    resultados = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futuros = {executor.submit(check, url): fecha for fecha, url in URLS.items()}

        for futuro in as_completed(futuros):
            fecha = futuros[futuro]
            try:
                resultados[fecha] = futuro.result()
            except:
                resultados[fecha] = False

    return resultados

avisadas = {k: False for k in URLS}

print("🚀 Bot NIVEL DIOS corriendo...")

while True:
    resultados = revisar_todo()

    for fecha, disponible in resultados.items():
        url = URLS[fecha]

        if disponible and not avisadas[fecha]:
            print(f"🔥 DISPONIBLE: {fecha}")

            # alerta múltiple (clave)
            for i in range(5):
                enviar(f"🚨🔥 BOLETOS DISPONIBLES 🔥🚨\n{fecha}\n{url}")
                time.sleep(0.8)

            avisadas[fecha] = True

        else:
            print(f"{fecha}: sin cambios")

    # intervalo agresivo pero seguro
    sleep_time = random.uniform(8, 15)
    print(f"⏳ Esperando {round(sleep_time,1)}s\n")
    time.sleep(sleep_time)