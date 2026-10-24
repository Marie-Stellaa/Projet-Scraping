import sys
sys.path.append('.')  # Permet à Python de regarder à la racine du projet

from bs4 import BeautifulSoup
import config
from app.models.produit import Produit


def extraire_donnees_page(html_brut, nom_page="", categorie=""):
    """
    Analyse le code HTML d'une page de recherche Amazon
    et renvoie une liste d'objets Produit.
    """
    soup = BeautifulSoup(html_brut, "html.parser")
    liste_produits = []

    blocs_produits = soup.select(config.SELECTEUR_PRODUIT)

    for bloc in blocs_produits:
        balise_titre = bloc.select_one(config.SELECTEUR_TITRE)
        titre = balise_titre.text.strip() if balise_titre else "Titre indisponible"

        balise_prix = bloc.select_one(config.SELECTEUR_PRIX)
        prix = balise_prix.text.strip() if balise_prix else "Prix non affiché"

        balise_note = bloc.select_one(config.SELECTEUR_NOTE)
        note = balise_note.text.strip() if balise_note else "Pas de note"

        balise_image = bloc.select_one("img.s-image")
        image_url = balise_image.get("src", "") if balise_image else ""

        asin = bloc.get("data-asin", "")

        liste_produits.append(
            Produit(titre, prix, note,
                    image_url=image_url, asin=asin, page=nom_page, categorie=categorie)
        )

    return liste_produits