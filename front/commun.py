"""Fonctions Streamlit partagées entre les pages."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from streamlit.errors import StreamlitAPIException

SESSION_KEYS = (
    "access_token",
    "role",
    "username",
)


def est_connecte() -> bool:
    """Indique simplement si un JWT est stocké en session"""
    return bool(st.session_state.get("access_token"))


def deconnecter() -> None:
    """Supprime toutes les informations de connexion"""
    for key in SESSION_KEYS:
        st.session_state.pop(key, None)


def exiger_connexion() -> None:
    """Bloque une page Streamlit si aucun JWT n'est présent"""
    if est_connecte():
        return

    st.warning("Veuillez vous connecter")

    try:
        st.page_link(
            "app.py",
            label="Aller à la connexion",
        )
    except StreamlitAPIException:
        pass

    st.stop()


def barre_laterale() -> None:
    """Affiche l'utilisateur courant et le bouton de déconnexion"""
    with st.sidebar:
        st.markdown(
            f"Utilisateur : **{st.session_state.get('username', '')}**"
        )
        st.markdown(
            f"Rôle : **{st.session_state.get('role', '')}**"
        )

        if st.button("Se déconnecter"):
            deconnecter()

            try:
                st.switch_page("app.py")
            except StreamlitAPIException:
                st.rerun()