
from app.models.produit import Produit

class Depot:
    def __init__(self):
       
        self._produits = []

    def ajouter_produit(self, produit: Produit):
        """Ajoute un objet Produit au dépôt."""
        self._produits.append(produit)

    def ajouter_plusieurs(self, liste_produits: list):
        """Ajoute une liste complète d'objets Produit d'un coup."""
        self._produits.extend(liste_produits)

    def recuperer_tous(self):
        """Retourne la liste de tous les produits stockés."""
        return self._produits

    def vider(self):
        """Vide le dépôt de tous ses produits."""
        self._produits = []
