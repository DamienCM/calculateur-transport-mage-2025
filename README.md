# Calculateur de Frais de Livraison

## Description
Cette application Python permet de calculer les frais de livraison d'un panier client en fonction de plusieurs transporteurs (DPD, Schenker Palette, Schenker Messagerie). Les grilles tarifaires des transporteurs sont stockées dans des fichiers CSV sous le répertoire `data`.

## Structure du Projet
- `data/`: Contient les fichiers CSV avec les grilles tarifaires des transporteurs.
- `src/`: Contient le code source de l'application.
  - `__main__.py`: Script principal pour exécuter l'application.
  - `utils.py`: Contient les utilitaires pour calculer les frais de livraison.
  - `charger_tarifs.py`: Contient le code pour charger les tarifs des transporteurs.

## Utilisation
1. Placez les fichiers CSV des transporteurs dans le répertoire `data`.
2. Exécutez le script `__main__.py` pour calculer les frais de livraison.

## Exemple
```bash
python src/__main__.py
```

## Auteurs
- Votre Nom