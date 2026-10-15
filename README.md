# VéloVille — Plateforme de valorisation des données

**Auteur :** Kheira Bekara  
**Version :** 1.0.0 (Release Candidate)  

---

## 1. Présentation du projet

**VéloVille** est une application monolithe modulaire conçue pour collecter, fiabiliser, analyser et valoriser les données issues du réseau de vélos en libre-service (stations, trajets et incidents) de la métropole. 

L'architecture repose sur :
- **FastAPI** pour l'API RESTful haute performance.
- **SQLAlchemy 2.0** (driver `psycopg3`) pour l'ORM et la gestion des sessions PostgreSQL.
- **Pydantic v2** pour la validation des schémas et des paramètres de requêtes.
- **Streamlit** pour l'interface utilisateur décisionnelle et d'exploitation.
- **Pytest & Pytest-Cov** pour les tests automatisés et la mesure de couverture de code.

---

## 2. Architecture du projet

```text
velo-ville/
├── api/                   # Application Back-End FastAPI (routeurs, services, schémas, sécurité)
├── data/                  # Fichiers CSV sources (stations, trajets, incidents)
├── docs/                  # Documentation projet, procédures, rapports et matrice RBAC
│   ├── htmlcov/           # Rapport HTML de couverture de tests
│   └── recette/           # Plan de recette, procès-verbal et fiches d'anomalies (ANO-001 à ANO-004)
├── front/                 # Application Front-End Streamlit (tableau de bord & exploitation)
├── scripts/               # Scripts d'ingestion ETL (importer.py) et utilitaires
├── sql/                   # Scripts DDL (schema.sql) et d'initialisation des comptes (comptes.sql)
├── tests/                 # Suite de tests unitaires et d'intégration (pytest)
├── .env.example           # Modèle de configuration des variables d'environnement
├── README.md              # Documentation principale du projet
└── requirements.txt       # Dépendances Python du projet
```

---

## 3. Prérequis techniques

- **Python** 3.10 ou supérieur
- **PostgreSQL** 14 ou supérieur (avec pgAdmin / Query Tool)
- **Git**

---

## 4. Installation et configuration

### 1. Initialisation du projet et environnement virtuel

```bash
# Cloner / Se placer à la racine du projet
cd velo-ville

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Sur Windows (PowerShell) :
.\.venv\Scripts\activate
# Sur Linux / macOS :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration de la base de données PostgreSQL

1. Ouvrir **pgAdmin** et créer manuellement les deux bases de données :
   - `veloville` (base d'exploitation)
   - `veloville_test` (base dédiée aux tests automatisés)
2. Ouvrir le **Query Tool** sur la base `veloville` :
   - Exécuter le script `sql/schema.sql` pour créer les tables.
   - Exécuter le script `sql/comptes.sql` pour créer les comptes utilisateurs (`exploitant01` et `direction01`).

### 3. Variables d'environnement (`.env`)

Créer un fichier `.env` à la racine du projet à partir de `.env.example` :

```env
# Connexion PostgreSQL
DATABASE_URL=postgresql+psycopg://postgres:votre_mot_de_passe@localhost:5432/veloville
DATABASE_URL_TEST=postgresql+psycopg://postgres:votre_mot_de_passe@localhost:5432/veloville_test

# Sécurité & Authentification JWT
JWT_SECRET=8175b05529911016af748d50e1369ac07bd4678160a9d7e3f3b390431c6c6ace
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Configuration Front-End Streamlit
API_URL=http://localhost:8000
API_TIMEOUT_SECONDES=5
```

---

## 5. Ingestion et fiabilisation des données (ETL)

L'alimentation de la base de données s'effectue via le script ETL d'importation idempotent :

```bash
$env:PYTHONPATH="." ; python scripts/importer.py
```

**Bilan d'exécution sur le jeu de données d'origine :**
- **2 330** lignes brutes lues.
- **2 295** enregistrements valides insérés en base (`120` stations, `1998` trajets, `177` incidents).
- **35** rejets isolés et journalisés (`docs/journal-rejets.csv`).
- **124** avertissements de normalisation enregistrés (`docs/journal-avertissements.csv`).

---

## 6. Démarrage des services

1. **Lancer l'API FastAPI (Back-End) :**
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```
   *Documentation interactive OpenAPI / Swagger disponible sur :* `http://127.0.0.1:8000/docs`

2. **Lancer l'interface Streamlit (Front-End) :**
   ```bash
   streamlit run front/app.py
   ```
   *Application accessible sur :* `http://localhost:8501`

**Comptes de démonstration :**
- **Exploitant :** `exploitant01` / `Formation2026!` (Gestion complète + mise à jour des incidents)
- **Direction :** `direction01` / `Formation2026!` (Consultation globale & indicateurs décisionnels)

---

## 7. Tests & Couverture de code

Les tests unitaires et d'intégration sont regroupés sous le dossier `tests/`.

### Lancer la suite de tests et générer le rapport de couverture :

```bash
pytest --cov=api/services --cov=api/routers --cov-report=term-missing --cov-report=html:docs/htmlcov
```

- **Rapport HTML :** Le rapport interactif est généré directement dans `docs/htmlcov/index.html`.
- **Pour l'ouvrir dans le navigateur (Windows) :**
  ```powershell
  Start-Process docs/htmlcov/index.html
  ```

---

## 8. Bilan de la recette & État des anomalies

La campagne de recette du 12 octobre 2026 a porté sur l'exécution des cas **REC-01 à REC-10**.

- **Décision :** **Recette PRONONCÉE AVEC RÉSERVES**
- **Synthèse :**
  - **`ANO-001` (Corrigée) :** Vidage/nettoyage du champ `date_resolution` dans le routeur pour les incidents non résolus.
  - **`ANO-002` (Corrigée) :** Prise en compte des dates par défaut dans la fonction `get_activite_par_jour`.
  - **`ANO-003` (Reportée V1.1) :** Amélioration des messages d'aide à la saisie sur la pagination IHM.
  - **`ANO-004` (Reportée V1.1) :** Précision des retours d'erreurs HTTP et masquage des boutons d'édition pour le rôle Direction.

*Les détails complets sont consultables dans `docs/recette/resultats-recette.md` et dans le dossier `docs/recette/anomalies/`.*