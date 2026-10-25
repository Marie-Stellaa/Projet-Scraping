import math
import os
import re
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox

from PIL import Image, ImageTk

import config
from app.views.export_view import ExportView

DOSSIER_IMAGES = "data/images"
PAR_PAGE = 24            # nombre de produits par page
TAILLE_IMG = 170         # taille de l'image dans une carte
CARTE_LARGEUR = 215      # largeur approximative d'une carte
TOUTES = "Toutes les catégories"
TRIS = ["Pertinence", "Prix croissant", "Prix décroissant", "Meilleures notes"]


# ----------------------------------------------------------------------
# Petites fonctions utiles
# ----------------------------------------------------------------------
def prix_en_nombre(texte):
    """'1 299,99 €' -> 1299.99 ; renvoie None si aucun prix."""
    nettoye = re.sub(r"[^\d,.]", "", texte or "")
    if not nettoye:
        return None
    if "," in nettoye:
        nettoye = nettoye.replace(".", "").replace(",", ".")
    try:
        return float(nettoye)
    except ValueError:
        return None


def note_en_nombre(texte):
    """'4,4 sur 5 étoiles' -> 4.4 ; renvoie None si pas de note."""
    trouve = re.search(r"\d+(?:[,.]\d+)?", texte or "")
    if not trouve:
        return None
    return float(trouve.group().replace(",", "."))


def etoiles(note):
    """4.4 -> '★★★★☆ 4,4'"""
    if note is None:
        return "Pas de note"
    pleines = int(round(note))
    return "★" * pleines + "☆" * (5 - pleines) + "  " + f"{note:.1f}".replace(".", ",")


def raccourcir(texte, maximum):
    if len(texte) <= maximum:
        return texte
    return texte[:maximum - 1].rstrip() + "…"


