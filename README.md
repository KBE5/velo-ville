# VéloVille — Plateforme de valorisation des données

Auteur : Kheira Bekara

Version : 0.1.0

Présentation du projet
VéloVille est une application monolithe modulaire conçue pour collecter, fiabiliser, analyser et valoriser les données liées au réseau de vélos en libre-service (stations, trajets et incidents). Le projet adopte une approche rigoureuse basée sur la modularité et les tests unitaires (TDD).

## Prérequis
* **Python** (version 3.10 ou supérieure recommandée)
* **Git**

## Installation et environnement de travail

1. **Cloner le dépôt et se placer à la racine du projet :**
   ```bash
   cd velo-ville
   ```
2.  **Créer l'environnement virtuel: ** 
    ```bash
    cd velo-ville
    ```
3.  **Activer l'environnement virtuel : ** 
    ```bash
    .\.venv\Scripts\activate
    ```
4.  **Installer les dépendances du projet : ** 
    ```bash
    pip install -r requirements.txt
    ```
3.  **Exécution des tests : ** 
    ```bash
    pytest
    ```

## Tests & Qualité

La fiabilité des règles de gestion métiers (RG1 à RG8) est garantie par une suite de tests unitaires développée avec `pytest`.

### Exécution des tests

Pour lancer l'ensemble des tests unitaires du module de fiabilisation :

```powershell
pytest tests/unit/
```