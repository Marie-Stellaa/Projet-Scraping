import os
import sys
import time
sys.path.append('.')

import config
from app.scraper.driver import Driver, CaptchaDetecte

ESSAIS_MAX = 3


def telecharger_page(driver, categorie, numero):
    url = config.url_recherche(categorie, numero)
    for essai in range(1, ESSAIS_MAX + 1):
        print(f"[{categorie}] Page {numero}/{config.NB_PAGES} (essai {essai}/{ESSAIS_MAX}) : {url}")
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
    os.makedirs(config.DOSSIER_PAGES, exist_ok=True)
    driver = Driver()
    driver.pilote.set_page_load_timeout(60)

    try:
        for categorie in config.CATEGORIES:
            print(f"\n=== Categorie : {categorie} ===")
            telechargees = 0

            for numero in range(1, config.NB_PAGES + 1):
                chemin = config.chemin_page(categorie, numero)

                if os.path.exists(chemin):
                    print(f"[{categorie}] Page {numero} deja enregistree, on passe.")
                    continue

                html = telecharger_page(driver, categorie, numero)
                if not html:
                    print(f"[{categorie}] Page {numero} non recuperee. Relance le script pour reessayer.")
                    continue

                with open(chemin, "w", encoding="utf-8") as fichier:
                    fichier.write(html)
                print(f"  -> enregistree : {chemin}")
                telechargees += 1

            if telechargees:
                time.sleep(config.PAUSE_ENTRE_CATEGORIES)

    except CaptchaDetecte as e:
        print(f"Captcha detecte : {e}")
        print("Relance le script plus tard : les pages deja enregistrees seront sautees.")
        print("Astuce : enregistre les pages a la main depuis ton navigateur (Ctrl+S).")
    finally:
        driver.fermer()


if __name__ == "__main__":
    main()