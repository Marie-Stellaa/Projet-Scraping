import csv
import os
import time

import requests

from app.views.console_view import ConsoleView

ENTETES = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


class ExportView:
    @staticmethod
    def _en_dict(produit):
        """Accepte un dictionnaire ou un objet Produit (to_dict ou To_dict)."""
        if isinstance(produit, dict):
            return dict(produit)
        for nom in ("to_dict", "To_dict"):
            methode = getattr(produit, nom, None)
            if methode:
                return methode()
        raise AttributeError("Le produit n'a ni to_dict ni To_dict.")

    @staticmethod
    def _telecharger_image(url, nom_base, dossier_images, pause=0.5):
        """Télécharge l'image et renvoie le nom du fichier ('' si échec)."""
        if not url:
            return ""

        extension = os.path.splitext(url.split("?")[0])[1] or ".jpg"
        nom_fichier = f"{nom_base}{extension}"
        chemin = os.path.join(dossier_images, nom_fichier)

        if os.path.exists(chemin):
            return nom_fichier

        try:
            reponse = requests.get(url, headers=ENTETES, timeout=15)
            reponse.raise_for_status()
            with open(chemin, "wb") as f:
                f.write(reponse.content)
            time.sleep(pause)
            return nom_fichier
        except requests.RequestException as e:
            ConsoleView.afficher_erreur(f"Image non téléchargée ({nom_base}) : {e}")
            return ""

    @staticmethod
    def exporter_en_csv(liste_produits,
                        nom_fichier="exports/produits_amazon.csv",
                        dossier_images="data/images",
                        telecharger_images=True):
        """Enregistre les produits dans un CSV et télécharge leurs images."""
        if not liste_produits:
            ConsoleView.afficher_erreur("Aucun produit à exporter.")
            return

        dossier = os.path.dirname(nom_fichier)
        if dossier:
            os.makedirs(dossier, exist_ok=True)
        os.makedirs(dossier_images, exist_ok=True)

        lignes = []
        for numero, produit in enumerate(liste_produits, start=1):
            ligne = ExportView._en_dict(produit)

            if telecharger_images:
                nom_base = ligne.get("ASIN") or f"produit_{numero}"
                ligne["Image_Fichier"] = ExportView._telecharger_image(
                    ligne.get("Image_URL", ""), nom_base, dossier_images
                )
            else:
                ligne["Image_Fichier"] = ""

            lignes.append(ligne)

        colonnes = ["Page", "Titre", "Prix", "Note", "Image_URL", "Image_Fichier"]

        try:
            with open(nom_fichier, mode="w", encoding="utf-8-sig", newline="") as fichier:
                writer = csv.DictWriter(
                    fichier, fieldnames=colonnes, delimiter=";", extrasaction="ignore"
                )
                writer.writeheader()
                writer.writerows(lignes)

            ConsoleView.afficher_message(f"Fichier exporté avec succès : {nom_fichier}")
            ConsoleView.afficher_message(f"Images dans : {dossier_images}")
        except Exception as e:
            ConsoleView.afficher_erreur(f"Erreur lors de l'exportation CSV : {e}")