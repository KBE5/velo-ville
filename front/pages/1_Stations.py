"""Écran Stations.

Tableau des stations filtrable par commune, pagination.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import api_client
import commun

st.set_page_config(page_title="VéloVille - Stations", layout="wide")

commun.exiger_connexion()
commun.barre_laterale()

st.title("Stations")

# Initialisation de la page dans la session si absente
if "station_page" not in st.session_state:
    st.session_state["station_page"] = 1

# Récupération de la liste complète pour alimenter dynamiquement le filtre des communes
try:
    data_all = api_client.obtenir("/stations", params={"taille_page": 100})
    stations_all = data_all.get("resultats", []) if isinstance(data_all, dict) else data_all
    df_all = pd.DataFrame(stations_all)
    
    communes = ["Toutes"]
    if not df_all.empty and "commune" in df_all.columns:
        communes += sorted(df_all["commune"].dropna().unique().tolist())
except api_client.ErreurApi:
    communes = ["Toutes"]

# Organisation en haut : Commune, Taille de page et Page (number_input)
col_f1, col_f2, col_f3 = st.columns([2, 1, 1])

with col_f1:
    commune_choisie = st.selectbox("Commune", communes)

with col_f2:
    taille_page = st.number_input(
        "Taille de page",
        min_value=1,
        max_value=100,
        value=20,
        step=1
    )

# Réinitialisation de la page à 1 si on change de filtre de commune
if "derniere_commune" not in st.session_state:
    st.session_state["derniere_commune"] = commune_choisie
elif st.session_state["derniere_commune"] != commune_choisie:
    st.session_state["derniere_commune"] = commune_choisie
    st.session_state["station_page"] = 1

# Construction propre des paramètres API
params = {
    "page": st.session_state["station_page"],
    "taille_page": int(taille_page)
}
if commune_choisie != "Toutes":
    params["commune"] = commune_choisie

try:
    with st.spinner("Chargement des stations..."):
        response_api = api_client.obtenir("/stations", params=params)
except api_client.ErreurApi as error:
    st.error(error.message)
    st.stop()

# Extraction sécurisée des données paginées
if isinstance(response_api, dict):
    stations = response_api.get("resultats", [])
    total_lignes = response_api.get("total", len(stations))
    total_pages = max(1, (total_lignes - 1) // int(taille_page) + 1)
else:
    stations = response_api
    total_lignes = len(stations)
    total_pages = max(1, (total_lignes - 1) // int(taille_page) + 1)

# S'assurer que la page courante ne dépasse pas le nombre total de pages
if st.session_state["station_page"] > total_pages:
    st.session_state["station_page"] = 1

with col_f3:
    st.session_state["station_page"] = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=st.session_state["station_page"],
        step=1
    )

# Affichage du total des stations
st.caption(f"{total_lignes} stations au total")

if not stations:
    st.info("Aucun résultat pour ces critères.")
else:
    df_page = pd.DataFrame(stations)

    # Suppression explicite des colonnes latitude et longitude si elles sont présentes
    for col_a_retirer in ["latitude", "longitude"]:
        if col_a_retirer in df_page.columns:
            df_page = df_page.drop(columns=[col_a_retirer])

    # Renommage des colonnes en français lisible (avec station_id -> Identifiant)
    rename_map = {
        "station_id": "Identifiant",
        "id_station": "Identifiant",
        "id": "Identifiant",
        "nom": "Nom",
        "commune": "Commune",
        "capacite": "Capacité",
        "date_mise_en_service": "Mise en service"
    }
    df_page = df_page.rename(columns={k: v for k, v in rename_map.items() if k in df_page.columns})

    # Restitution tabulaire propre
    st.dataframe(df_page, width="stretch", hide_index=True)
    st.caption(f"Page {st.session_state['station_page']} sur {total_pages}")