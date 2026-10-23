# app/models/produit.py

class Produit:
    def __init__(self, titre: str, prix: str, note: str):
        self.titre = titre
        self.prix = prix
        self.note = note

    def __str__(self):
        """
        Permet d'afficher proprement le produit textuellement.
        """
        return f"Produit: {self.titre} | Prix: {self.prix} | Note: {self.note}"

    def To_dict(self):
        """
        Convertit l'objet en dictionnaire.
        Très utile pour l'exportateur CSV ou Excel avec Pandas.
        """
        return {
            "Titre": self.titre,
            "Prix": self.prix,
            "Note": self.note
        }
