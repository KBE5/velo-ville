# Épreuve E.2 — Cas pratique : développement et suivi du cycle de vie d'une application — Sujet

Certification : Chargé de développement de solutions applicatives ou
logicielles — RNCP39103 — niveau 6.
Classe : Data Analyst 02 — Villeneuve d'Ascq.

## Bloc et compétences évaluées

Bloc 2 — Concevoir et développer la solution logicielle ou applicative.
Compétences C2.1, C2.2.1, C2.2.2, C2.3, C2.4 du référentiel RNCP39103.

## Durée et modalités

- **Production du dossier en conditions encadrées : mardi 07 et mercredi
  08/10/2026** (2 x 7 h, soit 14 h), sur poste informatique individuel.
  Le présent sujet est remis le 07/10 à 09:00.
- **Finalisation et dépôt : lundi 12/10/2026**, dépôt au plus tard à 15:30
  (voir « Modalités de dépôt »). Cette journée est consacrée à la recette,
  aux corrections et à la mise au propre de la documentation ; aucune
  fonctionnalité nouvelle n'est attendue.
- **Soutenance orale : mardi 13 et mercredi 14/10/2026** — 30 minutes par
  candidat : 20 minutes de présentation et de démonstration de l'application
  en fonctionnement, puis 10 minutes de questions du jury.
- Épreuve individuelle : dépôt de code et dossier individuels. Outils
  autorisés : IDE, Git, documentation officielle des bibliothèques, vos
  supports de cours. L'usage d'outils d'IA générative n'est pas autorisé ;
  tout plagiat ou toute production non personnelle entraîne l'invalidation
  de l'épreuve.

## Contexte et besoin du commanditaire

Commanditaire fictif : **VéloVille Hauts-de-France**, opérateur régional de
vélos en libre-service (120 stations, 1 800 vélos, environ 9 000 trajets par
jour). L'entreprise dispose de données brutes hétérogènes issues de son
système de billettique (trajets, stations, incidents de maintenance) et
souhaite une solution applicative de valorisation de ces données : collecte
et fiabilisation, exposition via une API sécurisée, et restitution destinée
aux équipes d'exploitation et à la direction.

Le cahier des charges de la solution VéloVille, élaboré au bloc 1, **a été
validé**. Une version de référence vous est fournie
(`ressources/cahier-des-charges-reference.md`) ; c'est elle qui fait foi,
indépendamment de votre propre production du bloc 1. La stratégie de
déploiement est arrêtée :

- back-end Python exposant une **API REST** (FastAPI) ;
- base de données relationnelle **PostgreSQL** ;
- front-end web de restitution **Streamlit**, responsive et accessible,
  limité à une restitution tabulaire (tableaux et métriques, sans graphique).

Pour cette première version, la direction a réduit le périmètre à trois
ressources (stations, trajets, incidents), trois indicateurs et deux profils
d'utilisateurs (exploitant, direction). Les données météo et les fonctions
d'anticipation sont reportées à une version ultérieure.

Vous êtes chargé(e) de développer la solution et d'en assurer le cycle de
vie : import et fiabilisation des données, API sécurisée, restitution, tests,
recette, gestion des accès, documentation, versioning et maintenance
préventive.

## Ressources fournies

Le dossier `ressources/` contient :

- `donnees/stations.csv`, `donnees/trajets.csv`, `donnees/incidents.csv` :
  les trois exports du système de billettique ;
- `README-donnees.md` : dictionnaire des données des trois fichiers ;
- `cahier-des-charges-reference.md` : la version de référence du cahier des
  charges (contexte, périmètre, règles de gestion RG1 à RG8, exigences) ;
- `maquettes-ecrans.md` : les maquettes des quatre écrans du front ;
- `plan-de-recette.md` : le plan de recette à dérouler (cas REC-01 à
  REC-10), avec un modèle de fiche d'anomalie et un modèle de procès-verbal ;
