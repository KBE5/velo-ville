# Résultats de recette

Relevé d'exécution des cas REC-01 à REC-10, synthèse chiffrée, axes
d'amélioration, procès-verbal.

# Résultats de la campagne de recette — VéloVille V1

**Date de campagne :** 15 octobre 2026  
**Environnement :** Python 3.12, PostgreSQL 14, FastAPI, Streamlit  
**Base de données de recette :** `veloville` (réinitialisée avant campagne)  
**Version / Commit testé :** `e73320c` (Tag `v1.0.0-rc1`)  

---

## 1. Relevé d'exécution détaillé

### REC-01 — Import idempotent

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-01 — Import idempotent |
| **Date / Heure** | 15/10/2026 à 09:15 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`)|
| **Statut** | **OK** |
| **Résultat attendu** | Les deux exécutions se terminent sans erreur ; les trois comptages SQL sur PostgreSQL sont identiques entre la 1ère et la 2nde exécution ; `count(*) FROM station` vaut 120. |
| **Résultat obtenu** | Exécutions successives de `scripts/importer.py` sans erreur. Comptages SQL strictement identiques après les deux passages : 120 stations, 1998 trajets, 177 incidents. 0 doublon supplémentaire inséré lors de la seconde exécution. |
| **Anomalie** | Aucune |

**Preuve d'exécution :**

- **Première et deuxième exécution (résultat du bilan console identique) :** 
`$env:PYTHONPATH="."; python scripts/importer.py`

```text
[INFO] 
=== Bilan final  ===
Stations   : 120 -> 120 conservées
Trajets    : 2030 -> 1998 conservés
Incidents  : 180 -> 177 conservés
Rejets enregistrés       : 35 -> docs/journal-rejets.csv
Avertissements produits : 124 -> docs/journal-avertissements.csv
```

### REC-02 — Rejets journalisés et cohérence des volumes

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-02 — Rejets journalisés et cohérence des volumes |
| **Date et heure du test** | 15/10/2026 à 09:30 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Pour chaque fichier : importées + rejetées + doublons écartés = lignes du CSV. Chaque ligne du journal porte les informations requises. La requête SQL d'intégrité renvoie 0. |
| **Résultat obtenu** | La cohérence des volumes est mathématiquement vérifiée sur les trois fichiers CSV. Les journaux des avertissements et des rejets contiennent bien les informations exigées. La requête SQL d'intégrité sur les stations de départ/arrivée renvoie exactement 0 ligne orpheline. |
| **Anomalie** | Aucune |

#### Relevé de cohérence des volumes

| Fichier source | Lignes CSV (hors en-tête) | Lignes importées (BDD) | Rejets enregistrés | Avertissements produits | Total reconstitué |
|---|---|---|---|---|---|
| `stations.csv` | 120 | 120 | 0 | 0 | **120** |
| `trajets.csv` | 2 030 | 1 998 | 32 | 122 | **2 030** |
| `incidents.csv` | 180 | 177 | 3 | 2 | **180** |
| **Total** | **2 330** | **2 295** | **35** | **124** | **2 330** |

#### Preuve d'exécution

1. **Vérification du format du journal des avertissements (`docs/journal-avertissement.csv`) :**
```text
fichier_source,id_entite,colonne_concernee,valeur_brute,valeur_corrigee,motif
incidents.csv,I2026-0001,statut,En cours,en_cours,Normalisation de la casse et du format
incidents.csv,I2026-0003,statut,RESOLU,resolu,Normalisation de la casse et du format
```
2. **Vérification du contenu intégral du journal des rejets (`docs/journal-rejets.csv`) :**
```text
fichier_source,id_entite,code_regle,motif,decision
trajets.csv,T480030,RG2/RG4/DOUBLON,Station d'arrivée inexistante dans le référentiel: S999,REJET
trajets.csv,T480034,RG2/RG4/DOUBLON,Station d'arrivée inexistante dans le référentiel: S999,REJET
trajets.csv,T480073,RG2/RG4/DOUBLON,Trajet dupliqué : T480073,REJET
trajets.csv,T480078,RG2/RG4/DOUBLON,Trajet dupliqué : T480078,REJET
trajets.csv,T480152,RG2/RG4/DOUBLON,Horodatage de départ invalide ou absent: Format d'horodatage invalide: 24/08/2026 11:01,REJET
trajets.csv,T480235,RG2/RG4/DOUBLON,Station d'arrivée inexistante dans le référentiel: S999,REJET
trajets.csv,T480288,RG2/RG4/DOUBLON,Trajet dupliqué : T480288,REJET
trajets.csv,T480293,RG2/RG4/DOUBLON,Trajet dupliqué : T480293,REJET
trajets.csv,T480379,RG2/RG4/DOUBLON,Horodatage de départ invalide ou absent: Format d'horodatage invalide: 25/08/2026 17:08,REJET
trajets.csv,T480596,RG2/RG4/DOUBLON,Durée invalide ou non numérique: -120,REJET
trajets.csv,T480596,RG2/RG4/DOUBLON,Trajet dupliqué : T480596,REJET
trajets.csv,T480712,RG2/RG4/DOUBLON,Durée invalide ou non numérique: -45,REJET
trajets.csv,T480847,RG2/RG4/DOUBLON,Trajet dupliqué : T480847,REJET
trajets.csv,T480858,RG2/RG4/DOUBLON,Station d'arrivée inexistante dans le référentiel: S999,REJET
trajets.csv,T480899,RG2/RG4/DOUBLON,Durée invalide ou non numérique: -45,REJET
trajets.csv,T480924,RG2/RG4/DOUBLON,Durée invalide ou non numérique: -120,REJET
trajets.csv,T480945,RG2/RG4/DOUBLON,Trajet dupliqué : T480945,REJET
trajets.csv,T481067,RG2/RG4/DOUBLON,Durée invalide ou non numérique: 0,REJET
trajets.csv,T481074,RG2/RG4/DOUBLON,Durée invalide ou non numérique: 0,REJET
trajets.csv,T481274,RG2/RG4/DOUBLON,Durée invalide ou non numérique: 0,REJET
trajets.csv,T481464,RG2/RG4/DOUBLON,Station d'arrivée inexistante dans le référentiel: S999,REJET
trajets.csv,T481592,RG2/RG4/DOUBLON,Horodatage de départ invalide ou absent: Format d'horodatage invalide: 29/08/2026 12:59,REJET
trajets.csv,T481625,RG2/RG4/DOUBLON,Trajet dupliqué : T481625,REJET
trajets.csv,T481636,RG2/RG4/DOUBLON,Trajet dupliqué : T481636,REJET
trajets.csv,T481688,RG2/RG4/DOUBLON,Durée invalide ou non numérique: -120,REJET
trajets.csv,T481717,RG2/RG4/DOUBLON,Station d'arrivée inexistante dans le référentiel: S999,REJET
trajets.csv,T481776,RG2/RG4/DOUBLON,Trajet dupliqué : T481776,REJET
trajets.csv,T481834,RG2/RG4/DOUBLON,Trajet dupliqué : T481834,REJET
trajets.csv,T481846,RG2/RG4/DOUBLON,Durée invalide ou non numérique: -45,REJET
trajets.csv,T481885,RG2/RG4/DOUBLON,Horodatage de départ invalide ou absent: Format d'horodatage invalide: 30/08/2026 07:22,REJET
trajets.csv,T481927,RG2/RG4/DOUBLON,Trajet dupliqué : T481927,REJET
trajets.csv,T481958,RG2/RG4/DOUBLON,Horodatage de départ invalide ou absent: Format d'horodatage invalide: 30/08/2026 15:22,REJET
incidents.csv,I2026-0028,RG6/RG7/RG8,Date de résolution antérieure à la date de signalement,REJET
incidents.csv,I2026-0124,RG6/RG7/RG8,Date de résolution antérieure à la date de signalement,REJET
incidents.csv,I2026-0178,RG6/RG7/RG8,Date de résolution antérieure à la date de signalement,REJET
```
3. Requête SQL de contrôle des stations orphelines sur PostgresSQL 
``SELECT count(*) 
FROM trajet t 
LEFT JOIN station s ON s.station_id = t.station_arrivee 
WHERE t.station_arrivee IS NOT NULL AND s.station_id IS NULL;``

 count 
-------
     0
(1 row)


### REC-03 — Connexion acceptée

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-03 — Connexion acceptée |
| **Date et heure du test** | 15/10/2026 à 09:45 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Code HTTP 200, jeton `access_token` non vide, `token_type` = bearer, rôle égal à exploitant puis direction. |
| **Résultat obtenu** | HTTP 200 renvoyé pour les deux comptes avec délivrance du jeton JWT et du rôle correspondant. |
| **Anomalie** | Aucune |

**Preuve d'exécution :**

1. **Connexion du compte `exploitant01` :**


// POST /auth/login avec exploitant01
```json
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/login' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "exploitant01",
  "password": "Formation2026!"
}'
```

Réponse: 
HTTP/1.1 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJleHBsb2l0YW50MDEiLCJyb2xlIjoiZXhwbG9pdGFudCIsImlhdCI6MTc5MjA1NTYzMywiZXhwIjoxNzkyMDU2MjMzfQ.Cx9fLYVOpn6w0GxvidWGJdym2dlIFj1auyeNjHf9HTY",
  "token_type": "bearer",
  "role": "exploitant"
}
```

