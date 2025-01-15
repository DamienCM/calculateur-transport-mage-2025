# Calculateur de Frais de Livraison

## Description
Cette application Python permet de calculer les frais de livraison d'un panier client en fonction de plusieurs transporteurs (DPD, Schenker Palette, Schenker Messagerie). Les grilles tarifaires des transporteurs sont stockées dans des fichiers CSV sous le répertoire `data`.

## Structure du Projet
- `data/`: Contient les fichiers CSV avec les grilles tarifaires des transporteurs.
  - `country_list.csv`: Liste des pays.
  - `country_supported.csv`: Liste des pays supportés par chaque transporteur.
  - `dpd.csv`: Grille tarifaire pour DPD.
  - `items.csv`: Liste des articles avec leurs poids.
  - `schenker_messagerie.csv`: Grille tarifaire pour Schenker Messagerie.
  - `schenker_palette.csv`: Grille tarifaire pour Schenker Palette.
- `src/`: Contient le code source de l'application.
  - `__main__.py`: Script principal pour exécuter l'application.
  - `calculateur.py`: Contient la logique de calcul des frais de livraison.
  - `c.py`: Interface pour les optimisations en C.
  - `ui.py`: Interface utilisateur en Tkinter.
  - `ui_qt.py`: Interface utilisateur en PyQt5.
  - `utils.py`: Contient les utilitaires pour calculer les frais de livraison.
  - `partition_optimizer.c`: Code C pour l'optimisation des partitions.
  - `logger_setup.py`: Configuration du logger.
- `build/`: Contient les fichiers de build.
  - `Calculateur Transports/`: Dossier de build.
- `icons/`: Contient les icônes de l'application.
- `installation_package/`: Contient le package d'installation.
  - `Calculateur Transports/`: Dossier de l'application.
  - `README.txt`: Instructions d'installation.
- `logs/`: Contient les fichiers de log.
- `.vscode/`: Configuration de l'éditeur Visual Studio Code.
  - `launch.json`: Configuration de lancement.
- `build_app.py`: Script pour builder l'application.
- `Calculateur Transports.spec`: Fichier de spécification pour PyInstaller.
- `LICENSE`: Licence du projet.
- `README.md`: Ce fichier.

## Dépendances
- Python 3.x
- numpy
- pandas
- PyQt5
- tkinter

## Installation
1. Clonez le dépôt:
    ```bash
    git clone <url-du-dépôt>
    cd CALCULATEUR-TRANSPORT-MAGE-2025
    ```
2. Installez les dépendances:
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation
1. Placez les fichiers CSV des transporteurs dans le répertoire [data](http://_vscodecontentref_/1).
2. Exécutez le script [__main__.py](http://_vscodecontentref_/2) pour calculer les frais de livraison:
    ```bash
    python src/__main__.py
    ```

## Exemple
```bash
python src/__main__.py
```

## Auteurs
- DCM