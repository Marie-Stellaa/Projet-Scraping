
class ConsoleView:
    @staticmethod
    def afficher_message(message: str):
        """Affiche un message d'information général."""
        print(f"[INFO] {message}")

    @staticmethod
    def afficher_erreur(message: str):
        """Affiche un message d'erreur de manière visible."""
        print(f"[ERREUR] ------------------\n{message}\n-------------------------")

    @staticmethod
    def afficher_produits(liste_produits):
        """Affiche la liste complète des produits récupérés dans la console."""
        print("\n--- LISTE DES PRODUITS COLLECTES ---")
        for index, produit in enumerate(liste_produits, 1):
           
            print(f"{index}. {produit}")
        print("------------------------------------\n")
