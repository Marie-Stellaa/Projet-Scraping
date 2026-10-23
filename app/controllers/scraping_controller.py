# app/controllers/scraping_controller.py
from app.scraper.amazon_scraper import AmazonScraper
from app.models.depot import Depot
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView


class ScrapingController:
    def __init__(self):
        self.scraper = AmazonScraper()
        self.depot = Depot()

    def lancer_application(self):
        """Démarre le flux complet de l'application."""
        ConsoleView.afficher_message("Demarrage de l'application de scraping...")

        # 1. Lancer le scraping et récupérer les objets Produit
        produits_recuperes = self.scraper.executer_scraping()

        if not produits_recuperes:
            ConsoleView.afficher_erreur("Le scraping n'a genere aucun resultat.")
            return

        # 2. Stocker les produits dans notre dépôt (Modèle)
        self.depot.ajouter_plusieurs(produits_recuperes)

        # 3. Récupérer les données validées depuis le dépôt
        donnees_finales = self.depot.recuperer_tous()

        # 4. Demander aux Vues d'afficher et d'exporter
        ConsoleView.afficher_produits(donnees_finales)

        ConsoleView.afficher_message("Lancement de l'exportation des donnees...")
        ExportView.exporter_en_csv(donnees_finales)

        ConsoleView.afficher_message("Application terminee avec succes !")