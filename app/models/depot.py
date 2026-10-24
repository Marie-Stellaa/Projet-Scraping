import os
import sqlite3
from contextlib import closing

from app.models.produit import Produit

COLONNES_SUPPLEMENTAIRES = ("categorie", "page", "asin", "image_url")


class Depot:
    def __init__(self, chemin_base="data/produits.db"):
        self.chemin_base = chemin_base
        dossier = os.path.dirname(chemin_base)
        if dossier:
            os.makedirs(dossier, exist_ok=True)
        self._creer_table()

    # ------------------------------------------------------------------
    # Outils internes
    # ------------------------------------------------------------------
    def _connexion(self):
        """Ouvre une connexion neuve (une par opération : sûr avec les threads)."""
        return sqlite3.connect(self.chemin_base)

    def _creer_table(self):
        with closing(self._connexion()) as cn:
            cn.execute(
                """
                CREATE TABLE IF NOT EXISTS produit (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre      TEXT NOT NULL,
                    prix       TEXT,
                    note       TEXT,
                    categorie  TEXT,
                    page       TEXT,
                    asin       TEXT,
                    image_url  TEXT,
                    date_ajout TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

         
            existantes = {ligne[1] for ligne in cn.execute("PRAGMA table_info(produit)")}
            for nom in COLONNES_SUPPLEMENTAIRES:
                if nom not in existantes:
                    cn.execute(f"ALTER TABLE produit ADD COLUMN {nom} TEXT")

            cn.commit()

    # ------------------------------------------------------------------
    # Opérations (CRUD)
    # ------------------------------------------------------------------
    def ajouter_produit(self, produit: Produit):
        """Ajoute un objet Produit dans la base."""
        self.ajouter_plusieurs([produit])

    def ajouter_plusieurs(self, liste_produits: list):
        """Ajoute une liste d'objets Produit d'un coup."""
        lignes = [
            (p.titre, p.prix, p.note, p.categorie, p.page, p.asin, p.image_url)
            for p in liste_produits
        ]
        with closing(self._connexion()) as cn:
            cn.executemany(
                "INSERT INTO produit (titre, prix, note, categorie, page, asin, image_url) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                lignes,
            )
            cn.commit()

    def recuperer_tous(self):
        """Lit la base et renvoie une liste d'objets Produit complets."""
        with closing(self._connexion()) as cn:
            lignes = cn.execute(
                "SELECT titre, prix, note, categorie, page, asin, image_url "
                "FROM produit ORDER BY id"
            ).fetchall()
        return [
            Produit(titre, prix, note,
                    image_url=image_url or "", asin=asin or "",
                    page=page or "", categorie=categorie or "")
            for (titre, prix, note, categorie, page, asin, image_url) in lignes
        ]

    def compter(self):
        with closing(self._connexion()) as cn:
            return cn.execute("SELECT COUNT(*) FROM produit").fetchone()[0]

    def vider(self):
        """Supprime tous les produits de la base."""
        with closing(self._connexion()) as cn:
            cn.execute("DELETE FROM produit")
            cn.commit()