"""Import et fiabilisation des trois exports CSV dans PostgreSQL.

Lire data/stations.csv, data/trajets.csv et data/incidents.csv,
appliquer les règles de fiabilisation (api/services/fiabilisation.py),
charger les lignes valides, journaliser les rejets et les avertissements.
Le script doit être idempotent : deux exécutions successives laissent la
base dans le même état.

Usage prévu : python scripts/importer.py [--dossier data]
"""


from pathlib import Path
import pandas as pd

# Importation des fonctions pures de fiabilisation
from api.services.fiabilisation import (
    valider_station,
    valider_trajet,
    valider_incident,
)

FICHIER_STATIONS = "data/stations.csv"
FICHIER_TRAJETS = "data/trajets.csv"
FICHIER_INCIDENTS = "data/incidents.csv"

SORTIE_STATIONS = "data/stations_propre.csv"
SORTIE_TRAJETS = "data/trajets_propre.csv"
SORTIE_INCIDENTS = "data/incidents_propre.csv"

SORTIE_REJETS = "docs/journal-rejets.csv"
SORTIE_AVERTISSEMENTS = "docs/journal-avertissements.csv"


def main() -> None:
    """Fais la lecture, la fiabilisation et l'exportation des données."""
    
    # Remise à zéro des journaux d'audit (garantit l'idempotence)
    logs_rejets = []
    logs_avertissements = []

    # Charger des fichier bruts 
    #"records" transforme le tableau en une liste de dictionnaires
    stations_lignes = pd.read_csv(FICHIER_STATIONS).to_dict(orient="records")
    trajets_lignes = pd.read_csv(FICHIER_TRAJETS).to_dict(orient="records")
    incidents_lignes = pd.read_csv(FICHIER_INCIDENTS).to_dict(orient="records")


    # ======Traiter les stations=======
    stations_valides = []
    stations_valides_ids = set()

    for idx, ligne in enumerate(stations_lignes): #Enumerate(affiche les éléments d'une liste en leur attribuant un index)
        id_station = str(ligne["station_id"]).strip() if pd.notna(ligne["station_id"]) else f"ligne_{idx}"

        try:
            valider_station(ligne)
            stations_valides.append(ligne)
            stations_valides_ids.add(id_station)
        except ValueError as e:
            logs_rejets.append({
                "fichier_source": "stations.csv",
                "id_entite": id_station,
                "code_regle": "RG1",
                "motif": str(e),
                "decision": "REJET"
            })

    # ======Traiter les trajets=======
    trajets_valides = []

    for idx, ligne in enumerate(trajets_lignes):
        id_trajet = ligne["id_trajet"] if "id_trajet" in ligne and pd.notna(ligne["id_trajet"]) else f"ligne_{idx}"

        try:
            valider_trajet(ligne, stations_valides=stations_valides_ids)
            trajets_valides.append(ligne)
        except ValueError as e:
            logs_rejets.append({
                "fichier_source": "trajets.csv",
                "id_entite": id_trajet,
                "code_regle": "RG2/RG4",
                "motif": str(e),
                "decision": "REJET"
            })

    # ======Traiter un incident=======
    
    incidents_valides = []

    for idx, ligne in enumerate(incidents_lignes):
        id_incident = ligne["id_incident"] if "id_incident" in ligne and pd.notna(ligne["id_incident"]) else f"ligne_{idx}"
        statut_brut = str(ligne["statut"]) if pd.notna(ligne["statut"]) else ""

        try:
            #vérifier que l'incident est valide (la station existe bien)
            statut_normalise = valider_incident(ligne, stations_valides=stations_valides_ids)

            # comparer le statut d'origine brut avec le statut nettoyé
            if statut_brut != statut_normalise and statut_brut.strip() != "":
                logs_avertissements.append({
                    "fichier_source": "incidents.csv",
                    "id_entite": id_incident,
                    "colonne_concernee": "statut",
                    "valeur_brute": statut_brut,
                    "valeur_corrigee": statut_normalise,
                    "motif": "Normalisation de la casse et du format"
                })

            ligne["statut"] = statut_normalise
            incidents_valides.append(ligne)

        except ValueError as e:
            logs_rejets.append({
                "fichier_source": "incidents.csv",
                "id_entite": id_incident,
                "code_regle": "RG6/RG7/RG8",
                "motif": str(e),
                "decision": "REJET"
            })

    # ======Export des fichiers propre dans data/ et des journaux dans docs/=======

    Path("data").mkdir(parents=True, exist_ok=True)
    Path("docs").mkdir(parents=True, exist_ok=True)

    pd.DataFrame(stations_valides).to_csv(SORTIE_STATIONS, index=False, encoding="utf-8")
    pd.DataFrame(trajets_valides).to_csv(SORTIE_TRAJETS, index=False, encoding="utf-8")
    pd.DataFrame(incidents_valides).to_csv(SORTIE_INCIDENTS, index=False, encoding="utf-8")

    pd.DataFrame(logs_rejets).to_csv(SORTIE_REJETS, index=False, encoding="utf-8")
    pd.DataFrame(logs_avertissements).to_csv(SORTIE_AVERTISSEMENTS, index=False, encoding="utf-8")

    print("\n=== Bilan d'importation et de fiabilisation ===")
    print(f"Stations   : {len(stations_lignes)} -> {len(stations_valides)} conservées")
    print(f"Trajets    : {len(trajets_lignes)} -> {len(trajets_valides)} conservés")
    print(f"Incidents  : {len(incidents_lignes)} -> {len(incidents_valides)} conservés")
    print(f"Rejets enregistrés       : {len(logs_rejets)} -> {SORTIE_REJETS}")
    print(f"Avertissements produits : {len(logs_avertissements)} -> {SORTIE_AVERTISSEMENTS}")


if __name__ == "__main__":
    main()
