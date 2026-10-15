# Schéma de données

À compléter : MLD textuel ou image, description des tables, clés et contraintes,
règles de gestion portées par le schéma.

### 1. Modèle Logique de Données (MLD) textuel

* **STATION** (`station_id`, nom, commune, capacite, latitude, longitude, date_mise_en_service)
* **TRAJET** (`trajet_id`, velo_id, depart_horodatage, `#station_depart` → STATION(station_id), `#station_arrivee` → STATION(station_id), duree_secondes, type_usager, usager_ref)
* **INCIDENT** (`incident_id`, date_signalement, cible, velo_id, `#station_id` → STATION(station_id), type_incident, statut, date_resolution, technicien)
* **UTILISATEUR** (`id_utilisateur`, username, mot_de_passe_hash, role)

---

### 2. Description des tables, clés et contraintes

* **Table `station`** :
  * **Clé primaire** : `station_id`
  * **Contraintes** : `capacite` doit être strictement positive (`> 0`). Les coordonnées géographiques (`latitude`, `longitude`) et la date de mise en service sont obligatoires (`NOT NULL`).

* **Table `trajet`** :
  * **Clé primaire** : `trajet_id`
  * **Clés étrangères** : `station_depart` (obligatoire, restreint en suppression -interdit de supprimer une station si des trajets sont encore rattachés- ) et `station_arrivee` (facultative si le vélo n'a pas été restitué).
  * **Contraintes** : La durée du trajet (`duree_secondes`) doit être strictement positive. Le type d'usager est restreint à deux valeurs (`abonne` ou `occasionnel`). Le format du vélo (`velo_id`) doit être respecté.

* **Table `incident`** :
  * **Clé primaire** : `incident_id`
  * **Clé étrangère** : `station_id` (référencée uniquement si l'incident concerne une station).
  * **Contraintes de cohérence (CHECK)** :
    * *Cible exclusive* : Si la cible est un `velo`, `velo_id` doit être renseigné et `station_id` doit être nul. Inversement, si la cible est une `station`, `station_id` doit être renseigné et `velo_id` doit être nul.
    * *Statut et Résolution* : Le statut est limité à `ouvert`, `en_cours` ou `resolu`. Si l'incident est `resolu`, la `date_resolution` devient obligatoire et doit être chronologiquement postérieure ou égale à la `date_signalement`. Si l'incident n'est pas résolu, la date de résolution doit être nulle.

* **Table `utilisateur`** :
  * **Clé primaire** : `id_utilisateur` (générée automatiquement par `SERIAL`).
  * **Contraintes** : `username` est unique et obligatoire. Le rôle est restreint à `exploitant` ou `direction` pour cette version V1.

---

### 3. Règles de gestion portées par le schéma (RG1 à RG8)

Le schéma sql traduit directement les contraintes métiers du projet "véloville" :

1. **Intégrité référentielle** : Assurée par les `FOREIGN KEY` avec la règle `ON DELETE RESTRICT` pour empêcher la suppression d'une station rattachée à des trajets ou des incidents.
2. **Cohérence des données (Contraintes CHECK)** : Validation en base (via PostgreSQL) des capacités de stations positives, des durées de trajets positives, des types d'usagers et des statuts d'incidents autorisés.
3. **Exclusivité des cibles d'incidents** : La contrainte `chk_cible_coherence` garantit qu'un incident cible soit un vélo, soit une station, mais jamais les deux en même temps, ni aucun des deux.
4. **Logique temporelle des résolutions** : La contrainte `chk_date_resolution` interdit l'incohérence d'une date de résolution sur un incident non résolu ou d'une date antérieure au signalement.



---
---


# Rajouter 'Rapport d'Audit et de Fiabilisation des Données

### 1. Introduction et Méthodologie
---

L'intégration des données issues du système de billettique (`stations.csv`, `trajets.csv`, `incidents.csv`) dans la base de données PostgreSQL (`veloville`) s'appuie sur un processus d'ETL et de fiabilisation implémenté dans `api/services/fiabilisation.py` et orchestré par `scripts/importer.py`.  

Cet audit croise les anomalies constatées avec :
- Le dictionnaire des données du projet.
- Les règles de gestion RG1 à RG8 du cahier des charges.
- Les contraintes d'intégrité du schéma relationnel (clés primaires, clés étrangères, types de données et contraintes de domaine).



### 2. Analyse Détaillée par Fichier Source
---

#### A. Fichier `stations.csv` (Référentiel des stations)
- **Description** : Contient les informations descriptives, géographiques et techniques des stations de vélos.
- **Volume brut analysé** : 120 lignes.  
- **Défauts identifiés & Règles associées** :
  - **RG1 (Capacité valide)** : Vérification que la capacité de chaque station est un entier strictement positif (> 0). Aucune anomalie n'a été relevée sur ce référentiel.  
  - **Intégrité géographique (RG2)** : Les coordonnées géographiques (latitude et longitude) s'inscrivent correctement dans la zone d'implantation cible.
- **Nombre de lignes concernées** : 0 rejet.  
- **Traitement retenu** : Intégration directe de l'ensemble du référentiel après formatage des dates de mise en service au type date SQL.  
- **Volume validé** : 120 lignes insérées.  

#### B. Fichier `trajets.csv` (Historique des locations de vélos)
- **Description** : Enregistre les mouvements de vélos entre stations, incluant les horodatages, les durées et les profils d'usagers.
- **Volume brut analysé** : 2 030 lignes.  
- **Défauts identifiés & Règles associées** :
  - **Violations d'intégrité référentielle (RG2 / FK)** : Présence de 6 trajets rattachés à une station d'arrivée inexistante dans le référentiel (`station_arrivee = 'S999'`).
  - **Incohérences de durée (RG4 / RG3)** : Présence de 9 lignes comportant des durées de trajet invalides, nulles ou négatives (0, -45 secondes, -120 secondes).
  - **Doublons d'identifiants (RG6)** : Détection de 12 lignes dupliquées basées sur l'identifiant du trajet (`trajet_id`).
  - **Non-conformité des formats temporels** : 5 lignes présentant des horodatages de départ au format textuel non ISO (ex: `DD/MM/YYYY HH:MM` au lieu du format `AAAA-MM-JJ HH:MM:SS`).
- **Nombre de lignes concernées** : 32 lignes rejetées.  
- **Traitement retenu (`fiabilisation.py`)** : Rejet systématique des trajets orphelins (station inconnue), des durées $\le 0$, des doublons d'ID et des formats de date non parsables afin de préserver l'intégrité référentielle et contraintes de domaine. Les motifs sont consignés lligne par ligne dans `docs/journal-rejets.csv`.  
- **Volume validé** : 1 998 lignes intégrées.  

#### C. Fichier `incidents.csv` (Signalements et pannes)
- **Description** : Recense les anomalies signalées sur les équipements (stations ou vélos).
- **Volume brut analysé** : 180 lignes.  
- **Défauts identifiés & Règles associées** :
  - **Variations de casse et formats (RG7)** : 124 lignes présentaient des libellés de statuts saisis avec des variations de casse ou des espaces (ex. `En cours`, `RESOLU`, `Ouvert`, `Resolu`) au lieu de la nomenclature normalisée.  
  - **Incohérences temporelles critiques (RG8)** : 3 incidents (`I2026-0028`, `I2026-0124`, `I2026-0178`) affichant une `date_resolution` strictement antérieure à la `date_signalement`.
  - **Intégrité de la cible (RG6)** : Vérification de la cohérence entre la cible déclarée (station ou vélo) et la présence de l'identifiant associé.
- **Nombre de lignes concernées** :
  - 3 lignes rejetées en raison de l'incohérence chronologique des dates (RG8).  
  - 124 lignes modifiées ayant fait l'objet d'un avertissement de normalisation (consigné dans `docs/journal-avertissements.csv`).  
- **Traitement retenu (`fiabilisation.py`)** : Normalisation automatique de la casse des statuts vers les valeurs suivantes: (`ouvert`, `en_cours`, `resolu`). Rejet strict des incidents dont la résolution précède le signalement.  
- **Volume validé** : 177 lignes intégrées.  

---

### 3. Synthèse Globale de l'Audit ETL

| Fichier Source | Volume Brut | Volume Intégré | Lignes Rejetées | Taux de Rejet | Avertissements (Normalisation) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `stations.csv` | 120 | 120 | 0 | 0.00 % | 0 |
| `trajets.csv` | 2 030 | 1 998 | 32 | 1.58 % | 0 |
| `incidents.csv` | 180 | 177 | 3 | 1.67 % | 124 |
| **TOTAL** | **2 330** | **2 295** | **35** | **1.50 %** | **124** |

---

### 4. Garanties d'Idempotence et Traçabilité

- **Traçabilité** : Chaque rejet de ligne est documenté dans `docs/journal-rejets.csv` avec mention du fichier source, de l'identifiant de l'entité, du code de règle enfreint et du motif détaillé.  
- **Idempotence** : Le script d'import nettoie systématiquement les tables cibles via une commande de purge en cascade (`TRUNCATE TABLE incident, trajet, station CASCADE;`) avant d'insérer les flux propres, garantissant que des exécutions successives laissent la base de données dans un état strictement identique.
