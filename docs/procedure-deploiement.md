# Procédure de déploiement — VéloVille V1.0

Ce document décrit les instructions nécessaires pour déployer l'application VéloVille sur un nouvel environnement, de la configuration de la base de données jusqu'au lancement des services, incluant la documentation technique et les rapports de tests.

## 1. Prérequis techniques

- **Python** 3.10 ou supérieur
- **PostgreSQL** 14 ou supérieur (avec pgAdmin / Query Tool)
- **Git**

## 2. Configuration de la base de données PostgreSQL

*Via l'interface pgAdmin ou le Query Tool :*

1. **Création des bases de données :**
   - Créer la base de données principale `veloville`.
   - Créer la base de données de test `veloville_test` (dédiée aux tests automatisés).

2. **Exécution des scripts de schéma et de comptes :**
   - Ouvrir le **Query Tool** sur la base `veloville`.
   - Charger et exécuter le fichier `sql/schema.sql` pour créer les tables.
   - Charger et exécuter le fichier `sql/comptes.sql` pour insérer les comptes utilisateurs initiaux (`exploitant01` et `direction01`).

## 3. Configuration de l'environnement applicatif

### A. Initialisation et récupération du projet

Initialisez le dépôt Git local et associez-le au dépôt distant GitHub :

```bash
cd velo-ville
git init -b main
git remote add origin <URL_DU_DEPOT_GITHUB>
```

### B. Environnement virtuel et dépendances

Créez l'environnement virtuel unique et installez les paquets requis :

```bash
python -m venv .venv
```

- **Activation de l'environnement :**
  - Sous Windows (PowerShell) :
    ```bash
    .\.venv\Scripts\activate
    ```

- **Installation des dépendances :**
  ```bash
  pip install -r requirements.txt
  ```

### C. Variables d'environnement

Copiez le fichier d'exemple `.env.example` vers un nouveau fichier `.env` à la racine, puis renseignez les paramètres de connexion PostgreSQL et de sécurité JWT :

```env
# Base de données PostgreSQL (psycopg3)
DATABASE_URL=postgresql+psycopg://postgres:votre_mot_de_passe@localhost:5432/veloville
DATABASE_URL_TEST=postgresql+psycopg://postgres:votre_mot_de_passe@localhost:5432/veloville_test

# Sécurité JWT
JWT_SECRET=8175b05529911016af748d50e1369ac07bd4678160a9d7e3f3b390431c6c6ace
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Client Front-End Streamlit
API_URL=http://localhost:8000
API_TIMEOUT_SECONDES=5
```

> **Note technique (Connexion BDD) :**  
> La connexion est gérée dynamiquement par SQLAlchemy via les variables chargées dans `api/config.py` et la session initialisée dans `api/database.py`.

## 4. Nettoyage et import des données

Pour exécuter les scripts de test de fiabilisation ou d'importation des données en configurant le chemin racine (PowerShell) :

```powershell
\$env:PYTHONPATH="."; python tests/unit/test_fiabilisation.py
\$env:PYTHONPATH="."; python scripts/importer.py
```

## 5. Lancement de l'API et du Front-End

1. **Lancer l'API (FastAPI via Uvicorn) :**
   ```bash
   uvicorn api.main:app --reload
   ```

2. **Lancer l'interface utilisateur (Streamlit) :**
   Dans un second terminal actif (avec l'environnement virtuel activé) :
   ```bash
   streamlit run front/app.py
   ```


## 6. Rapports de tests et validation

### REC-05 — Route protégée sans jeton

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-05 — Route protégée sans jeton |
| **Date et heure du test** | 12/10/2026 à 10:15 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Étapes 1 et 2 : 401. Étape 3 : 200 `{"statut": "ok"}`. |
| **Résultat obtenu** | Code HTTP 401 renvoyé sur `/stations` sans en-tête `Authorization` et avec un jeton invalide. Code HTTP 200 `{"statut": "ok"}` renvoyé sur `/sante`. |
| **Anomalie** | Aucune |

#### Preuve d'exécution

**Étape 1 : Appel à `GET /stations` sans en-tête `Authorization`**

```bash
curl -i -X 'GET' 'http://127.0.0.1:8000/stations'
```

**Réponse :**
```http
HTTP/1.1 401 Unauthorized
content-type: application/json

{"detail":"Not authenticated"}
```

**Étape 2 : Appel à `GET /stations` avec un jeton invalide (`Authorization: Bearer jeton.invalide.xyz`)**

```bash
curl -i -X 'GET' 'http://127.0.0.1:8000/stations' \
  -H 'Authorization: Bearer jeton.invalide.xyz'
```

**Réponse :**
```http
HTTP/1.1 401 Unauthorized
content-type: application/json

{"detail":"Could not validate credentials"}
```

**Étape 3 : Appel à `GET /sante` sans en-tête**

```bash
curl -i -X 'GET' 'http://127.0.0.1:8000/sante'
```

**Réponse :**
```http
HTTP/1.1 200 OK
content-type: application/json

{"statut":"ok"}
```

## 8. Vérifications après déploiement

- Valider le bon fonctionnement de l'API via l'endpoint de santé : `GET /sante`
- S'assurer de la bonne exécution des tests unitaires de validation :
  ```bash
  pytest
  ```

## Auteur et Version

- **Auteur :** Bekara Kheira
- **Version :** 1.0.0