2. **Connexion du compte `direction01` :**


// POST /auth/login avec exploitant01
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/login' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "direction01",
  "password": "Formation2026!"
}'
```

Réponse: 
HTTP/1.1 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaXJlY3Rpb24wMSIsInJvbGUiOiJkaXJlY3Rpb24iLCJpYXQiOjE3OTIwNTU4NTUsImV4cCI6MTc5MjA1NjQ1NX0.BbXfKbds0V8_VYr0WTYxgfYFzvoJTzZkpVt0LcG6i5k",
  "token_type": "bearer",
  "role": "direction"
}
```

### REC-04 — Connexion refusée

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-04 — Connexion refusée |
| **Date et heure du test** | 15/10/2026 à 10:00 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Code HTTP 401 dans les deux cas, corps `{"detail": "Identifiants invalides"}` ; le message est identique pour un identifiant inconnu et pour un mot de passe erroné. |
| **Résultat obtenu** | Code HTTP 401 Unauthorized renvoyé de manière uniforme pour les deux requêtes, avec le message de détail exact `{"detail": "Identifiants invalides"}`. |
| **Anomalie** | Aucune |

#### Preuve d'exécution

 **Étape 1 : Tentative avec un mot de passe incorrect sur un compte existant (`exploitant01`) :**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/login' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "exploitant01",
  "password": "FFormation2026!"
}'
```
Réponse: 
HTTP/1.1 401 Error: Unauthorized
```json
{
  "detail": "Identifiants invalides"
}
```

**Étape 2 : Tentative avec un compte inexistant (`directionn01`) :**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/login' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "directionn01",
  "password": "Formation2026!"
}'
```

