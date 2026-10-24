
from app.scraper.amazon_scraper import AmazonScraper
from app.models.depot import Depot
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView

FICHIER_EXPORT = "exports/produits_amazon.csv"


class ScrapingController:
    def __init__(self):
        self.scraper = AmazonScraper()
        self.depot = Depot()

    def recuperer_produits(self):
        """Lance le scraping et renvoie la liste des produits (utilisé par l'interface graphique)."""
       
        self.depot = Depot()

        produits_recuperes = self.scraper.executer_scraping()
        if not produits_recuperes:
            return []

        self.depot.ajouter_plusieurs(produits_recuperes)
        return self.depot.recuperer_tous()

    def exporter(self):
        """Exporte les produits du dépôt en CSV et renvoie le chemin du fichier."""
        donnees_finales = self.depot.recuperer_tous()
        ExportView.exporter_en_csv(donnees_finales, nom_fichier=FICHIER_EXPORT)
        return FICHIER_EXPORT

    def lancer_application(self):
        """Démarre le flux complet de l'application."""
        ConsoleView.afficher_message("Demarrage de l'application de scraping...")

        
        produits_recuperes = self.scraper.executer_scraping()

        if not produits_recuperes:
            ConsoleView.afficher_erreur("Le scraping n'a genere aucun resultat.")
            return

      
        self.depot.ajouter_plusieurs(produits_recuperes)

     
        donnees_finales = self.depot.recuperer_tous()

      
        ConsoleView.afficher_produits(donnees_finales)

        ConsoleView.afficher_message("Lancement de l'exportation des donnees...")
        ExportView.exporter_en_csv(donnees_finales)

        ConsoleView.afficher_message("Application terminee avec succes !")