- `squelette-git/` : le squelette du projet à initialiser (arborescence,
  fichiers à compléter, `requirements.txt`, `.gitignore`, `.env.example`,
  `sql/comptes.sql` avec les deux comptes fournis, copie des CSV dans
  `data/`). Lisez `squelette-git/README-SQUELETTE.md` avant de commencer.

Environnement de développement : Python 3.12, PostgreSQL 14 ou supérieur,
Git. Les bibliothèques attendues sont listées dans `requirements.txt`.

## Contrats techniques

Les éléments ci-dessous sont imposés. Ils permettent au jury de rejouer
votre application et le plan de recette sans adaptation. Tout écart doit
être justifié dans le README.

### Base de données `veloville`

```
station(station_id VARCHAR(10) PK, nom, commune, capacite INTEGER,
        latitude NUMERIC(8,5), longitude NUMERIC(8,5),
        date_mise_en_service DATE)
trajet(trajet_id VARCHAR(12) PK, velo_id VARCHAR(8),
       depart_horodatage TIMESTAMP, station_depart FK station,
       station_arrivee FK station NULL, duree_secondes INTEGER CHECK > 0,
       type_usager, usager_ref NULL)
incident(incident_id VARCHAR(12) PK, date_signalement TIMESTAMP, cible,
         velo_id NULL, station_id FK station NULL, type_incident,
         statut CHECK IN ('ouvert','en_cours','resolu'),
         date_resolution NULL, technicien NULL)
utilisateur(id_utilisateur SERIAL PK, username UNIQUE, mot_de_passe_hash,
            role CHECK IN ('exploitant','direction'))
```

Connexion lue dans la variable d'environnement `DATABASE_URL` ; valeur par
défaut : `postgresql+psycopg://veloville:veloville@localhost:5432/veloville`.

### Comptes fournis (`sql/comptes.sql`, mots de passe hachés bcrypt)

| Identifiant | Mot de passe | Rôle |
|---|---|---|
| exploitant01 | Formation2026! | exploitant |
| direction01 | Formation2026! | direction |

### API (FastAPI)

Toutes les routes exigent un jeton JWT valide dans l'en-tête
`Authorization: Bearer <jeton>`, sauf `GET /sante` et `POST /auth/login`.

| Méthode et route | Paramètres | Réponse 200 |
|---|---|---|
| GET /sante | — | `{"statut": "ok"}` |
| POST /auth/login | corps `{"username", "password"}` | `{"access_token", "token_type": "bearer", "role"}` |
| GET /stations | `commune`, `page`, `taille_page` | enveloppe paginée de stations |
| GET /stations/{station_id} | — | une station |
| GET /trajets | `date_debut`, `date_fin`, `station`, `page`, `taille_page` | enveloppe paginée de trajets |
| GET /incidents | `statut`, `page`, `taille_page` | enveloppe paginée d'incidents |
| PUT /incidents/{incident_id}/statut | corps `{"statut": "en_cours"}` ou `{"statut": "resolu"}` | l'incident mis à jour |
| GET /indicateurs/activite-par-jour | `date_debut`, `date_fin` | `{"donnees": [{"jour": "2026-08-24", "nb_trajets": n}, ...]}` |
| GET /indicateurs/stations-actives | `limite` (défaut 10) | `{"donnees": [{"station_id", "nom", "nb_departs", "nb_arrivees"}, ...]}` |
| GET /indicateurs/incidents-par-statut | — | `{"donnees": [{"statut", "nb_incidents"}, ...], "delai_moyen_resolution_heures": x}` |

Précisions :

- Enveloppe paginée : `{"total", "page", "taille_page", "resultats": [...]}`.
  `page >= 1`, `taille_page` entre 1 et 100, valeur par défaut 20 ; toute
  valeur hors bornes renvoie 422. Les stations sont triées par
  `station_id`, les trajets par `depart_horodatage` croissant, les
  incidents par `date_signalement` décroissant.
- Un objet station, trajet ou incident reprend les colonnes de sa table ;
  les dates et horodatages sont sérialisés au format ISO 8601.
