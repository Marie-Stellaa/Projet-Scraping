import os
import re
import unicodedata
from urllib.parse import quote_plus

SITE = "https://www.amazon.fr"
DOSSIER_PAGES = "pages_locales"

# Une recherche Amazon par ligne. Mets un # devant une ligne pour la desactiver.
CATEGORIES = [
    "laptop",
    "earpods",
    "smartphone",
    "tablette",
    "casque audio",
    "montre connectée",
    "appareil photo",
    "télévision",
    "enceinte bluetooth",
]

NB_PAGES = 3
DELAI = 4
PAUSE_ENTRE_CATEGORIES = 10
TIMEOUT = 15
MODE_LOCAL = True

SELECTEUR_PRODUIT = "div[data-component-type='s-search-result']"
SELECTEUR_TITRE = "h2 span"
SELECTEUR_PRIX = "span.a-price span.a-offscreen"
SELECTEUR_NOTE = "span.a-icon-alt"
SELECTEUR_SUIVANT = "a.s-pagination-next"


def _slug(texte):
    """'montre connectée' -> 'montre_connectee' (pour les noms de fichiers)."""
    sans_accents = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", sans_accents.lower()).strip("_")


def url_recherche(categorie, numero_page=1):
    return f"{SITE}/s?k={quote_plus(categorie)}&page={numero_page}"


def chemin_page(categorie, numero_page):
    return os.path.join(DOSSIER_PAGES, f"amazon_{_slug(categorie)}_page_{numero_page}.html")