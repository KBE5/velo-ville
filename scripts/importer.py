"""Import et fiabilisation des trois exports CSV dans PostgreSQL.

Lire data/stations.csv, data/trajets.csv et data/incidents.csv,
appliquer les règles de fiabilisation (api/services/fiabilisation.py),
charger les lignes valides, journaliser les rejets et les avertissements.
Le script doit être idempotent : deux exécutions successives laissent la
base dans le même état.

Usage prévu : python scripts/importer.py [--dossier data]
"""

from api.database import engine
from pathlib import Path
import pandas as pd

from api.services.fiabilisation import (valider_station, valider_trajet, valider_incident)

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
    #option "records" transforme le tableau en une liste de dictionnaires
    stations_lignes = pd.read_csv(FICHIER_STATIONS).to_dict(orient="records")
    trajets_lignes = pd.read_csv(FICHIER_TRAJETS).to_dict(orient="records")
    incidents_lignes = pd.read_csv(FICHIER_INCIDENTS).to_dict(orient="records")


    # ======Traiter les stations=======
    stations_valides = []
    stations_valides_ids = set()

    for idx, ligne in enumerate(stations_lignes): #Enumerate(affiche les éléments d'une liste en leur attribuant un index)
        station_id = str(ligne["station_id"]).strip() if pd.notna(ligne["station_id"]) else f"ligne_{idx}"

        try:
            valider_station(ligne)
            stations_valides.append(ligne)
            stations_valides_ids.add(station_id)
        except ValueError as e:
            logs_rejets.append({
                "fichier_source": "stations.csv",
                "id_entite": station_id,
                "code_regle": "RG1",
                "motif": str(e),
                "decision": "REJET"
            })

    # ======Traiter les trajets=======
    trajets_valides = []
    trajets_vus = set()#mémoriser ID 

    for idx, ligne in enumerate(trajets_lignes):
        id_trajet = str(ligne["trajet_id"]).strip() if "trajet_id" in ligne and pd.notna(ligne["trajet_id"]) else f"ligne_{idx}"

        try:
            # transmettre l'ensemble des trajets 
            valider_trajet(ligne, stations_valides=stations_valides_ids, trajets_deja_vus=trajets_vus)
            trajets_valides.append(ligne)
        except ValueError as e:
            logs_rejets.append({
                "fichier_source": "trajets.csv",
                "id_entite": id_trajet,
                "code_regle": "RG2/RG4/DOUBLON",
                "motif": str(e),
                "decision": "REJET"
            })

    # ======Traiter un incident=======
    
    incidents_valides = []

    for idx, ligne in enumerate(incidents_lignes):
        id_incident = str(ligne["incident_id"]).strip() if "incident_id" in ligne and pd.notna(ligne["incident_id"]) else f"ligne_{idx}"
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

    # ====== Préparer les DF propres et conversion des types ======
    
    df_stations = pd.DataFrame(stations_valides)
    if "date_mise_en_service" in df_stations.columns:
        df_stations["date_mise_en_service"] = pd.to_datetime(
            df_stations["date_mise_en_service"], errors="coerce").dt.date

    df_trajets = pd.DataFrame(trajets_valides)
    if "depart_horodatage" in df_trajets.columns:
        df_trajets["depart_horodatage"] = pd.to_datetime(
            df_trajets["depart_horodatage"], errors="coerce")

    df_incidents = pd.DataFrame(incidents_valides)
    for col_date in ["date_signalement", "date_resolution"]:
        if col_date in df_incidents.columns:
            df_incidents[col_date] = pd.to_datetime(
                df_incidents[col_date], errors="coerce")

    # ======Export des fichiers propre dans data/ et des journaux dans docs/=======

    Path("data").mkdir(parents=True, exist_ok=True)
    Path("docs").mkdir(parents=True, exist_ok=True)

    pd.DataFrame(stations_valides).to_csv(SORTIE_STATIONS, index=False, encoding="utf-8")
    pd.DataFrame(trajets_valides).to_csv(SORTIE_TRAJETS, index=False, encoding="utf-8")
    pd.DataFrame(incidents_valides).to_csv(SORTIE_INCIDENTS, index=False, encoding="utf-8")

    pd.DataFrame(logs_rejets).to_csv(SORTIE_REJETS, index=False, encoding="utf-8")
    pd.DataFrame(logs_avertissements).to_csv(SORTIE_AVERTISSEMENTS, index=False, encoding="utf-8")

    # ======Export des fichiers propre dans data/ et des journaux dans docs/=======
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("docs").mkdir(parents=True, exist_ok=True)

    pd.DataFrame(stations_valides).to_csv(SORTIE_STATIONS, index=False, encoding="utf-8")
    pd.DataFrame(trajets_valides).to_csv(SORTIE_TRAJETS, index=False, encoding="utf-8")
    pd.DataFrame(incidents_valides).to_csv(SORTIE_INCIDENTS, index=False, encoding="utf-8")

    pd.DataFrame(logs_rejets).to_csv(SORTIE_REJETS, index=False, encoding="utf-8")
    pd.DataFrame(logs_avertissements).to_csv(SORTIE_AVERTISSEMENTS, index=False, encoding="utf-8")

    # ====== Charger dans la BDD "veloville" ======
    
    with engine.begin() as connection:
        # Nettoyer >> idempotence (ordre inverse des clés étrangères)
        connection.exec_driver_sql("TRUNCATE TABLE incident, trajet, station CASCADE;")

    # Corriger la date pour les stations
    df_stations = pd.DataFrame(stations_valides)
    if "date_mise_en_service" in df_stations.columns:
        df_stations["date_mise_en_service"] = pd.to_datetime(
            df_stations["date_mise_en_service"], errors="coerce").dt.date

    df_stations.to_sql("station", con=engine, if_exists="append", index=False)

    # Corriger le timestamp pour les trajets
    df_trajets = pd.DataFrame(trajets_valides)
    if "depart_horodatage" in df_trajets.columns:
        df_trajets["depart_horodatage"] = pd.to_datetime(
            df_trajets["depart_horodatage"], errors="coerce")

    df_trajets.to_sql("trajet", con=engine, if_exists="append", index=False)

    # 3. Incidents
    df_incidents = pd.DataFrame(incidents_valides)
    for col_date in ["date_signalement", "date_resolution"]:
        if col_date in df_incidents.columns:
            df_incidents[col_date] = pd.to_datetime(
                df_incidents[col_date], errors="coerce")
                
    df_incidents.to_sql("incident", con=engine, if_exists="append", index=False)


    print("\n=== Bilan final  ===")
    print(f"Stations   : {len(stations_lignes)} -> {len(stations_valides)} conservées")
    print(f"Trajets    : {len(trajets_lignes)} -> {len(trajets_valides)} conservés")
    print(f"Incidents  : {len(incidents_lignes)} -> {len(incidents_valides)} conservés")
    print(f"Rejets enregistrés       : {len(logs_rejets)} -> {SORTIE_REJETS}")
    print(f"Avertissements produits : {len(logs_avertissements)} -> {SORTIE_AVERTISSEMENTS}")


if __name__ == "__main__":
    main()