- `GET /trajets` : `date_debut` et `date_fin` (format `AAAA-MM-JJ`)
  bornent inclusivement la date de `depart_horodatage` ; `station`
  retient les trajets dont la station de départ **ou** d'arrivée est celle
  indiquée.
- `PUT /incidents/{incident_id}/statut` est réservé au rôle exploitant.
  Transitions autorisées : `ouvert -> en_cours`, `ouvert -> resolu`,
  `en_cours -> resolu`. Le passage à `resolu` renseigne `date_resolution`
  avec l'horodatage courant si elle est vide. Toute autre transition
  renvoie 422 `{"detail": "Transition de statut non autorisee"}`.
- Indicateur 1 : nombre de trajets par jour de départ sur la période
  demandée (bornes incluses), un élément par jour comportant au moins un
  trajet, trié par jour croissant. Sans paramètre, toute la période connue.
- Indicateur 2 : les `limite` stations ayant le plus de mouvements
  (`nb_departs + nb_arrivees`), ordre décroissant puis `station_id`
  croissant ; une arrivée inconnue ne compte pour aucune station.
- Indicateur 3 : nombre d'incidents par statut (un élément par statut
  présent en base) et délai moyen de résolution en heures, calculé sur les
  incidents `resolu` dont `date_resolution` est renseignée, arrondi à une
  décimale ; `null` si aucun incident résolu.
- Codes d'erreur : 401 `{"detail": "Identifiants invalides"}` pour un
  login refusé ; 401 sans jeton ou avec un jeton invalide ou expiré ;
  403 `{"detail": "Acces reserve au role exploitant"}` pour un rôle
  insuffisant ; 404 `{"detail": "Station introuvable"}` ou
  `{"detail": "Incident introuvable"}` ; 422 pour toute erreur de
  validation.
- JWT signé en HS256 avec le secret `JWT_SECRET` lu dans l'environnement,
  durée de validité `JWT_EXPIRATION_MINUTES`, charge utile contenant au
  moins `sub` (identifiant) et `role`.

### Front (Streamlit)

- `front/app.py` : écran de connexion (formulaire), jeton et rôle stockés
  dans `st.session_state`.
- `front/pages/1_Stations.py` : tableau filtrable par commune, pagination.
- `front/pages/2_Incidents.py` : tableau filtrable par statut ; pour le
  rôle exploitant, changement de statut d'un incident via l'API.
- `front/pages/3_Indicateurs.py` : trois `st.metric` (nombre de trajets de
  la période, nombre de stations actives retournées, délai moyen de
  résolution) et trois tableaux issus des trois endpoints `/indicateurs`.
- `front/api_client.py` centralise les appels HTTP : adresse `API_URL`,
  délai `API_TIMEOUT_SECONDES`, en-tête Bearer, exception `ErreurApi` avec
  message en français.
- Chaque écran gère trois états : chargement, résultat vide, erreur (API
  injoignable ou réponse en erreur), avec des messages en français.
- Aucun graphique : la restitution est tabulaire (`st.dataframe`,
  `st.table`, `st.metric`).

### Arborescence du dépôt rendu

```
veloville/
  README.md            requirements.txt    .gitignore    CHANGELOG.md
  .env.example
  data/                              les 3 CSV
  sql/schema.sql  sql/comptes.sql
  scripts/importer.py                import + fiabilisation, idempotent
  scripts/sauvegarde.sh              pg_dump horodaté
  api/main.py database.py models.py schemas.py securite.py
  api/routers/auth.py stations.py trajets.py incidents.py indicateurs.py
  api/services/fiabilisation.py indicateurs.py     modules métier testés
  tests/conftest.py  tests/unit/  tests/integration/
  front/app.py api_client.py pages/1_Stations.py 2_Incidents.py
                                 pages/3_Indicateurs.py
  docs/schema-donnees.md matrice-roles-droits.md procedure-deploiement.md
  docs/recette/plan-de-recette.md resultats-recette.md anomalies/
```