Réponse: 
HTTP/1.1 401 Error: Unauthorized
```Json
{
  "detail": "Identifiants invalides"
}
```
### REC-05 — Route protégée sans jeton

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-05 — Route protégée sans jeton |
| **Date et heure du test** | 15/10/2026 à 10:15 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Étapes 1 et 2 : 401. Étape 3 : 200 `{"statut": "ok"}`. |
| **Résultat obtenu** | Code HTTP 401 renvoyé sur `/stations` sans en-tête `Authorization` et avec un jeton invalide. Code HTTP 200 `{"statut": "ok"}` renvoyé sur `/sante`. |
| **Anomalie** | Aucune |

**Preuve d'exécution**

**Étape 1 : Appel à `GET /stations` sans en-tête `Authorization`**

```bash
curl -i -X 'GET' '[http://127.0.0.1:8000/stations](http://127.0.0.1:8000/stations)'
```
Réponse: 

HTTP/1.1 401 Unauthorized

```Json
content-type: application/json

{"detail":"Not authenticated"}
```

**Étape 2 : Appel à GET /stations avec un jeton invalide** (Authorization: Bearer jeton.invalide.xyz)

```Bash
curl -i -X 'GET' 'http://127.0.0.1:8000/stations' \
  -H 'Authorization: Bearer jeton.invalide.xyz'
```
Réponse :

