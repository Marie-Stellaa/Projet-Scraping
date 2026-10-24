import os
import sys
import time
sys.path.append('.')

import config
from app.scraper.driver import Driver, CaptchaDetecte

DOSSIER = "pages_locales"
ESSAIS_MAX = 3


def telecharger_page(driver, numero):
    url = f"{config.BASE_URL}&page={numero}"
    for essai in range(1, ESSAIS_MAX + 1):
        print(f"Page {numero}/{config.NB_PAGES} (essai {essai}/{ESSAIS_MAX}) : {url}")
        try:
            html = driver.charger(url)
            if html:
                return html
            print("  Page vide ou liste de produits introuvable.")
        except CaptchaDetecte:
            raise
        except Exception as e:
            print(f"  Erreur ({type(e).__name__}).")
        time.sleep(5)
    return None


def main():
    os.makedirs(DOSSIER, exist_ok=True)
    driver = Driver()
    driver.pilote.set_page_load_timeout(60)  

    try:
        for numero in range(1, config.NB_PAGES + 1):
            chemin = os.path.join(DOSSIER, f"amazon_laptop_page_{numero}.html")

            if os.path.exists(chemin):
                print(f"Page {numero} deja enregistree, on passe.")
                continue

            html = telecharger_page(driver, numero)
            if not html:
                print(f"Page {numero} non recuperee. Relance le script pour reessayer.")
                continue

            with open(chemin, "w", encoding="utf-8") as fichier:
                fichier.write(html)
            print(f"  -> enregistree : {chemin}")

    except CaptchaDetecte as e:
        print(f"Captcha detecte : {e}")
        print("Astuce : enregistre les pages a la main depuis ton navigateur (Ctrl+S).")
    finally:
        driver.fermer()


if __name__ == "__main__":
    main()