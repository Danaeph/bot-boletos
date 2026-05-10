import os

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

            # ===== FILA =====
            if data["fila"]:
                log("🟡 EN FILA")

                if not aviso_fila:
                    enviar(
                        f"🟡 BOT EN FILA TM\n\n{data['url_actual']}"
                    )
                    aviso_fila = True

            else:
                aviso_fila = False

            # ===== BOLETOS =====
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
            log(f"⏳ Esperando {round(espera,1)}s")
            time.sleep(espera)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log(f"ERROR CRÍTICO: {e}")
            time.sleep(15)
