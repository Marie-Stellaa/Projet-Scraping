import sys
import time
import os
sys.path.append('.')

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

            for categorie in config.CATEGORIES:
                print(f"--- Categorie : {categorie} ---")

                for numero_page in range(1, config.NB_PAGES + 1):
                    chemin_fichier = config.chemin_page(categorie, numero_page)

                    if not os.path.exists(chemin_fichier):
                        print(f"Fichier introuvable : {chemin_fichier}. Categorie ignoree (lance telecharger_pages.py).")
                        break

                    print(f"Analyse du fichier local : {chemin_fichier}...")
                    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
                        html_brut = fichier.read()

                    produits_page = extraire_donnees_page(
                        html_brut, os.path.basename(chemin_fichier), categorie
                    )
                    print(f"Extraction reussie : {len(produits_page)} produits detectes.")
                    tous_les_produits.extend(produits_page)

        # ========================================================
        # RECHERCHE EN DIRECT (SUR INTERNET AVEC SELENIUM)
        # ========================================================
        else:
            print("Mode En ligne active. Initialisation du navigateur securise...")
            self.driver = Driver()

            try:
                for categorie in config.CATEGORIES:
                    print(f"--- Categorie : {categorie} ---")
                    url_actuelle = config.url_recherche(categorie, 1)
                    numero_page = 1
                    bloque = False

                    while numero_page <= config.NB_PAGES:
                        print(f"Chargement et analyse de la page {numero_page}/{config.NB_PAGES} sur Amazon...")
                        html_brut = self.driver.charger(url_actuelle)

                        if not html_brut:
                            print(f"Attention : Impossible de recuperer le contenu de la page {numero_page}.")
                            print("Arret du scraping en ligne pour eviter un blocage.")
                            bloque = True
                            break

                        nom_page = os.path.basename(config.chemin_page(categorie, numero_page))
                        produits_page = extraire_donnees_page(html_brut, nom_page, categorie)
                        print(f"Extraction reussie : {len(produits_page)} produits detectes.")
                        tous_les_produits.extend(produits_page)

                        if numero_page >= config.NB_PAGES:
                            break

                        # Gestion de la pagination pour la page suivante
                        soup = BeautifulSoup(html_brut, "html.parser")
                        bouton_suivant = soup.select_one(config.SELECTEUR_SUIVANT)
                        href = bouton_suivant.get("href") if bouton_suivant else None

                        if isinstance(href, str) and href:
                            if href.startswith("http"):
                                url_actuelle = href
                            else:
                                url_actuelle = f"{config.SITE}{href}"

                            numero_page += 1
                            time.sleep(config.DELAI)
                        else:
                            print("Fin des resultats : Aucun bouton 'Suivant' trouve.")
                            break

                    if bloque:
                        break
                    time.sleep(config.PAUSE_ENTRE_CATEGORIES)

            except CaptchaDetecte as e:
                print(f"Blocage de securite : {e}")
            except Exception as e:
                print(f"Une erreur imprevue est survenue : {e}")
            finally:
                if self.driver:
                    print("Fermeture du navigateur...")
                    self.driver.fermer()

        # Un meme produit peut sortir dans plusieurs pages ou categories : on le garde une fois
        produits_uniques = []
        asins_vus = set()
        for produit in tous_les_produits:
            if produit.asin:
                if produit.asin in asins_vus:
                    continue
                asins_vus.add(produit.asin)
            produits_uniques.append(produit)

        doublons = len(tous_les_produits) - len(produits_uniques)
        print(f"Scraping termine ! Total de produits collectes : {len(produits_uniques)} ({doublons} doublons ignores).")
        return produits_uniques