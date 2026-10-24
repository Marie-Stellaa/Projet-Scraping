from app.scraper.amazon_scraper import AmazonScraper
from app.models.depot import Depot
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView

FICHIER_EXPORT = "exports/produits_amazon.csv"


class ScrapingController:
    def __init__(self):
        self.scraper = AmazonScraper()
        self.depot = Depot()
        self.nb_nouveaux = 0   

    # ------------------------------------------------------------------
    # Méthodes utilisées par l'interface graphique
    # ------------------------------------------------------------------
    def recuperer_produits(self):
        """
        Lance le scraping. La base n'est remplacée que si de nouveaux produits
        ont été récupérés : en cas d'échec (captcha, réseau...), les anciennes
        données sont conservées.
        """
        produits = self.scraper.executer_scraping()
        self.nb_nouveaux = len(produits)

        if produits:
            self.depot.vider()
            self.depot.ajouter_plusieurs(produits)

        return self.depot.recuperer_tous()

    def charger_depuis_base(self):
        """Relit les produits déjà enregistrés dans la base SQLite."""
        return self.depot.recuperer_tous()

    def exporter(self):
        """Exporte le contenu de la base en CSV et renvoie le chemin du fichier."""
        ExportView.exporter_en_csv(self.depot.recuperer_tous(), FICHIER_EXPORT)
        return FICHIER_EXPORT

    # ------------------------------------------------------------------
    # Mode console
    # ------------------------------------------------------------------
    def lancer_application(self):
        """Démarre le flux complet de l'application en console."""
        ConsoleView.afficher_message("Demarrage de l'application de scraping...")

        produits = self.recuperer_produits()

        if self.nb_nouveaux == 0:
            ConsoleView.afficher_erreur(
                "Le scraping n'a genere aucun resultat. La base n'a pas ete modifiee."
            )
            return

        ConsoleView.afficher_produits(produits)

        ConsoleView.afficher_message("Lancement de l'exportation des donnees...")
        self.exporter()

        ConsoleView.afficher_message("Application terminee avec succes !")