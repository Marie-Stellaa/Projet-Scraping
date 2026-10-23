# app/scraper/amazon_scraper.py
import sys
import time
import os
sys.path.append('.')  # Permet de trouver config.py à la racine du projet

from bs4 import BeautifulSoup
import config
from app.scraper.driver import Driver, CaptchaDetecte
from app.scraper.parsing import extraire_donnees_page


class AmazonScraper:
    def __init__(self):
        self.driver = None

    def executer_scraping(self):
        tous_les_produits = []

        # ========================================================
        # RECHERCHE EN MODE LOCAL (HORS-LIGNE)
        # ========================================================
        if config.MODE_LOCAL:
            print("Mode Hors-ligne active. Lecture des fichiers locaux...")
            dossier = "pages_locales"

            for page_interrogee in range(1, config.NB_PAGES + 1):
                chemin_fichier = os.path.join(dossier, f"amazon_laptop_page_{page_interrogee}.html")

                if not os.path.exists(chemin_fichier):
                    print(f"Fichier introuvable : {chemin_fichier}. Arret du processus.")
                    break

                print(f"Analyse du fichier local : {chemin_fichier}...")
                with open(chemin_fichier, "r", encoding="utf-8") as fichier:
                    html_brut = fichier.read()

                produits_page = extraire_donnees_page(html_brut)
                print(f"Extraction reussie : {len(produits_page)} produits detectes.")
                tous_les_produits.extend(produits_page)

        # ========================================================
        # RECHERCHE EN DIRECT (SUR INTERNET AVEC SELENIUM)
        # ========================================================
        else:
            print("Mode En ligne active. Initialisation du navigateur securise...")
            self.driver = Driver()
            url_actuelle = config.BASE_URL
            page_interrogee = 1

            try:
                while page_interrogee <= config.NB_PAGES:
                    print(f"Chargement et analyse de la page {page_interrogee}/{config.NB_PAGES} sur Amazon...")
                    html_brut = self.driver.charger(url_actuelle)

                    if not html_brut:
                        print(f"Attention : Impossible de recuperer le contenu de la page {page_interrogee}.")
                        break

                    produits_page = extraire_donnees_page(html_brut)
                    print(f"Extraction reussie : {len(produits_page)} produits detectes.")
                    tous_les_produits.extend(produits_page)

                    if page_interrogee >= config.NB_PAGES:
                        break

                    # Gestion de la pagination pour la page suivante
                    soup = BeautifulSoup(html_brut, "html.parser")
                    bouton_suivant = soup.select_one(config.SELECTEUR_SUIVANT)
                    href = bouton_suivant.get("href") if bouton_suivant else None

                    if isinstance(href, str) and href:
                        if href.startswith("http"):
                            url_actuelle = href
                        else:
                            url_actuelle = f"https://amazon.fr{href}"

                        page_interrogee += 1
                        time.sleep(config.DELAI)
                    else:
                        print("Fin des resultats : Aucun bouton 'Suivant' trouve.")
                        break

            except CaptchaDetecte as e:
                print(f"Blocage de securite : {e}")
            except Exception as e:
                print(f"Une erreur imprevue est survenue : {e}")
            finally:
                if self.driver:
                    print("Fermeture du navigateur...")
                    self.driver.fermer()

        print(f"Scraping termine ! Total de produits collectes : {len(tous_les_produits)}")
        return tous_les_produits