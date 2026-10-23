# app/views/interface_view.py
# Vue graphique (Tkinter) : elle affiche et reçoit les clics,
# mais tout le travail est délégué au contrôleur.
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import config


class InterfaceView(tk.Tk):
    def __init__(self, controleur):
        super().__init__()
        self.controleur = controleur
        self.produits = []        # tous les produits récupérés
        self._thread = None       # thread qui fait le scraping
        self._resultat = None
        self._erreur = None

        self.title("Scraper Amazon - Laptops")
        self.geometry("1000x600")
        self.minsize(800, 450)
        self._construire()

    # ------------------------------------------------------------------
    # Construction de la fenêtre
    # ------------------------------------------------------------------
    def _construire(self):
        # --- Bandeau de titre ---
        titre = tk.Label(self, text="Scraper Amazon - Ordinateurs portables",
                         bg="#1F3864", fg="white", font=("Segoe UI", 16, "bold"), pady=12)
        titre.pack(fill="x")

        # --- Barre d'actions ---
        actions = ttk.Frame(self, padding=10)
        actions.pack(fill="x")

        self.var_local = tk.BooleanVar(value=config.MODE_LOCAL)
        ttk.Checkbutton(actions, text="Mode hors-ligne (fichiers locaux)",
                        variable=self.var_local).pack(side="left")

        self.btn_exporter = ttk.Button(actions, text="Exporter en CSV", command=self._exporter)
        self.btn_exporter.pack(side="right")
        self.btn_lancer = ttk.Button(actions, text="Lancer le scraping", command=self._lancer)
        self.btn_lancer.pack(side="right", padx=8)

        # --- Barre de recherche ---
        recherche = ttk.Frame(self, padding=(10, 0, 10, 8))
        recherche.pack(fill="x")
        ttk.Label(recherche, text="Rechercher dans les titres :").pack(side="left")
        self.var_filtre = tk.StringVar()
        self.var_filtre.trace_add("write", self._filtrer)
        ttk.Entry(recherche, textvariable=self.var_filtre, width=40).pack(side="left", padx=8)

        # --- Tableau des produits ---
        zone = ttk.Frame(self, padding=(10, 0, 10, 0))
        zone.pack(fill="both", expand=True)

        colonnes = ("titre", "prix", "note")
        self.tableau = ttk.Treeview(zone, columns=colonnes, show="headings")
        self.tableau.heading("titre", text="Titre")
        self.tableau.heading("prix", text="Prix")
        self.tableau.heading("note", text="Note")
        self.tableau.column("titre", width=600, anchor="w")
        self.tableau.column("prix", width=120, anchor="center")
        self.tableau.column("note", width=180, anchor="center")

        barre = ttk.Scrollbar(zone, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=barre.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        barre.pack(side="right", fill="y")

        # --- Barre de progression + statut ---
        bas = ttk.Frame(self, padding=10)
        bas.pack(fill="x")
        self.var_statut = tk.StringVar(value="Prêt. Clique sur « Lancer le scraping ».")
        ttk.Label(bas, textvariable=self.var_statut).pack(side="left")
        self.progression = ttk.Progressbar(bas, mode="indeterminate", length=160)
        self.progression.pack(side="right")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _lancer(self):
        if self._thread is not None and self._thread.is_alive():
            return

        config.MODE_LOCAL = self.var_local.get()   # applique le choix de l'utilisateur
        self._resultat = None
        self._erreur = None

        self.btn_lancer.config(state="disabled")
        self.var_statut.set("Scraping en cours, patiente...")
        self.progression.start(12)

        # Le scraping tourne dans un thread à part pour ne pas figer la fenêtre
        self._thread = threading.Thread(target=self._travail, daemon=True)
        self._thread.start()
        self.after(200, self._verifier)

    def _travail(self):
        try:
            self._resultat = self.controleur.recuperer_produits()
        except Exception as e:
            self._erreur = e

    def _verifier(self):
        """Regarde toutes les 200 ms si le thread a fini."""
        if self._thread is not None and self._thread.is_alive():
            self.after(200, self._verifier)
            return

        self.progression.stop()
        self.btn_lancer.config(state="normal")

        if self._erreur is not None:
            self.var_statut.set("Erreur pendant le scraping.")
            messagebox.showerror("Erreur", str(self._erreur))
            return

        self.produits = self._resultat or []
        self.var_filtre.set("")
        self._afficher(self.produits)
        if not self.produits:
            messagebox.showwarning(
                "Aucun résultat",
                "Aucun produit trouvé.\nEn mode hors-ligne, vérifie le dossier pages_locales.")

    def _afficher(self, liste):
        self.tableau.delete(*self.tableau.get_children())
        for p in liste:
            self.tableau.insert("", "end", values=(p.titre, p.prix, p.note))
        self.var_statut.set(f"{len(liste)} produit(s) affiché(s) sur {len(self.produits)}.")

    def _filtrer(self, *_):
        texte = self.var_filtre.get().strip().lower()
        if texte:
            liste = [p for p in self.produits if texte in p.titre.lower()]
        else:
            liste = self.produits
        self._afficher(liste)

    def _exporter(self):
        if not self.produits:
            messagebox.showinfo("Export", "Aucun produit à exporter. Lance d'abord le scraping.")
            return
        try:
            chemin = self.controleur.exporter()
            messagebox.showinfo("Export", f"Fichier exporté :\n{chemin}")
        except Exception as e:
            messagebox.showerror("Erreur d'export", str(e))