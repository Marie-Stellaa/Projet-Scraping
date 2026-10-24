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
        """Affiche proprement le produit en texte."""
        return (f"[{self.categorie}] Produit: {self.titre} | "
                f"Prix: {self.prix} | Note: {self.note}")

    def to_dict(self):
        """Convertit l'objet en dictionnaire (utilisé par l'export CSV)."""
        return {
            "Categorie": self.categorie,
            "Page": self.page,
            "Titre": self.titre,
            "Prix": self.prix,
            "Note": self.note,
            "Image_URL": self.image_url,
            "ASIN": self.asin,
        }