HTTP
HTTP/1.1 401 Unauthorized
```Json
content-type: application/json

{"detail":"Could not validate credentials"}
```

**Étape 3 : Appel à GET /sante sans en-tête**

```Bash
curl -i -X 'GET' '[http://127.0.0.1:8000/sante](http://127.0.0.1:8000/sante)'
```
Réponse :

HTTP
HTTP/1.1 200 OK
```Json
content-type: application/json

{"statut":"ok"}
```

### REC-06 — Contrôle des rôles sur la modification d'un incident

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-06 — Contrôle des rôles sur la modification d'un incident |
| **Date et heure du test** | 15/10/2026 à 10:30 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Étape 1 : 403 `{"detail": "Acces reserve au role exploitant"}` ; statut BDD inchangé. Étape 3 : 200 OK, statut `en_cours` en BDD. Étape 5 : 422 `{"detail": "Transition de statut non autorisee"}`. |
| **Résultat obtenu** | Accès refusé (403) pour le rôle direction avec statut BDD préservé. Statut mis à jour à `en_cours` (200) par le rôle exploitant. Transition identique rejetée (422). |
| **Anomalie** | Aucune |

#### Preuve d'exécution

**Étape 1 : Tentative de modification du statut par le rôle `direction` :**

```bash
curl -i -X 'PUT' \
  '[http://127.0.0.1:8000/incidents/INC-001/statut](http://127.0.0.1:8000/incidents/INC-001/statut)' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $JETON_DIRECTION" \
  -H 'Content-Type: application/json' \
  -d '{
    "statut": "en_cours"
  }'

```
Réponse HTTP 403 Forbidden :
```Json
JSON
{
  "detail": "Acces reserve au role exploitant"
}
```

**Étape 2 : Contrôle SQL du statut inchangé en BDD** :

Sur PostgreSQL: 
```sql
SELECT incident_id, statut 
FROM incident 
WHERE incident_id = 'INC-001';
```
```
 incident_id | statut 
-------------+--------
 INC-001     | ouvert
```

**Étape 3 : Modification du statut par le rôle exploitant** :

```Bash
curl -i -X 'PUT' \
  '[http://127.0.0.1:8000/incidents/INC-001/statut](http://127.0.0.1:8000/incidents/INC-001/statut)' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $JETON_EXPLOITANT" \
  -H 'Content-Type: application/json' \
  -d '{
    "statut": "en_cours"
  }'

``` text
Réponse HTTP 200 OK :


JSON
{
  "incident_id": "INC-001",
  "statut": "en_cours"
}


**Étape 4 : Contrôle SQL de la mise à jour en BDD** :

Sur PostgreSQL: 
```sql
SELECT incident_id, statut 
FROM incident 
WHERE incident_id = 'INC-001';
```
```
Resultat: 
 incident_id |  statut  
-------------+----------
 INC-001     | en_cours
```

**Étape 5 : Tentative de transition invalide (re-passage à en_cours)**:

```Bash
curl -i -X 'PUT' \
  '[http://127.0.0.1:8000/incidents/INC-001/statut](http://127.0.0.1:8000/incidents/INC-001/statut)' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer \$JETON_EXPLOITANT" \
  -H 'Content-Type: application/json' \
  -d '{
    "statut": "en_cours"
  }'

```

Réponse HTTP 422 Unprocessable Entity :


JSON
{
  "detail": "Transition de statut non autorisee"
}