## Travail demandé

### Travail 1 — Environnement, composants, tests et correction des bugs (C2.1)

Sélectionner et configurer l'environnement de développement, implémenter
et paramétrer les composants (import et fiabilisation des données, calcul
des indicateurs), les tester sur les données fournies et corriger les bugs.

Consignes :

1. Initialisez le dépôt Git à partir du squelette fourni (voir
   `README-SQUELETTE.md`), créez un environnement virtuel, installez les
   dépendances et fixez leurs versions dans `requirements.txt`.
2. Créez la base `veloville` et le rôle PostgreSQL associé, puis écrivez
   `sql/schema.sql` conformément au contrat (types, clés primaires et
   étrangères, contraintes CHECK). Le script doit être rejouable.
3. Exécutez `sql/comptes.sql` pour charger les deux comptes fournis.
4. Auditez les trois exports CSV avant de les charger. **Ils proviennent du
   système de billettique et n'ont pas été fiabilisés : ils comportent des
   défauts de plusieurs natures.** Appuyez-vous sur le dictionnaire des
   données, sur les règles de gestion RG1 à RG8 du cahier des charges et sur
   les contraintes du schéma pour les repérer. Votre audit (défauts
   identifiés, nombre de lignes concernées, traitement retenu) figure dans
   le README ou dans `docs/schema-donnees.md`.
5. Écrivez les règles de fiabilisation sous forme de **fonctions pures**
   dans `api/services/fiabilisation.py` (une fonction par règle, sans accès
   à la base). Politique de traitement attendue :
   - une valeur dont le format ou la casse peut être corrigé sans ambiguïté
     est **normalisée** et la ligne est importée (avertissement journalisé) ;
   - une ligne qui viole une règle de gestion ou une contrainte du schéma
     après normalisation est **rejetée** (rejet journalisé) ;
   - une ligne strictement identique à une ligne déjà traitée n'est
     importée qu'une fois ;
   - une donnée facultative absente n'entraîne pas de rejet.
6. Écrivez `scripts/importer.py`, qui lit les trois fichiers de `data/`,
   applique les règles, charge les lignes valides dans l'ordre des
   dépendances (stations, puis trajets et incidents) et produit un
   **journal des rejets et avertissements** (fichier CSV ou texte dans
   `docs/` ou à la racine, chemin indiqué dans le README) comportant pour
   chaque ligne : fichier source, identifiant, colonne, valeur, motif,
   décision (rejet ou normalisation). L'import doit être **idempotent** :
   une seconde exécution ne crée ni doublon ni erreur.
7. Implémentez les trois indicateurs dans `api/services/indicateurs.py`,
   sous forme de fonctions appelées par les routeurs, conformément aux
   précisions du contrat.
8. Testez sur les données fournies et corrigez ce qui ne fonctionne pas ;
   chaque correction significative donne lieu à un commit explicite.

Livrables : `requirements.txt` versionné, `sql/schema.sql`,
`scripts/importer.py`, `api/services/fiabilisation.py`,
`api/services/indicateurs.py`, le journal des rejets, la section d'audit
des données.

Vérifiez vous-même :

- `python scripts/importer.py` exécuté deux fois donne les mêmes comptages
  (`SELECT count(*)` sur les trois tables) ;
- pour chaque fichier, lignes importées + lignes rejetées + doublons
  écartés = nombre de lignes du CSV ;
- aucune ligne de `trajet` ou `incident` ne référence une station absente
  de `station` ; aucune durée nulle ou négative ; aucun statut hors des
  trois valeurs autorisées ;
- chaque fonction de `fiabilisation.py` s'exécute sans base de données.

### Travail 2 — Déploiement back-end et front-end, tests, écoresponsabilité (C2.2.1)

Déployer la partie back-end (API REST) et front-end (restitution responsive
et accessible), en effectuant les tests unitaires et fonctionnels
(couverture minimale 60 % des modules métier) et en veillant à
l'écoresponsabilité des choix techniques.

Consignes :

