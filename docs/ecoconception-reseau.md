# Stratégie d'Optimisation Réseau et Sobriété Numérique

Dans le cadre de l'éco-conception de l'application **Vélo-Ville**, des choix architecturaux stricts ont été réalisés pour limiter l'empreinte environnementale, réduire la bande passante réseau et optimiser la consommation des serveurs.

## 1. Pagination des flux de données
Afin d'éviter le transfert massif et inutile de données sur le réseau (bande passante superflue) et d'alléger le rendu côté client :
* **Limitation des charges utiles (Payloads) :** Les API ne renvoient jamais l'intégralité d'une table en une seule fois. Les listes volumineuses (trajets, stations, incidents) utilisent systématiquement un mécanisme de **pagination** (paramètres `limit` et `offset`, ou curseurs).
* **Affichage ciblé :** Seul le strict nécessaire est transmis à l'interface utilisateur pour un instant $T$, réduisant l'utilisation de la mémoire vive (RAM) sur les postes des utilisateurs et sur les appareils mobiles des agents de terrain.

## 2. Synchronisation et requêtes à la demande (Pas de temps réel permanent)
Pour éliminer la charge CPU et réseau inutile liée au polling (rafraîchissement automatique en continu) :
* **Pas de rafraîchissement en temps réel en arrière-plan :** Aucune connexion permanente de type WebSocket ou de requêtes périodiques agressives n'est maintenue pour écouter la base de données en direct.
* **Chargement à la demande (On-demand) :** Les données sont rafraîchies uniquement lorsque l'utilisateur effectue une action explicite (clic sur un bouton de rechargement, application d'un filtre ou soumission de formulaire). 
* **Mise en cache intelligente :** Les référentiels peu modifiés (comme la liste des stations) bénéficient d'un cache local pour éviter les allers-retours répétés vers la base de données PostgreSQL.

## 3. Bénéfices écologiques et techniques
* **Sobriété réseau :** Réduction sensible du trafic de données sur les réseaux mobiles et filaires.
* **Économie d'énergie serveur :** Diminution des requêtes concurrentes en base de données, ce qui réduit la sollicitation du processeur (CPU) du serveur et limite son échauffement.
* **Durabilité des équipements :** Moins de charge réseau et de calculs superflus signifie une usure moindre des infrastructures matérielles (routeurs, serveurs, terminaux utilisateurs).