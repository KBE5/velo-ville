"""Écran Indicateurs.

Trois st.metric et trois tableaux issus des trois endpoints
/indicateurs:
- GET /indicateurs/activite-par-jour
- GET /indicateurs/stations-actives
- GET /indicateurs/incidents-par-statut
Aucun graphique.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import date
import streamlit as st
import pandas as pd
import api_client
import commun

st.set_page_config(page_title="VéloVille - Indicateurs", layout="wide")

commun.exiger_connexion()
commun.barre_laterale()

st.title("Indicateurs et Tableaux de Bord")

# 1. Filtres haut de page (Période et Nombre de stations)
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    date_debut = st.date_input("Date de début", value=date(2026, 8, 24))
with col2:
    date_fin = st.date_input("Date de fin", value=date(2026, 8, 30))
with col3:
    limite_stations = st.number_input("Stations", min_value=1, max_value=50, value=10, step=1)

if st.button("Actualiser"):
    st.rerun()

st.markdown("---")

# 2. Appels API pour récupérer les indicateurs
try:
    with st.spinner("Chargement des indicateurs..."):
        res_activite = api_client.obtenir(
            "/indicateurs/activite-par-jour",
            params={"date_debut": date_debut.isoformat(), "date_fin": date_fin.isoformat()}
        )
        res_stations = api_client.obtenir(
            "/indicateurs/stations-actives",
            params={"limite": limite_stations}
        )
        res_incidents = api_client.obtenir("/indicateurs/incidents-par-statut")
except api_client.ErreurApi as error:
    st.error(error.message)
    st.stop()

# Traitement sécurisé des données d'activité (liste directe ou dictionnaire)
activite_list = res_activite if isinstance(res_activite, list) else res_activite.get("resultats", res_activite.get("donnees", []))
df_activite = pd.DataFrame(activite_list)

total_trajets = int(df_activite["nb_trajets"].sum()) if not df_activite.empty and "nb_trajets" in df_activite.columns else 0

stations_list = res_stations if isinstance(res_stations, list) else res_stations.get("resultats", res_stations.get("donnees", []))
df_stations = pd.DataFrame(stations_list)
nb_stations_actives = len(df_stations)

delai_moyen = "n. d."
if isinstance(res_incidents, dict) and "delai_moyen_resolution_heures" in res_incidents:
    val_delai = res_incidents["delai_moyen_resolution_heures"]
    delai_moyen = f"{val_delai:.1f}" if val_delai is not None else "n. d."

# Affichage des métriques de la maquette[cite: 6]
m1, m2, m3 = st.columns(3)
m1.metric("Trajets sur la période", total_trajets)
m2.metric("Stations actives", nb_stations_actives)
m3.metric("Délai moyen de résolution (h)", delai_moyen)

st.markdown("---")

# 3. Tableaux et rendus
st.subheader("Activité par jour")
if not df_activite.empty:
    rename_activite = {"jour": "Jour", "nb_trajets": "Nombre de trajets"}
    df_activite = df_activite.rename(columns={k: v for k, v in rename_activite.items() if k in df_activite.columns})
    st.dataframe(df_activite, width="stretch", hide_index=True)
else:
    st.info("Aucune donnée d'activité pour cette période.")

st.subheader("Stations les plus actives")
if not df_stations.empty:
    if "nb_departs" in df_stations.columns and "nb_arrivees" in df_stations.columns:
        df_stations["Total"] = df_stations["nb_departs"] + df_stations["nb_arrivees"]
    
    rename_stations = {
        "station_id": "Identifiant",
        "nom": "Nom",
        "nb_departs": "Départs",
        "nb_arrivees": "Arrivées"
    }
    df_stations = df_stations.rename(columns={k: v for k, v in rename_stations.items() if k in df_stations.columns})
    st.dataframe(df_stations, width="stretch", hide_index=True)
else:
    st.info("Aucune station active trouvée.")

st.subheader("Incidents par statut")
incidents_list = res_incidents if isinstance(res_incidents, list) else res_incidents.get("resultats", res_incidents.get("donnees", []))
df_incidents_statut = pd.DataFrame(incidents_list)
if not df_incidents_statut.empty:
    rename_incidents = {"statut": "Statut", "nombre": "Nombre d'incidents", "nb_incidents": "Nombre d'incidents"}
    df_incidents_statut = df_incidents_statut.rename(columns={k: v for k, v in rename_incidents.items() if k in df_incidents_statut.columns})
    st.dataframe(df_incidents_statut, width="stretch", hide_index=True)
else:
    st.info("Aucune donnée d'incidents par statut.")