# Schéma de données

À compléter : MLD textuel ou image, description des tables, clés et contraintes,
règles de gestion portées par le schéma.

### 1. Modèle Logique de Données (MLD) textuel

* **STATION** (`<u>station_id</u>`, nom, commune, capacite, latitude, longitude, date_mise_en_service)
* **TRAJET** (`<u>trajet_id</u>`, velo_id, depart_horodatage, `#station_depart` → STATION(station_id), `#station_arrivee` → STATION(station_id), duree_secondes, type_usager, usager_ref)
* **INCIDENT** (`<u>incident_id</u>`, date_signalement, cible, velo_id, `#station_id` → STATION(station_id), type_incident, statut, date_resolution, technicien)
* **UTILISATEUR** (`<u>id_utilisateur</u>`, username, mot_de_passe_hash, role)

---

### 2. Description des tables, clés et contraintes

* **Table `station`** :
  * **Clé primaire** : `station_id`
  * **Contraintes** : `capacite` doit être strictement positive (`> 0`). Les coordonnées géographiques (`latitude`, `longitude`) et la date de mise en service sont obligatoires (`NOT NULL`).

* **Table `trajet`** :
  * **Clé primaire** : `trajet_id`
  * **Clés étrangères** : `station_depart` (obligatoire, restreint en suppression) et `station_arrivee` (facultative si le vélo n'a pas été restitué).
  * **Contraintes** : La durée du trajet (`duree_secondes`) doit être strictement positive. Le type d'usager est restreint à deux valeurs (`abonne` ou `occasionnel`). Le format du vélo (`velo_id`) doit être respecté.

* **Table `incident`** :
  * **Clé primaire** : `incident_id`
  * **Clé étrangère** : `station_id` (référencée uniquement si l'incident concerne une station).
  * **Contraintes de cohérence métier (CHECK)** :
    * *Cible exclusive* : Si la cible est un `velo`, `velo_id` doit être renseigné et `station_id` doit être nul. Inversement, si la cible est une `station`, `station_id` doit être renseigné et `velo_id` doit être nul.
    * *Statut et Résolution* : Le statut est limité à `ouvert`, `en_cours` ou `resolu`. Si l'incident est `resolu`, la `date_resolution` devient obligatoire et doit être chronologiquement postérieure ou égale à la `date_signalement`. Si l'incident n'est pas résolu, la date de résolution doit être nulle.

* **Table `utilisateur`** :
  * **Clé primaire** : `id_utilisateur` (générée automatiquement par `SERIAL`).
  * **Contraintes** : `username` est unique et obligatoire. Le rôle est restreint à `exploitant` ou `direction`.

---

### 3. Règles de gestion portées par le schéma (RG1 à RG8)

Le schéma traduit directement les contraintes métiers du projet via les mécanismes SQL :
1. **Intégrité référentielle** : Assurée par les `FOREIGN KEY` avec la règle `ON DELETE RESTRICT` pour empêcher la suppression d'une station rattachée à des trajets ou des incidents.
2. **Cohérence des données (Contraintes CHECK)** : Validation native en base des capacités de stations positives, des durées de trajets positives, des types d'usagers et des statuts d'incidents autorisés.
3. **Exclusivité des cibles d'incidents** : La contrainte `chk_cible_coherence` garantit qu'un incident cible soit un vélo, soit une station, mais jamais les deux en même temps, ni aucun des deux.
4. **Logique temporelle des résolutions** : La contrainte `chk_date_resolution` interdit l'incohérence d'une date de résolution sur un incident non résolu ou d'une date antérieure au signalement.