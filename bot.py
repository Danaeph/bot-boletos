import requests
import time
import os

# Variables de entorno (NO pongas el token aquí)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = {
    "07 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-07-05-2026/event/1400642AA1B78268",
    "09 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-09-05-2026/event/1400642AA32C84D5",
    "10 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7"
}

def enviar(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def check(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    
    return "Buscar Boletos" in r.text or "Buy Tickets" in r.text

avisadas = {k: False for k in URLS}

while True:
    for fecha, url in URLS.items():
        if check(url) and not avisadas[fecha]:
            enviar(f"🚨 BOLETOS DISPONIBLES\n{fecha}\n{url}")
            avisadas[fecha] = True
            print(f"Alerta enviada: {fecha}")
        else:
            print(f"{fecha}: sin cambios")

    time.sleep(60)