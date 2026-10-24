# Projet-Scraping

Scraper de produits Amazon avec base de données SQLite, mode console, interface graphique, export CSV et téléchargement d'images

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.51-43B02A?logo=selenium&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.15-orange)
![Architecture](https://img.shields.io/badge/Architecture-MVC-blueviolet)
![Statut](https://img.shields.io/badge/Statut-En%20développement-yellow)

## Table des matières

- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Fonctionnement](#fonctionnement)
- [Technologies](#technologies)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Base de données SQLite](#base-de-données-sqlite)
- [Données extraites](#données-extraites)
- [Configuration](#configuration)
- [Évolutions prévues](#évolutions-prévues)
- [Avertissement](#avertissement)
- [Auteure](#auteure)

## À propos

Projet-Scraping collecte automatiquement les informations de produits électroniques listés sur Amazon, les stocke dans une base de données SQLite, puis les exporte au format CSV avec les images des produits.

Neuf catégories sont traitées : laptop, earpods, smartphone, tablette, casque audio, montre connectée, appareil photo, télévision et enceinte bluetooth.

Le projet fonctionne en local : les pages Amazon sont d'abord téléchargées et sauvegardées, puis analysées hors ligne. Cette approche rend l'extraction plus rapide et plus stable, et limite le nombre de requêtes envoyées à Amazon.

## Fonctionnalités

- Téléchargement des pages Amazon avec Selenium
- Extraction des données produits avec BeautifulSoup
- Suppression automatique des doublons (grâce à l'identifiant ASIN)
- Stockage des produits dans une base de données SQLite
- Téléchargement automatique des images produits
- Export des résultats au format CSV
- Deux modes d'utilisation :
  - **Mode console** (par défaut)
  - **Interface graphique Tkinter** (option `--gui`) avec tableau, recherche par titre ou catégorie, barre de progression et export
- Mode hors-ligne (fichiers locaux) ou mode en ligne (Selenium)
- Conservation des anciennes données si un nouveau scraping échoue (captcha, réseau)

## Fonctionnement

```
1. Téléchargement      2. Extraction          3. Stockage        4. Sortie
telecharger_pages.py → app/scraper (HTML)  →  data/produits.db → exports/*.csv
   (Selenium)             (BeautifulSoup)       (SQLite)          data/images/
        ↓
  pages_locales/
```

1. **Téléchargement** : Selenium récupère les pages et les enregistre dans `pages_locales/` (étape facultative, à faire une seule fois).
2. **Extraction** : le scraper lit les fichiers HTML locaux et en extrait les données.
3. **Stockage** : les produits sont enregistrés dans la base SQLite `data/produits.db`.
4. **Sortie** : les données sont affichées (console ou Tkinter), exportées en CSV depuis la base, et les images sont enregistrées.

## Technologies

| Outil | Rôle |
|---|---|
| Python | Langage principal |
| Selenium | Téléchargement des pages |
| BeautifulSoup4 | Analyse du HTML |
| SQLite (module `sqlite3`) | Stockage des données |
| Requests | Téléchargement des images |
| Tkinter | Interface graphique |

## Structure du projet

```
Projet-Scraping/
├── main.py                  # Point d'entrée
├── config.py                # Paramètres
├── telecharger_pages.py     # Téléchargement des pages
├── requirements.txt         # Dépendances
├── app/
│   ├── controllers/
│   │   └── scraping_controller.py   # Logique de contrôle
│   ├── models/
│   │   ├── produit.py               # Modèle Produit
│   │   └── depot.py                 # Accès à la base SQLite
│   ├── scraper/
│   │   ├── amazon_scraper.py        # Orchestration du scraping
│   │   ├── driver.py                # Navigateur Selenium
│   │   └── parsing.py               # Extraction des données (HTML)
│   └── views/
│       ├── console_view.py          # Affichage console
│       ├── export_view.py           # Export CSV et images
│       └── interface_view.py        # Interface Tkinter
├── pages_locales/           # Pages HTML sauvegardées
├── exports/                 # Fichiers CSV générés
└── data/
    ├── produits.db          # Base de données SQLite
    └── images/              # Images des produits
```

Le projet suit l'architecture **MVC** (Modèle - Vue - Contrôleur).

## Installation

**Prérequis :** Python 3.x et Google Chrome (Tkinter est déjà inclus avec Python).

```bash
# 1. Cloner le dépôt
git clone https://github.com/Marie-Stellaa/Projet-Scraping.git
cd Projet-Scraping

# 2. Créer l'environnement virtuel
python -m venv env
env\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

Toutes les commandes se lancent **depuis la racine du projet**.

```bash
# Étape 1 (optionnelle) : télécharger les pages Amazon dans pages_locales/
python telecharger_pages.py

# Étape 2a : lancer l'application en mode console (par défaut)
python main.py

# Étape 2b : lancer l'application avec l'interface graphique
python main.py --gui
```

### Mode console

`python main.py` exécute le déroulement complet : lecture des pages, extraction, enregistrement dans SQLite, affichage de la liste des produits, puis export CSV avec téléchargement des images.

### Interface graphique

`python main.py --gui` ouvre une fenêtre avec :

- une case **Mode hors-ligne** (fichiers locaux) ou en ligne (Selenium)
- **Lancer le scraping** : récupère les produits et les enregistre dans la base
- **Charger depuis la base** : affiche les produits déjà enregistrés
- **Exporter en CSV** : crée le fichier CSV et télécharge les images
- une barre de **recherche** par titre ou par catégorie

> **Durée de l'export :** chaque image est téléchargée une par une (environ 1 seconde chacune). Avec plus d'un millier de produits, l'export peut durer 15 à 25 minutes. Les images déjà téléchargées sont conservées et réutilisées lors des exports suivants.

## Base de données SQLite

Les produits sont stockés dans le fichier `data/produits.db`, dans la table `produit` :

| Colonne | Type | Description |
|---|---|---|
| `id` | INTEGER | Identifiant (clé primaire, auto-incrémenté) |
| `titre` | TEXT | Titre du produit |
| `prix` | TEXT | Prix affiché |
| `note` | TEXT | Note moyenne |
| `categorie` | TEXT | Catégorie recherchée |
| `page` | TEXT | Fichier HTML d'origine |
| `asin` | TEXT | Identifiant Amazon du produit |
| `image_url` | TEXT | Lien de l'image |
| `date_ajout` | TEXT | Date d'enregistrement |

À chaque scraping réussi, la table est remplacée par les nouveaux produits. Si le scraping échoue ou ne renvoie rien, les anciennes données sont conservées.

Pour consulter la base, utilise l'extension VS Code **SQLite Viewer** ou le logiciel gratuit **DB Browser for SQLite**.

## Données extraites

Le fichier CSV (séparateur `;`, encodage UTF-8 avec BOM pour Excel) est généré **à partir de la base SQLite** et contient, pour chaque produit :

| Champ | Description |
|---|---|
| Categorie | Catégorie du produit (laptop, smartphone, etc.) |
| Page | Fichier HTML d'où provient le produit |
| ASIN | Identifiant Amazon du produit |
| Titre | Titre complet du produit sur Amazon |
| Prix | Prix en euros (ou `Prix non affiché` si indisponible) |
| Note | Note moyenne sur 5 (ou `Pas de note` si aucun avis) |
| Image_URL | Lien de l'image du produit sur Amazon |
| Image_Fichier | Nom de l'image enregistrée dans `data/images/` (identifiant Amazon du produit, ex. `B0H2NRBQX5.jpg`) |

Exemple de ligne :

```
laptop;amazon_laptop_page_1.html;B09BFPCDLS;ASUS Vivobook 15 M1502NAQ-BQ047W 15.6-inch FHD (1920 x 1080) 60Hz Pc Portable (processeur AMD Ryzen 5 150, 16GB DDR5, 1TB SSD, GPU AMD Radeon Graphics, Windows 11 Home) – Clavier AZERTY;649,99 €;4,5 sur 5 étoiles;https://m.media-amazon.com/images/I/71p81IUN8IL._AC_UL320_.jpg;B09BFPCDLS.jpg
laptop;amazon_laptop_page_1.html;B0HBWY6K1H;Lenovo IdeaPad Slim 3 | Laptop | R7 | 16Go | 512Go | Chargeur Non Inclus;699,99 €;4,2 sur 5 étoiles;https://m.media-amazon.com/images/I/71AUekHcU-L._AC_UL320_.jpg;B0HBWY6K1H.jpg
laptop;amazon_laptop_page_1.html;B0HFWTZ59X;Lenovo IdeaPad Slim 3 | Laptop | R3 | 8Go | 512GB | Chargeur Non Inclus;499,99 €;4,0 sur 5 étoiles;https://m.media-amazon.com/images/I/71oReI7XzZL._AC_UL320_.jpg;B0HFWTZ59X.jpg
```

## Configuration

Les paramètres se trouvent dans `config.py` :

| Paramètre | Rôle |
|---|---|
| `CATEGORIES` | Liste des catégories à traiter |
| `NB_PAGES` | Nombre de pages récupérées par catégorie |
| `MODE_LOCAL` | `True` : lecture des fichiers de `pages_locales/` ; `False` : scraping en direct avec Selenium |
| `DELAI`, `PAUSE_ENTRE_CATEGORIES`, `TIMEOUT` | Délais pour limiter les requêtes envoyées à Amazon |
| `SELECTEUR_*` | Sélecteurs CSS utilisés pour extraire les données |

> Le dossier `pages_locales/` doit contenir les pages HTML pour que le mode hors-ligne fonctionne. Sans ces fichiers, aucun produit ne sera trouvé.

## Évolutions prévues

- [x] Étendre le scraper à plusieurs catégories d'appareils électroniques (9 catégories)
- [x] Stocker les données dans une base SQLite
- [ ] Ajouter d'autres catégories de produits
- [ ] Convertir le prix en valeur numérique pour permettre le tri et les calculs

## Avertissement

Ce projet est réalisé à des fins pédagogiques. L'utilisation du scraper doit respecter les conditions d'utilisation d'Amazon.

## Auteure

Godé Ayekpa Epiphanie Marie-Stella Rachel
Étudiante en Informatique et Génie Logiciel, Institut Ivoirien de Technologie (IIT)
GitHub : [Marie-Stellaa](https://github.com/Marie-Stellaa)