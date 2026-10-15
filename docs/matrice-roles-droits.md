# Matrice rôles x droits

Une ligne par route, une colonne par rôle (anonyme, exploitant,
direction), code HTTP attendu en cas de refus.

Ce document définit les règles d'accès aux différents endpoints de l'API REST FastAPI de l'application VéloVille.

| En-point / Route | Méthode | Rôle Anonyme | Rôle Exploitant (`exploitant01`) | Rôle Direction (`direction01`) | Code HTTP si refus |
|---|---|---|---|---|---|
| `/sante` | `GET` | **Autorisé (200)** | **Autorisé (200)** | **Autorisé (200)** | N/A |
| `/auth/login` | `POST` | **Autorisé (200)** | **Autorisé (200)** | **Autorisé (200)** | `401 Unauthorized` |
| `/stations` | `GET` | Refusé | **Autorisé (200)** | **Autorisé (200)** | `401 Unauthorized` |
| `/stations/{station_id}` | `GET` | Refusé | **Autorisé (200)** | **Autorisé (200)** | `401 Unauthorized` / `404 Not Found` |
| `/trajets` | `GET` | Refusé | **Autorisé (200)** | **Autorisé (200)** | `401 Unauthorized` |
| `/incidents` | `GET` | Refusé | **Autorisé (200)** | **Autorisé (200)** | `401 Unauthorized` |
| `/incidents/{incident_id}/statut` | `PUT` | Refusé | **Autorisé (200)** | **Refusé (403)** | `403 Forbidden` / `401 Unauthorized` |
| `/indicateurs/activite-par-jour` | `GET` | Refusé | **Autorisé (200)** | **Autorisé (200)** | `401 Unauthorized` |

### Remarques :
- Le contrôle d'accès repose sur un jeton **JWT Bearer** à transmettre dans l'en-tête `Authorization`.
- Le rôle `direction` possède un accès en lecture sur l'ensemble du réseau et des indicateurs, mais ne peut pas modifier le statut des incidents d'exploitation (`HTTP 403`).