# ----------------------------------------------------------------------
# Fenêtre principale
# ----------------------------------------------------------------------
class InterfaceView(tk.Tk):
    def __init__(self, controleur):
        super().__init__()
        self.controleur = controleur
        self.produits = []            # tous les produits chargés
        self._liste_courante = []     # produits après filtre et tri
        self.page = 0
        self._colonnes = 5
        self._muet = False            # évite de réafficher plusieurs fois de suite
        self._cache = {}              # images déjà chargées (évite de les relire)
        self._tentes = set()          # ASIN dont on a déjà tenté le téléchargement
        self._thread = None           # thread de scraping ou d'export
        self._thread_images = None    # thread de téléchargement des images
        self._tache = None
        self._resultat = None
        self._erreur = None

        self.title("Scraper Amazon - Produits électroniques")
        self.geometry("1150x700")
        self.minsize(700, 500)
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

        # --- Filtres : recherche, catégorie, tri ---
        filtres = ttk.Frame(self, padding=(10, 0, 10, 8))
        filtres.pack(fill="x")

        ttk.Label(filtres, text="Rechercher :").pack(side="left")
        self.var_filtre = tk.StringVar()
        self.var_filtre.trace_add("write", self._filtres_changes)
        ttk.Entry(filtres, textvariable=self.var_filtre, width=28).pack(side="left", padx=(6, 16))

        ttk.Label(filtres, text="Catégorie :").pack(side="left")
        self.var_categorie = tk.StringVar(value=TOUTES)
        self.combo_cat = ttk.Combobox(filtres, textvariable=self.var_categorie,
                                      values=[TOUTES], state="readonly", width=22)
        self.combo_cat.pack(side="left", padx=(6, 16))
        self.combo_cat.bind("<<ComboboxSelected>>", self._filtres_changes)

        ttk.Label(filtres, text="Trier par :").pack(side="left")
        self.var_tri = tk.StringVar(value=TRIS[0])
        combo_tri = ttk.Combobox(filtres, textvariable=self.var_tri,
                                 values=TRIS, state="readonly", width=18)
        combo_tri.pack(side="left", padx=6)
        combo_tri.bind("<<ComboboxSelected>>", self._filtres_changes)

        ttk.Label(filtres, text="Clique sur un produit pour voir sa fiche.",
                  foreground="#666666").pack(side="right")

        # --- Barre de statut (tout en bas) ---
        bas = ttk.Frame(self, padding=10)
        bas.pack(side="bottom", fill="x")
        self.var_statut = tk.StringVar(value="Prêt. Clique sur « Lancer le scraping ».")
        ttk.Label(bas, textvariable=self.var_statut).pack(side="left")
        self.progression = ttk.Progressbar(bas, mode="indeterminate", length=160)
        self.progression.pack(side="right")

        # --- Pagination (au-dessus de la barre de statut) ---
        pagination = ttk.Frame(self, padding=(10, 4))
        pagination.pack(side="bottom", fill="x")
        centre = ttk.Frame(pagination)
        centre.pack()
        self.btn_prec = ttk.Button(centre, text="← Précédent", command=self._page_precedente)
        self.btn_prec.pack(side="left")
        self.var_page = tk.StringVar(value="Page 1 / 1")
        ttk.Label(centre, textvariable=self.var_page, padding=(20, 0)).pack(side="left")
        self.btn_suiv = ttk.Button(centre, text="Suivant →", command=self._page_suivante)
        self.btn_suiv.pack(side="left")

        # --- Zone des cartes produits (canvas défilant) ---
        zone = ttk.Frame(self)
        zone.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(zone, bg="#eaeded", highlightthickness=0)
        barre = ttk.Scrollbar(zone, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grille = tk.Frame(self.canvas, bg="#eaeded")
        self._fenetre_grille = self.canvas.create_window((0, 0), window=self.grille, anchor="nw")
        self.grille.bind("<Configure>",
                         lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._au_redimensionnement)

        # Molette de la souris
        self.canvas.bind_all("<MouseWheel>", self._molette)
        self.canvas.bind_all("<Button-4>", self._molette)
        self.canvas.bind_all("<Button-5>", self._molette)

        self._charger_base()

    def _molette(self, event):
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(delta, "units")

    def _au_redimensionnement(self, event):
        """Adapte le nombre de colonnes à la largeur de la fenêtre."""
        self.canvas.itemconfigure(self._fenetre_grille, width=event.width)
        colonnes = max(1, event.width // CARTE_LARGEUR)
        if colonnes != self._colonnes:
            self._colonnes = colonnes
            self._afficher_page(remonter=False)

    # ------------------------------------------------------------------
    # Images
    # ------------------------------------------------------------------
    def _chemin_image(self, produit):
        """Cherche l'image du produit dans data/images (nommée d'après l'ASIN)."""
        if not produit.asin:
            return None
        for extension in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            chemin = os.path.join(DOSSIER_IMAGES, produit.asin + extension)
            if os.path.exists(chemin):
                return chemin
        return None

    def _photo(self, produit, taille):
        """Renvoie l'image redimensionnée, ou None si elle n'est pas disponible."""
        cle = (produit.asin, taille)
        if cle in self._cache:
            return self._cache[cle]

        chemin = self._chemin_image(produit)
        if chemin is None:
            return None
        try:
            image = Image.open(chemin).convert("RGB")
            image.thumbnail(taille)
            photo = ImageTk.PhotoImage(image)
        except Exception:
            return None

        self._cache[cle] = photo
        return photo

    def _telecharger_images_manquantes(self, produits):
        """Télécharge en arrière-plan les images absentes des produits affichés."""
        if self._thread_images is not None and self._thread_images.is_alive():
            return

        a_telecharger = [p for p in produits
                         if p.asin and p.image_url and p.asin not in self._tentes
                         and self._chemin_image(p) is None]
        if not a_telecharger:
            return

        for p in a_telecharger:
            self._tentes.add(p.asin)

        os.makedirs(DOSSIER_IMAGES, exist_ok=True)
        self._thread_images = threading.Thread(
            target=self._travail_images, args=(a_telecharger,), daemon=True)
        self._thread_images.start()
        self.after(400, self._verifier_images)

    def _travail_images(self, produits):
        for p in produits:
            ExportView._telecharger_image(p.image_url, p.asin, DOSSIER_IMAGES, pause=0.1)

    def _verifier_images(self):
        if self._thread_images is not None and self._thread_images.is_alive():
            self.after(400, self._verifier_images)
            return
        self._afficher_page(remonter=False)     # affiche les images arrivées

    # ------------------------------------------------------------------
    # Tâches en arrière-plan (scraping et export)
    # ------------------------------------------------------------------
    def _tache_en_cours(self):
        return self._thread is not None and self._thread.is_alive()

    def _basculer_boutons(self, etat):
        for bouton in (self.btn_lancer, self.btn_base, self.btn_exporter):
            bouton.config(state=etat)

    def _demarrer_tache(self, nom, fonction, message):
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
    # Filtres, tri et pagination
    # ------------------------------------------------------------------
    def _remplacer_produits(self, produits):
        self.produits = produits

        categories = sorted({p.categorie for p in produits if p.categorie})
        self.combo_cat["values"] = [TOUTES] + categories

        self._muet = True                   # on réinitialise sans réafficher 3 fois
        self.var_filtre.set("")
        self.var_categorie.set(TOUTES)
        self.var_tri.set(TRIS[0])
        self._muet = False

        self.page = 0
        self._appliquer_filtres()
        self._afficher_page()

    def _filtres_changes(self, *_):
        if self._muet:
            return
        self.page = 0
        self._appliquer_filtres()
        self._afficher_page()

    def _appliquer_filtres(self):
        texte = self.var_filtre.get().strip().lower()
        categorie = self.var_categorie.get()

        liste = self.produits
        if categorie != TOUTES:
            liste = [p for p in liste if p.categorie == categorie]
        if texte:
            liste = [p for p in liste if texte in p.titre.lower()]

        self._liste_courante = self._trier(liste)

    def _trier(self, liste):
        tri = self.var_tri.get()

        if tri in ("Prix croissant", "Prix décroissant"):
            avec = [p for p in liste if prix_en_nombre(p.prix) is not None]
            sans = [p for p in liste if prix_en_nombre(p.prix) is None]
            avec.sort(key=lambda p: prix_en_nombre(p.prix), reverse=(tri == "Prix décroissant"))
            return avec + sans

        if tri == "Meilleures notes":
            avec = [p for p in liste if note_en_nombre(p.note) is not None]
            sans = [p for p in liste if note_en_nombre(p.note) is None]
            avec.sort(key=lambda p: note_en_nombre(p.note), reverse=True)
            return avec + sans

        return liste

    def _nb_pages(self):
        return max(1, math.ceil(len(self._liste_courante) / PAR_PAGE))

    def _page_precedente(self):
        if self.page > 0:
            self.page -= 1
            self._afficher_page()

    def _page_suivante(self):
        if self.page < self._nb_pages() - 1:
            self.page += 1
            self._afficher_page()

    # ------------------------------------------------------------------
    # Affichage de la grille de produits
    # ------------------------------------------------------------------
    def _afficher_page(self, remonter=True):
        total = len(self._liste_courante)
        nb_pages = self._nb_pages()
        self.page = min(self.page, nb_pages - 1)

        debut = self.page * PAR_PAGE
        morceau = self._liste_courante[debut:debut + PAR_PAGE]

        for widget in self.grille.winfo_children():
            widget.destroy()

        for c in range(12):
            self.grille.columnconfigure(c, weight=1 if c < self._colonnes else 0)

        if not morceau:
            tk.Label(self.grille, text="Aucun produit à afficher.", bg="#eaeded",
                     fg="#555555", font=("Segoe UI", 12), pady=40).grid(row=0, column=0)
        for index, produit in enumerate(morceau):
            self._creer_carte(produit, index // self._colonnes, index % self._colonnes)

        self.var_page.set(f"Page {self.page + 1} / {nb_pages}")
        self.btn_prec.config(state="normal" if self.page > 0 else "disabled")
        self.btn_suiv.config(state="normal" if self.page < nb_pages - 1 else "disabled")
        self.var_statut.set(f"{total} produit(s) affiché(s) sur {len(self.produits)}.")

        if remonter:
            self.canvas.yview_moveto(0)

        self._telecharger_images_manquantes(morceau)

    def _creer_carte(self, produit, ligne, colonne):
        carte = tk.Frame(self.grille, bg="white", highlightbackground="#d5d9d9",
                         highlightthickness=1, cursor="hand2")
        carte.grid(row=ligne, column=colonne, padx=6, pady=6, sticky="n")

        # Image (zone de taille fixe pour que toutes les cartes soient alignées)
        zone_img = tk.Frame(carte, bg="white", width=TAILLE_IMG, height=TAILLE_IMG)
        zone_img.pack(padx=10, pady=(10, 4))
        zone_img.pack_propagate(False)

        photo = self._photo(produit, (TAILLE_IMG, TAILLE_IMG))
        if photo:
            lbl_img = tk.Label(zone_img, image=photo, bg="white")
        else:
            lbl_img = tk.Label(zone_img, text="Pas d'image", bg="#f0f2f2", fg="#888888")
        lbl_img.pack(expand=True, fill="both" if not photo else None)

        # Titre (4 lignes max)
        lbl_titre = tk.Label(carte, text=raccourcir(produit.titre, 85), bg="white",
                             fg="#0f1111", font=("Segoe UI", 9), wraplength=TAILLE_IMG,
                             justify="left", anchor="nw", height=4)
        lbl_titre.pack(padx=10, anchor="w")

        # Étoiles
        note = note_en_nombre(produit.note)
        lbl_note = tk.Label(carte, text=etoiles(note), bg="white",
                            fg="#ffa41c" if note is not None else "#888888",
                            font=("Segoe UI", 9), anchor="w")
        lbl_note.pack(padx=10, anchor="w")

        # Prix
        if prix_en_nombre(produit.prix) is not None:
            lbl_prix = tk.Label(carte, text=produit.prix, bg="white", fg="#0f1111",
                                font=("Segoe UI", 13, "bold"), anchor="w")
        else:
            lbl_prix = tk.Label(carte, text="Prix non affiché", bg="white", fg="#888888",
                                font=("Segoe UI", 9), anchor="w")
        lbl_prix.pack(padx=10, anchor="w")

        # Catégorie
        lbl_cat = tk.Label(carte, text=produit.categorie, bg="white", fg="#565959",
                           font=("Segoe UI", 8), anchor="w")
        lbl_cat.pack(padx=10, pady=(0, 10), anchor="w")

        # Un clic n'importe où sur la carte ouvre la fiche
        for widget in (carte, zone_img, lbl_img, lbl_titre, lbl_note, lbl_prix, lbl_cat):
            widget.bind("<Button-1>", lambda e, p=produit: self._ouvrir_fiche(p))
            widget.configure(cursor="hand2")

    # ------------------------------------------------------------------
    # Fiche détaillée d'un produit
    # ------------------------------------------------------------------
    def _ouvrir_fiche(self, produit):
        fen = tk.Toplevel(self)
        fen.title(raccourcir(produit.titre, 60))
        fen.geometry("800x500")
        fen.configure(bg="white")
        fen.transient(self)

        # --- Image à gauche ---
        gauche = tk.Frame(fen, bg="white", width=340, height=340)
        gauche.pack(side="left", padx=20, pady=20, anchor="n")
        gauche.pack_propagate(False)

        photo = self._photo(produit, (320, 320))
        if photo:
            lbl = tk.Label(gauche, image=photo, bg="white")
            lbl.image = photo
        else:
            lbl = tk.Label(gauche, text="Pas d'image disponible", bg="#f0f2f2", fg="#888888")
        lbl.pack(expand=True)

        # --- Informations à droite ---
        droite = tk.Frame(fen, bg="white")
        droite.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        tk.Label(droite, text=produit.titre, bg="white", fg="#0f1111",
                 font=("Segoe UI", 13, "bold"), wraplength=380, justify="left",
                 anchor="w").pack(anchor="w")

        note = note_en_nombre(produit.note)
        tk.Label(droite, text=etoiles(note), bg="white",
                 fg="#ffa41c" if note is not None else "#888888",
                 font=("Segoe UI", 12)).pack(anchor="w", pady=(10, 0))

        if prix_en_nombre(produit.prix) is not None:
            tk.Label(droite, text=produit.prix, bg="white", fg="#b12704",
                     font=("Segoe UI", 22)).pack(anchor="w", pady=(10, 10))
        else:
            tk.Label(droite, text="Prix non affiché", bg="white", fg="#888888",
                     font=("Segoe UI", 12)).pack(anchor="w", pady=(10, 10))

        infos = [
            ("Catégorie", produit.categorie),
            ("ASIN", produit.asin),
            ("Trouvé dans", produit.page),
        ]
        for nom, valeur in infos:
            if valeur:
                tk.Label(droite, text=f"{nom} : {valeur}", bg="white", fg="#565959",
                         font=("Segoe UI", 10)).pack(anchor="w")

        boutons = tk.Frame(droite, bg="white")
        boutons.pack(anchor="w", pady=20)
        if produit.asin:
            ttk.Button(boutons, text="Voir sur Amazon",
                       command=lambda: webbrowser.open(f"{config.SITE}/dp/{produit.asin}")
                       ).pack(side="left", padx=(0, 10))
        ttk.Button(boutons, text="Fermer", command=fen.destroy).pack(side="left")