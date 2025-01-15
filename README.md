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
  -`bin/` Contient des fichiers plus ou moisn relies a des bianires executables
    - `c.py`: Interface pour les optimisations en C.
    - `partition_optimizer.c`: Code C pour l'optimisation des partitions.
    - `libpartition_optimizer.so`: Code compile pour l'optimisation des partitions.
  -`config/`
    -`logger_setup.py`: Fichier config pou log dans le terminal et dans un fichier avec des niveaux de logs
  -`ui/` Contient les elemetns d'interface graphique
    - `ui.py`: Interface utilisateur en Tkinter. OUTDATED
    - `ui_qt.py`: Interface utilisateur en PyQt5.
    - `article_entry.py`: Widget ligne d'article en PyQt5.
    - `loading_overlay.py`: Overlay pour le chargement en PyQt5.
    - `loading_spinner.py`: Animated spinner utiliable pour le chargement en PyQt5.
    - `styles.py`: Styles par default utilise dans l'application en PyQt5.
  -`models/` Contient des modeles genereiques pour notre application
    -`calculation_errors.py` : custom error type
    -`culculation_thread.py` : to run calculation on an other thread than ui
    -`transporteurs.py` : Transporteurs logic and calculations
  -`utils/` Contient es utilitaire pour notre application
    -`utils.py` : Contient des fonctions utiles generiques
  - `__main__.py`: Script principal pour exécuter l'application.
  - `__init__.py`: Pour considerer l'ensemble comme package.
  - `calculateur.py`: Contient la logique de calcul des frais de livraison.
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