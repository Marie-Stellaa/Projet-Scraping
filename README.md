<div align="center">

# Projet-Scraping

**Scraper de produits Amazon avec interface graphique, export CSV et téléchargement d'images**

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.51-43B02A?logo=selenium&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.15-orange)
![Architecture](https://img.shields.io/badge/Architecture-MVC-blueviolet)
![Statut](https://img.shields.io/badge/Statut-En%20développement-yellow)

</div>

---

## Table des matières

- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Fonctionnement](#fonctionnement)
- [Technologies](#technologies)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Données extraites](#données-extraites)
- [Évolutions prévues](#évolutions-prévues)
- [Avertissement](#avertissement)
- [Auteure](#auteure)

---

## À propos

**Projet-Scraping** collecte automatiquement les informations des ordinateurs portables listés sur Amazon, les organise, puis les exporte au format CSV avec les images des produits.

Le projet fonctionne en local : les pages Amazon sont d'abord téléchargées et sauvegardées, puis analysées hors ligne. Cette approche rend l'extraction plus rapide et plus stable, et limite le nombre de requêtes envoyées à Amazon.

## Fonctionnalités

- Téléchargement des pages Amazon avec Selenium
- Extraction des données produits avec BeautifulSoup
- Téléchargement automatique des images produits
- Export des résultats au format CSV
- Trois modes d'utilisation : console, interface graphique Tkinter et export

## Fonctionnement

```
1. Téléchargement      2. Extraction           3. Sortie
telecharger_pages.py → app/scraper (HTML)  →  exports/*.csv
   (Selenium)             (BeautifulSoup)      data/images/
        ↓
  pages_locales/
```

1. **Téléchargement** : Selenium récupère les pages et les enregistre dans `pages_locales/`.
2. **Extraction** : le scraper lit les fichiers HTML locaux et en extrait les données.
3. **Sortie** : les données sont affichées (console ou Tkinter), exportées en CSV, et les images sont enregistrées.

## Technologies

| Outil | Rôle |
|-------|------|
| Python | Langage principal |
| Selenium | Téléchargement des pages |
| BeautifulSoup4 | Analyse du HTML |
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
│   ├── controllers/         # Logique de contrôle
│   ├── models/              # Modèles de données
│   ├── scraper/             # Extraction des données
│   └── views/
│       ├── console_view.py      # Affichage console
│       ├── export_view.py       # Export CSV
│       └── interface_view.py    # Interface Tkinter
├── pages_locales/           # Pages HTML sauvegardées
├── exports/                 # Fichiers CSV générés
└── data/images/             # Images des produits
```

## Installation

**Prérequis** : Python 3.x et Google Chrome.

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

```bash
# Étape 1 (optionnelle) : télécharger les pages Amazon
python telecharger_pages.py

# Étape 2 : lancer l'application
python main.py
```

## Données extraites

Le fichier CSV (séparateur `;`) contient, pour chaque produit :

| Champ | Description |
|-------|-------------|
| Nom | Titre complet du produit sur Amazon |
| Prix | Prix en euros (ou `Prix non affiché` si indisponible) |
| Note | Note moyenne sur 5 (ou `Pas de note` si aucun avis) |
| URL de l'image | Lien de l'image du produit sur Amazon |
| Fichier image | Nom de l'image enregistrée dans `data/images/` (identifiant Amazon du produit, ex. `B0H2NRBQX5.jpg`) |

**Exemple de ligne :**

```
Lenovo Legion 5 | Gaming Laptop | i7 | NVIDIA RTX 5070 | 16Go | 512Go SSD;2 099,99 €;Pas de note;https://m.media-amazon.com/images/I/610PGV4S23L._AC_UL320_.jpg;B0HC4BYXT2.jpg
```

## Évolutions prévues

- [ ] Étendre le scraper à tous les appareils électroniques d'Amazon

## Avertissement

Ce projet est réalisé à des fins pédagogiques. L'utilisation du scraper doit respecter les conditions d'utilisation d'Amazon.

## Auteure

**Godé Epiphanie (Marie-Stella)**
Étudiante en Informatique et Génie Logiciel, Institut Ivoirien de Technologie (IIT)
GitHub : [Marie-Stellaa](https://github.com/Marie-Stellaa)