1. Implémentez l'API décrite dans le contrat : connexion SQLAlchemy
   (`api/database.py`), modèles (`api/models.py`), schémas Pydantic
   (`api/schemas.py`), un routeur par ressource. Les routeurs ne
   contiennent pas de logique métier : ils appellent `api/services/`.
2. Implémentez la pagination et les filtres exactement comme spécifiés ;
   les paramètres hors bornes renvoient 422.
3. Implémentez le front Streamlit conformément à
   `ressources/maquettes-ecrans.md` : les quatre écrans, le client HTTP
   centralisé, les trois états (chargement, vide, erreur). Veillez à
   l'accessibilité : libellés explicites sur chaque champ et bouton,
   messages d'erreur textuels, aucune information portée uniquement par la
   couleur, en-têtes de colonnes lisibles.
4. Écrivez les tests pytest :
   - `tests/unit/` : les règles de fiabilisation (cas nominal et cas de
     rejet pour chaque règle) et le calcul des indicateurs ;
   - `tests/integration/` : avec `TestClient`, au minimum `GET /sante`,
     `POST /auth/login` (succès et échec), une route protégée appelée sans
     jeton (401) et `PUT /incidents/{incident_id}/statut` avec le rôle direction
     (403).
   Les tests lisent la configuration dans l'environnement ; aucun secret en
   dur. Un test qui modifie des données remet la base dans son état initial.
5. Mesurez la couverture des modules métier :
   `pytest --cov=api/services --cov-report=term-missing`. Le résultat doit
   être supérieur ou égal à 60 % ; reportez le chiffre obtenu dans le README.
6. Rédigez dans le README une section **« Choix écoresponsables »** qui
   explique, en quelques lignes chacun : la pagination côté serveur et la
   taille de page bornée, l'absence de rafraîchissement automatique ou de
   temps réel dans le front, la mise en cache des données de référence
   (par exemple `st.cache_data` sur la liste des stations, avec une durée de
   vie), et tout autre choix que vous jugez pertinent (requêtes agrégées en
   SQL plutôt qu'en Python, absence de dépendance superflue).

Livrables : `api/` complet, `front/` complet, `tests/` avec `conftest.py`,
chiffre de couverture dans le README, section « Choix écoresponsables ».

Vérifiez vous-même :

- `uvicorn api.main:app` démarre sans erreur et `GET /sante` répond
  `{"statut": "ok"}` ;
- `GET /stations` sans jeton renvoie 401, avec jeton renvoie l'enveloppe
  paginée avec `total` = 120 après import ;
- `pytest` est vert ; la couverture affichée sur `api/services` est au
  moins 60 % ;
- `streamlit run front/app.py` : connexion avec exploitant01, puis les
  trois pages affichent leurs données ; l'API arrêtée, chaque page affiche
  un message d'erreur en français et non une trace Python.

### Travail 3 — Recette (C2.2.2)

Conduire la recette de la solution : dérouler le plan de recette fourni,
évaluer les composants en condition de production, corriger les anomalies
détectées et consigner les axes d'amélioration.

Consignes :

1. Déroulez les dix cas du plan `docs/recette/plan-de-recette.md` sur votre
   application, dans l'ordre, à partir d'un état connu (base réimportée).
   Ne corrigez rien pendant le passage : relevez.
2. Consignez chaque résultat dans `docs/recette/resultats-recette.md` :
   résultat obtenu, statut (OK, KO, non testé), preuve (commande, extrait de
   réponse, capture).
3. Pour chaque cas KO, rédigez une fiche dans `docs/recette/anomalies/`
   (une fiche par anomalie, nommée `ANO-001.md`, `ANO-002.md`, ...) selon le
   modèle du plan : symptôme, cas de test, environnement, reproduction,
   attendu / obtenu, sévérité, priorité, statut.
4. Corrigez les anomalies, chaque correction dans un commit qui cite
   l'identifiant de la fiche (`Corrige ANO-002 : ...`). Ajoutez un test de
   non-régression pour chaque anomalie corrigée. Rejouez les cas concernés
   et mettez à jour le relevé et le statut des fiches.
5. Terminez `resultats-recette.md` par une synthèse chiffrée (cas exécutés,
   OK, KO, corrigés), par un **procès-verbal de recette** selon le modèle
   fourni, et par une section **« Axes d'amélioration »** : au moins trois
   propositions argumentées au regard du besoin du commanditaire (fonctions
   reportées, limites constatées, dette technique).

Livrables : `docs/recette/resultats-recette.md`, `docs/recette/anomalies/`,
tests de non-régression, commits de correction.

Vérifiez vous-même :

- les dix cas ont un statut et une preuve ;
- chaque KO initial a une fiche, un commit de correction et un test ;
- le procès-verbal porte une décision motivée (prononcée, prononcée avec
  réserves ou refusée).

### Travail 4 — Accès : authentification, rôles, droits, données sensibles (C2.3)

Paramétrer les accès : authentification, rôles (exploitant, direction),
droits d'accès et sécurisation des données sensibles.

Consignes :

1. Implémentez `POST /auth/login` : vérification du mot de passe contre le
   hachage bcrypt stocké, émission d'un JWT signé (HS256) contenant
   l'identifiant et le rôle, avec une date d'expiration.
2. Implémentez dans `api/securite.py` les dépendances de protection :
   utilisateur courant (401 si jeton absent, invalide ou expiré) et contrôle
   de rôle (403 si le rôle est insuffisant). Protégez toutes les routes
   sauf `/sante` et `/auth/login`.
3. Réservez `PUT /incidents/{incident_id}/statut` au rôle exploitant ; le
   rôle direction obtient 403 avec le message du contrat.
4. Aucun secret en dur : `DATABASE_URL`, `JWT_SECRET` et les autres
   paramètres sont lus dans l'environnement (fichier `.env` ignoré par Git,
   `.env.example` versionné sans valeur sensible). Les mots de passe ne sont
   jamais stockés ni journalisés en clair.