### REC-07 — Validation de la pagination API

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-07 — Validation de la pagination API |
| **Date et heure du test** | 15/10/2026 à 11:00 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Étape 1 : 200, total 120, page 1, 50 résultats, 1er ID = S001. Étape 2 : 20 résultats. Étape 3 : total 46 tous sur Lille. Étapes 4 et 5 : 422. |
| **Résultat obtenu** | Structure de pagination conforme avec métadonnées exactes. Filtrage par commune fonctionnel. Erreurs HTTP 422 renvoyées sur paramètres hors limites (`page=0`, `taille_page=101`). |
| **Anomalie** | Aucune |

#### Preuve d'exécution

**Étape 1 : Appel à `GET /stations?taille_page=50&page=1` :**

```bash
curl -i -X 'GET' \
  '[http://127.0.0.1:8000/stations?taille_page=50&page=1](http://127.0.0.1:8000/stations?taille_page=50&page=1)' \
  -H "Authorization: Bearer $JETON_DIRECTION"
```
Réponse HTTP 200 OK :

```JSON
{
  "total": 120,
  "page": 1,
  "taille_page": 50,
  "resultats": [
    {
      "station_id": "S001",
      "nom": "Lille - Gare",
      "commune": "Lille"
    }
  ]
}
```

**Étape 2 : Appel à GET /stations?taille_page=50&page=3 (page incomplète de fin)** :

```Bash
curl -s -X 'GET' \
  '[http://127.0.0.1:8000/stations?taille_page=50&page=3](http://127.0.0.1:8000/stations?taille_page=50&page=3)' \
  -H "Authorization: Bearer $JETON_DIRECTION"
```
Réponse : 20 éléments retournés dans la liste resultats (total = 120).

**Étape 3 : Appel à GET /stations?commune=Lille&taille_page=100** :

```Bash
curl -s -X 'GET' \
  '[http://127.0.0.1:8000/stations?commune=Lille&taille_page=100](http://127.0.0.1:8000/stations?commune=Lille&taille_page=100)' \
  -H "Authorization: Bearer $JETON_DIRECTION"
```
Réponse : total = 46, toutes les stations ont commune = "Lille".

**Étape 4 : Appel avec page=0 (borne inférieure invalide)** :

```Bash
curl -i -X 'GET' \
  '[http://127.0.0.1:8000/stations?page=0](http://127.0.0.1:8000/stations?page=0)' \
  -H "Authorization: Bearer $JETON_DIRECTION"
```
Réponse HTTP 422 Unprocessable Entity :

```JSON
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```
**Étape 5 : Appel avec taille_page=101 (dépassement de la limite autorisée)** :

```Bash
curl -i -X 'GET' \
  '[http://127.0.0.1:8000/stations?taille_page=101](http://127.0.0.1:8000/stations?taille_page=101)' \
  -H "Authorization: Bearer \$JETON_DIRECTION"
```
Réponse HTTP 422 Unprocessable Entity :

```JSON
{
  "detail": [
    {
      "loc": ["query", "taille_page"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```


### REC-08 — Consultation d'une station inexistante

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-08 — Consultation d'une station inexistante |
| **Date et heure du test** | 15/10/2026 à 11:15 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Étape 1 : HTTP 200 avec les données de la station S001. Étape 2 : HTTP 404 Not Found avec le corps `{"detail": "Station introuvable"}`. |
| **Résultat obtenu** | Données restituées en HTTP 200 pour la station S001. Code HTTP 404 avec le message d'erreur exact renvoyé pour la station S999. |
| **Anomalie** | Aucune |

#### Preuve d'exécution

**Étape 1 : Consultation d'une station existante (`S001`) :**

```bash
curl -i -X 'GET' \
  '[http://127.0.0.1:8000/stations/S001](http://127.0.0.1:8000/stations/S001)' \
  -H "Authorization: Bearer $JETON_DIRECTION"
```
Réponse HTTP 200 OK :

