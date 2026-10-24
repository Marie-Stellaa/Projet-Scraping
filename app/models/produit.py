class Produit:
    def __init__(self, titre: str, prix: str, note: str,
                 image_url: str = "", asin: str = "", page: str = "", categorie: str = ""):
        self.titre = titre
        self.prix = prix
        self.note = note
        self.image_url = image_url
        self.asin = asin
        self.page = page
        self.categorie = categorie

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
            "Categorie": self.categorie,
            "Page": self.page,
            "Titre": self.titre,
            "Prix": self.prix,
            "Note": self.note,
            "Image_URL": self.image_url,
            "ASIN": self.asin
        }