5. Dans le front, le jeton n'apparaît ni dans l'URL ni à l'écran ; les
   actions non autorisées pour le rôle connecté sont masquées ou
   désactivées, et un refus de l'API (403) est affiché en français.
6. Rédigez `docs/matrice-roles-droits.md` : une ligne par route, une
   colonne par profil (anonyme, exploitant, direction), avec le code HTTP
   attendu en cas de refus, puis une section « Données sensibles » qui
   identifie les données à protéger (mots de passe, `usager_ref`
   pseudonymisé, jeton) et les mesures prises.

Livrables : `api/securite.py`, `api/routers/auth.py`, `.env.example`,
`docs/matrice-roles-droits.md`.

Vérifiez vous-même :

- `git grep -i "Formation2026"` ne renvoie que `sql/comptes.sql` (hachages)
  et la documentation ; `git grep -n "JWT_SECRET"` ne renvoie aucune valeur
  réelle ;
- un jeton modifié d'un caractère est refusé (401) ;
- direction01 peut lire les incidents mais reçoit 403 sur le PUT ;
  exploitant01 peut modifier un statut.

### Travail 5 — Documentation, versioning, schéma de données, maintenance préventive (C2.4)

Documenter la solution déployée : documentation technique et
fonctionnelle, historique de versioning structuré (commits, branches),
schéma de données, scripts d'automatisation de la maintenance préventive.

Consignes :

1. `README.md` : présentation, prérequis, installation pas à pas, variables
   d'environnement, import des données, lancement de l'API et du front,
   exécution des tests et couverture obtenue, audit des données, choix
   écoresponsables, limites connues.
2. `docs/schema-donnees.md` : le MLD (textuel ou image exportée dans
   `docs/`), la description de chaque table et contrainte, et la manière
   dont les règles de gestion RG1 à RG8 sont portées par le schéma ou par
   l'import.
3. `docs/procedure-deploiement.md` : procédure reproductible sur un poste
   vierge, de la création de la base à la vérification de `GET /sante`, y
   compris la sauvegarde et la restauration.
