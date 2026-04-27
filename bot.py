import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

TOKEN = "8260890367:AAGFSPyc-BAdDooEpI-tnnCNMX8QZwM3nkA"
CHAT_ID = "5087322624"

URLS = {
    "07 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-07-05-2026/event/1400642AA1B78268",
    "09 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-09-05-2026/event/1400642AA32C84D5",
    "10 Mayo 2026": "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-10-05-2026/event/1400642AA32D84D7"
}

def enviar_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

avisadas = {fecha: False for fecha in URLS}

def boletos_disponibles():
    botones = driver.find_elements(By.TAG_NAME, "button")
    
    for b in botones:
        texto = b.text.lower()
        clases = b.get_attribute("class")

        # Detecta botón real de compra habilitado
        if (
            ("buscar boletos" in texto or "buy tickets" in texto)
            and b.is_enabled()
            and "disabled" not in clases
        ):
            return True

    return False
while True:
    for fecha, url in URLS.items():
        driver.get(url)
        time.sleep(8)

        if boletos_disponibles() and not avisadas[fecha]:
            enviar_telegram(f"""🚨 BOLETOS DISPONIBLES 🚨
Fecha: {fecha}
{url}
""")
            avisadas[fecha] = True
            print(f"Alerta enviada: {fecha}")
        else:
            print(f"{fecha}: sin cambios")

    time.sleep(60)