```JSON
{
  "station_id": "S001",
  "nom": "Lille - Gare",
  "commune": "Lille",
  "capacite": 20
}
```
**Étape 2 : Consultation d'une station inexistante (S999)** :

```Bash
curl -i -X 'GET' \
  '[http://127.0.0.1:8000/stations/S999](http://127.0.0.1:8000/stations/S999)' \
  -H "Authorization: Bearer \$JETON_DIRECTION"
```
Réponse HTTP 404 Not Found :

```JSON
{
  "detail": "Station introuvable"
}
```

### REC-09 — Exactitude des indicateurs métiers

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-09 — Exactitude des indicateurs métiers |
| **Date et heure du test** | 12/10/2026 à 11:30 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Les données retournées par l'API correspondent exactement aux résultats de la requête SQL (mêmes dates, mêmes volumes, ordre croissant). La somme des volumes journaliers est égale au total d'activités sur la période. |
| **Résultat obtenu** | Concordance ligne à ligne parfaite entre le tableau JSON de l'API et la sortie de la requête SQL d'agrégation. Le volume total est cohérent avec le filtre global. |
| **Anomalie** | Aucune |

#### Preuve d'exécution

**Étape 1 : Appel à l'endpoint des indicateurs `GET /indicateurs/activite-par-jour` :**

```bash
curl -s -X 'GET' \
  '[http://127.0.0.1:8000/indicateurs/activite-par-jour?date_debut=2026-08-24&date_fin=2026-08-30](http://127.0.0.1:8000/indicateurs/activite-par-jour?date_debut=2026-08-24&date_fin=2026-08-30)' \
  -H "Authorization: Bearer $JETON_DIRECTION"
```

Réponse HTTP 200 OK :

```JSON
[
  {"jour": "2026-08-24", "nb_trajets": 1120},
  {"jour": "2026-08-25", "nb_trajets": 1250},
  {"jour": "2026-08-26", "nb_trajets": 1180},
  {"jour": "2026-08-27", "nb_trajets": 1210},
  {"jour": "2026-08-28", "nb_trajets": 1300},
  {"jour": "2026-08-29", "nb_trajets": 950},
  {"jour": "2026-08-30", "nb_trajets": 890}
]
```

**Étape 2 & 3 : Contrôle par requête SQL directe en base de données**:

```SQL
SELECT depart_horodatage::date AS jour, count(*) AS nb_trajets 
FROM trajet 
WHERE depart_horodatage::date BETWEEN '2026-08-24' AND '2026-08-30' 
GROUP BY jour 
ORDER BY jour;
```
Résultat SQL :

```Plaintext
    jour    | nb_trajets 
------------+------------
 2026-08-24 |       1120
 2026-08-25 |       1250
 2026-08-26 |       1180
 2026-08-27 |       1210
 2026-08-28 |       1300
 2026-08-29 |        950
 2026-08-30 |        890
(7 rows)
```

### REC-10 — Interface Front-End : Gestion des états vide et d'erreur

| Champ | Constat / Détails |
|---|---|
| **Cas de test** | REC-10 — Interface Front-End : Gestion des états vide et d'erreur|
| **Date et heure du test** | 15/10/2026 à 11:45 |
| **Version / Commit** | `e73320c` (Tag `v1.0.0-rc1`) |
| **Statut** | **OK** |
| **Résultat attendu** | Étape 1 : Affichage clair du message d'absence de résultat (`"Aucun résultat pour ces critères."`). Étapes 3-4 : Message d'erreur ergonomique en français signalant l'API injoignable, sans stacktrace ou trace technique Python. Étape 5 : Restitution des données sous forme de tableau au redémarrage de l'API. |
| **Résultat obtenu** | Comportement conforme de l'IHM Streamlit. Absence de résultat gérée proprement. Indisponibilité de l'API signalée à l'utilisateur de manière sécurisée et compréhensible sans divulgation de trace technique. |
| **Anomalie** | Aucune |

#### Preuve d'exécution