4. `CHANGELOG.md` : une entrée par version livrée (au minimum une version
   avant recette et une version après corrections), changements regroupés
   en Ajouté, Modifié, Corrigé.
5. Historique Git structuré : commits fréquents aux messages explicites
   (verbe à l'infinitif ou au présent, périmètre indiqué), **au moins une
   branche de fonctionnalité ou de correction fusionnée** dans la branche
   principale, un tag par version du CHANGELOG. Aucun fichier `.env`,
   aucun environnement virtuel, aucune sauvegarde dans le dépôt.
6. `scripts/sauvegarde.sh` (**obligatoire**) : sauvegarde `pg_dump`
   horodatée (`sauvegardes/veloville_AAAAMMJJ_HHMMSS.dump`), connexion lue
   dans l'environnement, code de retour non nul en cas d'échec, commande de
   restauration documentée.
7. En bonus, si le temps le permet : un script de purge (par exemple
   suppression des trajets de plus de N jours, paramètre en argument, mode
   simulation par défaut) ou un script de contrôle d'intégrité (requêtes de
   vérification des règles de gestion, rapport en sortie).

Livrables : `README.md`, `docs/schema-donnees.md`,
`docs/procedure-deploiement.md`, `CHANGELOG.md`, `scripts/sauvegarde.sh`,
historique Git.

Vérifiez vous-même :

- un camarade suivant uniquement `docs/procedure-deploiement.md` peut
  démarrer l'application ;
- `git log --oneline --graph` montre une branche fusionnée et des messages
  compréhensibles ; `git status` est propre ;
- `bash scripts/sauvegarde.sh` produit un fichier horodaté et
  `pg_restore --list` le lit sans erreur.

## Livrable attendu

**Dossier technique individuel**, comprenant :

1. le dépôt Git individuel (historique complet, branche principale à jour,
   tags) ;
2. l'application fonctionnelle dans votre environnement de test : la
   procédure de déploiement doit permettre au jury de la relancer ;
3. dans le dépôt : le schéma de données, le plan de recette et ses
   résultats, les fiches d'anomalie, le script de sauvegarde, la matrice des
   rôles et droits, la documentation technique et la procédure de
   déploiement, le CHANGELOG ;
4. le support de soutenance (PDF, 8 à 12 diapositives), déposé avec le
   dossier.

### Modalités de dépôt

Le dépôt a lieu le **lundi 12/10/2026 au plus tard à 15:30**, sur l'espace
de rendu indiqué par le formateur référent, sous deux formes conjointes :

- **(a)** le lien vers votre dépôt Git individuel, créé depuis le squelette
  fourni, avec l'historique complet poussé ;
- **(b)** une archive zip du projet **incluant le dossier `.git/`** (hors
  environnement virtuel), nommée `veloville-<nom>-<prenom>.zip`, accompagnée
  de l'empreinte du dernier commit (`git rev-parse HEAD`), recopiée dans le
  message ou le formulaire de dépôt. Le support de soutenance est joint à
  l'archive ou déposé à côté.

Les deux formes doivent correspondre : l'empreinte annoncée est celle de la
tête de la branche principale, dans le dépôt distant comme dans l'archive.

**Vérification de réception.** Entre 15:30 et 18:00, le formateur vérifie
que chaque dépôt démarre en suivant votre procédure : clone, schéma, import,
tests, API, front. À titre d'information, cette réception comporte onze
vérifications automatisables ; elles ne constituent pas un critère de
notation, mais un dossier qui ne les passe pas ne pourra pas être démontré :

1. le dépôt se clone ;
2. `.env.example` est présent, et aucun fichier `.env` ni aucun secret ne
   figure dans l'historique ;
