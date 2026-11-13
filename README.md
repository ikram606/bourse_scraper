# Web Scraper Automatisé de Données Boursières

Pipeline d'extraction automatisée (*Web Scraping*) conçu pour collecter, parser et structurer les données de marché depuis des sources web publiques afin d'alimenter des analyses de données et séries temporelles.

## Objectifs & Fonctionnalités

* **Extraction Web (Scraping) :** Collecte automatisée des cotations, variations et indicateurs clés via requêtes HTTP et parsing HTML.
* **Nettoyage & Structuration :** Conversion des chaînes de caractères brutes en types numériques exploitables, normalisation des dates et suppression des doublons.
* **Export de Données :** Génération de fichiers structurés (CSV / Excel) prêts à être ingérés dans un pipeline analytique ou une base de données.

## Stack Technique

* **Langage :** Python
* **Collecte & Parsing :** Requests, BeautifulSoup4 / Selenium *(ajuste selon les bibliothèques utilisées dans ton script)*
* **Manipulation de données :** Pandas

## Exécution

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'extraction
python main.py
