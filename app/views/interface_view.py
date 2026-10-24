import threading
import tkinter as tk
from tkinter import ttk, messagebox

import config


class InterfaceView(tk.Tk):
    def __init__(self, controleur):
        super().__init__()
        self.controleur = controleur
        self.produits = []
        self._thread = None
        self._tache = None        
        self._resultat = None
        self._erreur = None

        self.title("Scraper Amazon - Produits électroniques")
        self.geometry("1100x620")
        self.minsize(850, 450)
        self._construire()

    # ------------------------------------------------------------------
    # Construction de la fenêtre
    # ------------------------------------------------------------------
    def _construire(self):
        # --- Bandeau de titre ---
        titre = tk.Label(self, text="Scraper Amazon - Produits électroniques",
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
        self.btn_base = ttk.Button(actions, text="Charger depuis la base", command=self._charger_base)
        self.btn_base.pack(side="right", padx=8)
        self.btn_lancer = ttk.Button(actions, text="Lancer le scraping", command=self._lancer)
        self.btn_lancer.pack(side="right")

        # --- Barre de recherche ---
        recherche = ttk.Frame(self, padding=(10, 0, 10, 8))
        recherche.pack(fill="x")
        ttk.Label(recherche, text="Rechercher (titre ou catégorie) :").pack(side="left")
        self.var_filtre = tk.StringVar()
        self.var_filtre.trace_add("write", self._filtrer)
        ttk.Entry(recherche, textvariable=self.var_filtre, width=40).pack(side="left", padx=8)

        # --- Tableau des produits ---
        zone = ttk.Frame(self, padding=(10, 0, 10, 0))
        zone.pack(fill="both", expand=True)

        colonnes = ("categorie", "titre", "prix", "note")
        self.tableau = ttk.Treeview(zone, columns=colonnes, show="headings")
        self.tableau.heading("categorie", text="Catégorie")
        self.tableau.heading("titre", text="Titre")
        self.tableau.heading("prix", text="Prix")
        self.tableau.heading("note", text="Note")
        self.tableau.column("categorie", width=130, anchor="center")
        self.tableau.column("titre", width=520, anchor="w")
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

        self._charger_base()

    # ------------------------------------------------------------------
    # Gestion des tâches en arrière-plan (scraping et export)
    # ------------------------------------------------------------------
    def _tache_en_cours(self):
        return self._thread is not None and self._thread.is_alive()

    def _basculer_boutons(self, etat):
        for bouton in (self.btn_lancer, self.btn_base, self.btn_exporter):
            bouton.config(state=etat)

    def _demarrer_tache(self, nom, fonction, message):
        """Lance 'fonction' dans un thread pour ne pas figer la fenêtre."""
        if self._tache_en_cours():
            return

        self._tache = nom
        self._resultat = None
        self._erreur = None

        self._basculer_boutons("disabled")
        self.var_statut.set(message)
        self.progression.start(12)

        self._thread = threading.Thread(target=self._travail, args=(fonction,), daemon=True)
        self._thread.start()
        self.after(200, self._verifier)

    def _travail(self, fonction):
        try:
            self._resultat = fonction()
        except Exception as e:
            self._erreur = e

    def _verifier(self):
        """Regarde toutes les 200 ms si le thread a fini."""
        if self._tache_en_cours():
            self.after(200, self._verifier)
            return

        self.progression.stop()
        self._basculer_boutons("normal")

        if self._erreur is not None:
            if self._tache == "scraping":
                self.var_statut.set("Erreur pendant le scraping.")
                messagebox.showerror("Erreur", str(self._erreur))
            else:
                self.var_statut.set("Erreur pendant l'export.")
                messagebox.showerror("Erreur d'export", str(self._erreur))
            return

        if self._tache == "scraping":
            self._fin_scraping()
        else:
            self._fin_export()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _lancer(self):
        if self._tache_en_cours():
            return
        config.MODE_LOCAL = self.var_local.get()
        self._demarrer_tache("scraping", self.controleur.recuperer_produits,
                             "Scraping en cours, patiente...")

    def _fin_scraping(self):
        self._remplacer_produits(self._resultat or [])

        if self.controleur.nb_nouveaux == 0:
            if config.MODE_LOCAL:
                detail = "En mode hors-ligne, vérifie le dossier pages_locales."
            else:
                detail = "Amazon a peut-être bloqué la requête (captcha ou erreur réseau)."
            messagebox.showwarning(
                "Aucun résultat",
                "Aucun nouveau produit trouvé.\n"
                "Les données déjà présentes dans la base ont été conservées.\n\n" + detail)

    def _charger_base(self):
        """Affiche les produits stockés dans la base SQLite."""
        if self._tache_en_cours():
            return
        try:
            produits = self.controleur.charger_depuis_base()
        except Exception as e:
            messagebox.showerror("Erreur base de données", str(e))
            return

        self._remplacer_produits(produits)
        if self.produits:
            self.var_statut.set(f"{len(self.produits)} produit(s) chargé(s) depuis la base SQLite.")

    def _exporter(self):
        if self._tache_en_cours():
            return
        if not self.produits:
            messagebox.showinfo("Export", "Aucun produit à exporter. Lance d'abord le scraping.")
            return
        self._demarrer_tache("export", self.controleur.exporter,
                             "Export en cours (téléchargement des images)...")

    def _fin_export(self):
        self.var_statut.set("Export terminé.")
        messagebox.showinfo("Export", f"Fichier exporté :\n{self._resultat}")

    # ------------------------------------------------------------------
    # Affichage du tableau
    # ------------------------------------------------------------------
    def _remplacer_produits(self, produits):
        self.produits = produits
        self.var_filtre.set("")         
        self._afficher(self.produits)

    def _afficher(self, liste):
        self.tableau.delete(*self.tableau.get_children())
        for p in liste:
            self.tableau.insert("", "end", values=(p.categorie, p.titre, p.prix, p.note))
        self.var_statut.set(f"{len(liste)} produit(s) affiché(s) sur {len(self.produits)}.")

    def _filtrer(self, *_):
        texte = self.var_filtre.get().strip().lower()
        if texte:
            liste = [p for p in self.produits
                     if texte in p.titre.lower() or texte in p.categorie.lower()]
        else:
            liste = self.produits
        self._afficher(liste)