3. les dépendances de `requirements.txt` s'installent ;
4. `sql/schema.sql` s'exécute ;
5. `scripts/importer.py` s'exécute deux fois sans erreur ;
6. `pytest` s'exécute et affiche la couverture ;
7. `uvicorn api.main:app` démarre et `GET /sante` répond ;
8. le login fonctionne, puis une route protégée renvoie 401 sans jeton et
   le PUT renvoie 403 pour le rôle direction ;
9. le front Streamlit démarre ;
10. la documentation attendue est présente (README, `docs/`, CHANGELOG) ;
11. `scripts/sauvegarde.sh` est syntaxiquement valide (`bash -n`).

**Correctif de démarrage.** Si la vérification révèle que l'application ne
démarre pas (dépendance manquante, variable d'environnement non documentée,
fichier oublié), vous êtes prévenu(e) et disposez d'une fenêtre **jusqu'au
12/10 à 17:30** pour pousser **un seul correctif de démarrage**, puis
transmettre la nouvelle empreinte. Ce correctif ne peut pas ajouter de
fonctionnalité ni modifier la documentation au-delà du strict nécessaire.
Au-delà de 17:30, le dépôt est figé tel quel et sert de base à la
soutenance.

### Démonstration en soutenance

Vous présentez et démontrez votre application sur votre poste, API et base
démarrées à l'avance. Plan attendu, 20 minutes :

1. **Contexte et périmètre** (2 min) : besoin, architecture retenue,
   ce qui est livré et ce qui ne l'est pas.
2. **Démonstration** (12 min), dans cet ordre : audit et import des données
   (journal des rejets, idempotence) ; connexion avec les deux comptes et
   différence de droits (un 403 montré) ; les quatre écrans du front ;
   un indicateur rapproché d'une requête SQL de contrôle ; exécution des
   tests et affichage de la couverture ; exécution de la sauvegarde.
3. **Choix techniques et qualité** (4 min) : structure du code, tests,
   sécurité, écoconception, historique Git, recette et corrections.
4. **Limites et axes d'amélioration** (2 min).

Le jury dispose ensuite de 10 minutes de questions ; il peut vous demander
d'exécuter une commande, de montrer un fichier ou d'expliquer un extrait de
code.

## Évaluation

Évaluation individuelle par le jury sur la grille d'évaluation Skolae du
bloc 2 (note sur 20). Critères : respect des standards de conception ;
adéquation des technologies retenues ; couverture et pertinence des tests ;
correction des bugs ; conformité aux spécifications, aux règles
d'accessibilité et d'écoconception ; qualité du versioning et de la
documentation.

Le dossier déposé le 12/10 et la démonstration des 13-14/10 sont évalués
ensemble. Un dossier dont l'application ne démarre pas selon sa propre
procédure de déploiement ne peut pas être démontré : vérifiez-la avant le
dépôt.

## Conseils

- **Priorisez.** Le schéma, l'import fiabilisé et l'API avant le front ;
  un front sobre qui fonctionne vaut mieux qu'un front soigné sur une API
  incomplète. Ne commencez pas par la mise en forme.
- **Testez au fil de l'eau**, pas le second jour en fin d'après-midi : une
  fonction de fiabilisation s'écrit avec son test ; une route s'écrit avec
  son appel `TestClient`.
- **Commitez souvent**, à chaque étape qui fonctionne, avec un message qui
  dit ce que le commit apporte. L'historique fait partie du livrable.
- **Ne laissez jamais un secret dans Git** : vérifiez `.gitignore` avant le
  premier commit, et relisez `git status` avant chaque `git add`. Un secret
  (mot de passe de base, clé JWT) présent à n'importe quel endroit de
  l'historique, **même supprimé par un commit ultérieur**, reste lisible
  dans `git log -p` et est considéré comme une faute de sécurité majeure.
  En cas d'erreur, la seule issue est de changer le secret et de réécrire
  l'historique avant de pousser.
- **Lisez le plan de recette dès le premier jour** : il dit précisément ce
  qui sera vérifié.
- Gardez une trace de ce que vous n'avez pas eu le temps de faire : c'est la
  matière de la section « Limites et axes d'amélioration », attendue et
  valorisée.
