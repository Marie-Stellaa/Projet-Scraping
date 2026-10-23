from pathlib import Path

from bs4 import BeautifulSoup

from app.views.console_view import ConsoleView
from app.views.export_view import ExportView

DOSSIER_PAGES = Path("pages_locales")


def texte(element):
    return element.get_text(strip=True) if element else ""


def extraire_produits(html, nom_page):
    soupe = BeautifulSoup(html, "html.parser")
    produits = []

    for carte in soupe.select('div[data-component-type="s-search-result"]'):
        titre = texte(carte.select_one("h2"))
        if not titre:
            continue

        balise_image = carte.select_one("img.s-image")

        produits.append({
            "Page": nom_page,
            "Titre": titre,
            "Prix": texte(carte.select_one(".a-price .a-offscreen")),
            "Note": texte(carte.select_one(".a-icon-alt")),
            "Image_URL": balise_image.get("src", "") if balise_image else "",
            "ASIN": carte.get("data-asin", ""),
        })

    return produits


def main():
    if not DOSSIER_PAGES.exists():
        ConsoleView.afficher_erreur(f"Le dossier '{DOSSIER_PAGES}' est introuvable.")
        return

    fichiers = sorted(list(DOSSIER_PAGES.glob("*.html")) + list(DOSSIER_PAGES.glob("*.htm")))
    if not fichiers:
        ConsoleView.afficher_erreur(f"Aucun fichier .html dans '{DOSSIER_PAGES}'.")
        return

    tous = []
    for fichier in fichiers:
        html = fichier.read_text(encoding="utf-8", errors="ignore")
        produits = extraire_produits(html, fichier.name)
        ConsoleView.afficher_message(f"{fichier.name} : {len(produits)} produits")
        tous.extend(produits)

    ExportView.exporter_en_csv(tous)


if __name__ == "__main__":
    main()