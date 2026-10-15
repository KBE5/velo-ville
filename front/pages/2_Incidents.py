"""Écran Incidents.

Tableau filtrable par statut ; pour le rôle exploitant, changement de
statut d'un incident via l'API.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import api_client
import commun

st.set_page_config(page_title="VéloVille - Incidents", layout="wide")

commun.exiger_connexion()
commun.barre_laterale()

st.title("Incidents")

if "incident_page" not in st.session_state:
    st.session_state["incident_page"] = 1

# Filtres haut de page
col_f1, col_f2, col_f3 = st.columns([2, 2, 1])

with col_f1:
    statuts_map = {"Tous": "", "ouvert": "ouvert", "en_cours": "en_cours", "resolu": "resolu"}
    statut_choisi = st.selectbox("Statut", list(statuts_map.keys()))

with col_f2:
    taille_page = st.selectbox("Taille de page", [10, 20, 50], index=1)

# Construction des paramètres pour l'appel API
params = {
    "page": st.session_state["incident_page"],
    "taille_page": taille_page
}
if statut_choisi != "Tous":
    params["statut"] = statuts_map[statut_choisi]

try:
    with st.spinner("Chargement..."):
        data = api_client.obtenir("/incidents", params=params)
except api_client.ErreurApi as error:
    st.error(error.message)
    st.stop()

# Extraction des résultats et du total renvoyés par l'API
incidents_list = data.get("resultats", [])
total_lignes = data.get("total", 0)

st.caption(f"{total_lignes} incidents au total")

if not incidents_list:
    st.info("Aucun résultat pour ces critères.")
else:
    total_pages = max(1, (total_lignes - 1) // taille_page + 1)

    if st.session_state["incident_page"] > total_pages:
        st.session_state["incident_page"] = 1
        st.rerun()

    with col_f3:
        st.session_state["incident_page"] = st.number_input(
            "Page",
            min_value=1,
            max_value=total_pages,
            value=st.session_state["incident_page"],
            step=1
        )

    df_page = pd.DataFrame(incidents_list)

    # En-têtes de colonnes exacts conformes à la maquette
    rename_map = {
        "incident_id": "Identifiant",
        "date_signalement": "Signalé le",
        "cible": "Cible",
        "velo_id": "Vélo",
        "station_id": "Station",
        "type_incident": "Type",
        "statut": "Statut",
        "date_resolution": "Résolu le",
        "technicien": "Technicien"
    }
    
    # S'assurer que toutes les colonnes requises existent dans le DataFrame
    df_page = df_page.rename(columns={k: v for k, v in rename_map.items() if k in df_page.columns})
    
    # Filtrage des colonnes dans l'ordre de la maquette si elles sont présentes
    if "Identifiant" in df_page.columns:
        colonnes_affichees = [c for c in ["Identifiant", "Signalé le", "Cible", "Vélo", "Station", "Type", "Statut", "Résolu le", "Technicien"] if c in df_page.columns]
        df_page = df_page[colonnes_affichees]

    st.dataframe(df_page, width="stretch", hide_index=True)
    st.caption(f"Page {st.session_state['incident_page']} sur {total_pages}")

    st.markdown("---")

    # Gestion de la section de modification selon le rôle
    role_actuel = st.session_state.get("role")
    if role_actuel == "exploitant":
        st.subheader("Changer le statut d'un incident")

        with st.form("update_incident_form"):
            col_id_1, col_id_2 = st.columns(2)
            with col_id_1:
                incident_id = st.text_input("Incident (ID)")
            with col_id_2:
                nouveau_statut = st.selectbox("Nouveau statut", ["en_cours", "resolu"])
            
            submitted = st.form_submit_button("Appliquer")

        if submitted:
            if not incident_id:
                st.error("Veuillez renseigner l'identifiant de l'incident.")
            else:
                try:
                    api_client.modifier(
                        f"/incidents/{incident_id}/statut",
                        json={"statut": nouveau_statut}
                    )
                except api_client.ErreurApi as error:
                    if error.status_code == 422:
                        st.error("Transition de statut non autorisée.")
                    elif error.status_code == 404:
                        st.error("Incident introuvable.")
                    elif error.status_code == 403:
                        st.error("Vous n'avez pas le droit de modifier un incident.")
                    else:
                        st.error(error.message)
                else:
                    st.success(f"Statut de l'incident {incident_id} mis à jour : {nouveau_statut}.")
                    # On retire st.rerun() pour laisser le message s'afficher à l'écran
    else:
        st.write("Vous n'avez pas le droit de modifier un incident.") # Conforme au message de la maquette pour la direction