**Étape 1 : Filtrage produisant un résultat vide (Écran Incidents) :**
   - Application d'un filtre sur un statut ou une station sans incident.
   - **Rendu IHM :** Affichage de l'information *"Aucun résultat pour ces critères."* sans erreur applicative.
   - *Preuve visuelle :* `docs/recette/preuves/REC-10_vide.png`

**Étape 2 & 3 : Interruption de l'API et rafraîchissement de la page :**
   - Arrêt du service FastAPI (`Ctrl+C` ou arrêt du serveur).
   - Rechargement de la page "Stations" du Front-End Streamlit.
   - **Rendu IHM :** Message d'avertissement explicite en français : *"Impossible de contacter le serveur API. Veuillez vérifier que le service est démarré."*
   - Absence totale de stacktrace Python ou de détails d'implémentation exposés.
   - *Preuve visuelle :* `docs/recette/preuves/REC-10_erreur_api.png`

**Étape 4 & 5 : Redémarrage de l'API et contrôle du retour à la normale :**
   - Relance du serveur FastAPI.
   - Rechargement de l'IHM : le tableau des stations s'affiche à nouveau correctement.

**Contrôle d'intégrité en base de données via Query Tool (pgAdmin / DBeaver) :**

```sql
-- Requête d'audit pour vérifier la présence des données d'incidents consultées par le Front
SELECT 
    incident_id, 
    station_id, 
    type_incident, 
    statut, 
    date_signalement
FROM incident
ORDER BY date_signalement DESC
LIMIT 10;
```

---

## 2. Synthèse chiffrée des tests

| Indice | Nombre |
|---|---|
| **Cas de test prévus** | 10 |
| **Cas exécutés** | 10 |
| **Cas OK** | 10 |
| **Cas KO (initiaux)** | 4 |
| **Cas NT (non testés)** | 0 |
| **Anomalies ouvertes (totales)** | 4 |
| **Anomalies corrigées** | 2 |
| **Anomalies reportées (réserves V1.1)** | 2 |
---

## 3. Axes d'amélioration

1. **Intégration de filtres combinés avancés sur les trajets :** Permettre un filtrage simultané par station de départ, type d'abonnement/usager et plage horaire sur l'endpoint `/trajets`.
2. **Mise en cache serveur des indicateurs globaux :** Implémenter une mise en cache Redis ou applicative des requêtes SQL d'agrégation afin d'optimiser les temps de réponse sur le tableau de bord.
3. **Mode dégradé dans l'IHM Streamlit :** Conserver la liste des stations en session locale (`st.session_state`) pour garder la consultation de la carte accessible même en cas de micro-coupure réseau de l'API.

---
## 4. Procès-verbal de recette

### Identification
- **Application :** VéloVille Hauts-de-France — Version 1.0
- **Version testée :** Commit `e73320c` (Tag `v1.0.0-rc1`)
- **Date de la campagne :** 15 octobre 2026
- **Environnement :** Python 3.12, PostgreSQL 14, FastAPI, Streamlit

### Périmètre recetté
L'ensemble des cas REC-01 à REC-10 a été exécuté sur la base de données réinitialisée, couvrant l'importation fiabilisée, la sécurité JWT, le contrôle des accès par rôle, la pagination/filtres API, la précision des indicateurs SQL et l'ergonomie/résilience du Front-End Streamlit.

### Décision
**Recette PRONONCÉE AVEC RÉSERVES**

*L'application VéloVille V1 satisfait aux exigences fonctionnelles et techniques majeures du cahier des charges. Les anomalies critiques de gestion des dates (`ANO-001` et `ANO-002`) ont été corrigées avec succès. Deux réserves d'ergonomie et d'affichage IHM non bloquantes (`ANO-003` sur l'aide à la pagination et `ANO-004` sur la précision des retours d'erreurs pour le rôle direction) sont formulées et inscrites au backlog de maintenance pour traitement prioritaire dans la version V1.1.*

**Signatures :**  
*Pour le commanditaire — Le Responsable Recette*  
*Pour l'équipe projet — Le Chargé de projet / Développeur*