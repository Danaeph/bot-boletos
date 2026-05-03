# ==========================================
# BOT PRO MAX - Ticketmaster Alertas Telegram
# Detecta:
# ✅ HTML normal
# ✅ Fila virtual / Queue-it
# ✅ Cambios rápidos
# ✅ Reapertura después de agotado
# ✅ Anti-falsos positivos
# ✅ Logs detallados
# ==========================================

import os
import time
import random
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = {
    "07 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-07-05-2026/event/1400642AA1B78268",
    "09 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-09-05-2026/event/1400642AA32C84D5",
    "10 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7"
}

HEADERS = {
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)"
    ]),
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

# ======================
# PALABRAS CLAVE
# ======================

OPEN_WORDS = [
    "buscar boletos",
    "buy tickets",
    "find tickets",
    "ticket availability",
    "selecciona tus boletos",
    "join queue",
    "queue",
    "fila virtual",
    "waiting room",
    "queue-it",
    "unlock",
    "tickets available"
]

CLOSED_WORDS = [
    "agotado",
    "sold out",
    "coming soon",
    "próximamente",
    "no tickets available"
]

# ======================
# SESSION
# ======================

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ======================
# TELEGRAM
# ======================

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
        print("Telegram error:", e)

# ======================
# LOG
# ======================

def log(msg):
    ahora = datetime.now().strftime("%H:%M:%S")
    print(f"[{ahora}] {msg}")

# ======================
# CHECK PRINCIPAL
# ======================

def revisar_evento(nombre, url):
    try:
        r = SESSION.get(
            url,
            timeout=12,
            allow_redirects=True
        )

        html = r.text.lower()
        final_url = r.url.lower()

        # señales positivas
        abierta = any(word in html for word in OPEN_WORDS)

        # queue-it redirect
        queue = "queue-it" in final_url

        # señales negativas
        cerrada = any(word in html for word in CLOSED_WORDS)

        # status code útil
        code_ok = r.status_code == 200

        disponible = (abierta or queue) and not cerrada and code_ok

        return {
            "evento": nombre,
            "url": url,
            "ok": disponible,
            "status": r.status_code,
            "queue": queue
        }

    except Exception as e:
        return {
            "evento": nombre,
            "url": url,
            "ok": False,
            "error": str(e)
        }

# ======================
# ESTADO
# ======================

estado = {
    nombre: {
        "activo": False,
        "ultima_alerta": 0
    }
    for nombre in URLS
}

# ======================
# ALERTA
# ======================

def lanzar_alerta(nombre, url):
    for i in range(5):
        enviar(
            f"🚨🚨 BTS DISPONIBLE 🚨🚨\n\n"
            f"{nombre}\n"
            f"{url}\n\n"
            f"¡ENTRA YA!"
        )
        time.sleep(1)

# ======================
# LOOP PRINCIPAL
# ======================

log("BOT PRO MAX iniciado")

while True:

    try:
        with ThreadPoolExecutor(max_workers=3) as executor:

            futuros = {
                executor.submit(revisar_evento, nombre, url): nombre
                for nombre, url in URLS.items()
            }

            for futuro in as_completed(futuros):

                data = futuro.result()
                nombre = data["evento"]
                url = data["url"]
                ok = data["ok"]

                if ok:
                    log(f"🔥 DISPONIBLE -> {nombre}")

                    ahora = time.time()

                    # evita spam, reavisa cada 5 min si sigue abierto
                    if (
                        not estado[nombre]["activo"]
                        or ahora - estado[nombre]["ultima_alerta"] > 300
                    ):
                        lanzar_alerta(nombre, url)
                        estado[nombre]["ultima_alerta"] = ahora

                    estado[nombre]["activo"] = True

                else:
                    log(f"❌ Cerrado -> {nombre}")
                    estado[nombre]["activo"] = False

        # intervalo rápido random anti-bloqueo
        espera = random.uniform(4, 8)
        log(f"Esperando {round(espera,1)}s")
        time.sleep(espera)

    except Exception as e:
        log(f"ERROR GENERAL: {e}")
        time.sleep(10)