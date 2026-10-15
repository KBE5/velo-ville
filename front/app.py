"""Page d'accueil Streamlit : connexion.

À compléter : formulaire identifiant / mot de passe, appel de POST /auth/login via
api_client, stockage du jeton et du rôle dans st.session_state,
message d'erreur en français en cas d'échec.

Lancement : streamlit run front/app.py
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import api_client
import commun

st.set_page_config(
    page_title="VéloVille - Connexion",
    page_icon="🚲",
    layout="centered",
)

st.title("VéloVille — Plateforme de restitution")

# Afficher le message de succès et la consigne (si user connecté)
if commun.est_connecte():
    commun.barre_laterale()

    st.success(
        f"Connecté en tant que **{st.session_state['username']}** "
        f"(rôle : **{st.session_state['role']}**)."
    )
    
    st.write("Utilisez le menu latéral pour accéder aux écrans.")

    st.stop()

st.header("Connexion")

# st.form évite de relancer le script à chaque frappe dans les champs
with st.form("login_form"):
    username = st.text_input("Identifiant", autocomplete="username")
    password = st.text_input("Mot de passe", type="password", autocomplete="current-password")
    envoyer = st.form_submit_button("Se connecter")

if envoyer:
    if not username or not password:
        st.error("Veuillez renseigner l'identifiant et le mot de passe.")
    else:
        try:
            # Appel de la fonction de connexion centralisée dans api_client
            response = api_client.connexion(username, password)
        except api_client.ErreurApi as error:
            if error.status_code == 401:
                st.error("Identifiant ou mot de passe incorrect.")
            else:
                st.error(error.message)
        else:
            # Stockage sécurisé du jeton et du rôle dans la session Streamlit
            st.session_state["access_token"] = response["access_token"]
            st.session_state["role"] = response["role"]
            st.session_state["username"] = username

            # Relance la page pour basculer vers l'état connecté
            st.rerun()