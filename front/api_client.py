"""Client HTTP centralisé vers l'API VéloVille.

Lire API_URL et API_TIMEOUT_SECONDES, ajouter l'en-tête
Authorization: Bearer <jeton>, lever ErreurApi (message en français)
sur erreur réseau, délai dépassé ou code HTTP d'erreur.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import requests
import streamlit as st
from api.config import API_URL, API_TIMEOUT_SECONDES


class ErreurApi(Exception):
    """Erreur simplifiée présentée aux pages Streamlit"""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _api_url() -> str:
    """Retourne l'adresse de FastAPI définie dans .env"""
    return os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


def _timeout() -> float:
    """Retourne le délai maximal autorisé pour un appel HTTP"""
    return float(os.getenv("API_TIMEOUT_SECONDES", "5"))


def _headers() -> dict[str, str]:
    """Ajoute automatiquement le JWT s'il existe dans la session."""
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def appeler(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    json: dict | None = None,
) -> dict | list:
    """Exécute un appel HTTP vers FastAPI."""
    try:
        response = requests.request(
            method=method,
            url=f"{_api_url()}{path}",
            params=params,
            json=json,
            headers=_headers(),
            timeout=_timeout(),
        )
    except requests.exceptions.Timeout as error:
        raise ErreurApi("L'API n'a pas répondu dans le délai prévu.") from error
    except requests.exceptions.RequestException as error:
        raise ErreurApi("Impossible de joindre l'API.") from error

    if response.ok:
        # Si la réponse est vide (ex: 204 No Content) > retourne un dict vide
        if not response.content:
            return {}
        return response.json()
    

    messages = {
        401: "Session absente, invalide ou expirée.",
        403: "Votre rôle ne permet pas cet accès.",
        404: "Ressource introuvable.",
        422: "Paramètres invalides.",
    }

    raise ErreurApi(
        messages.get(response.status_code, f"Erreur API ({response.status_code})"),
        status_code=response.status_code,
    )


def connexion(username: str, password: str) -> dict:
    """Appelle POST /auth/login"""
    return appeler("POST", "/auth/login", json={"username": username, "password": password})


def obtenir(path: str, params: dict | None = None) -> dict | list:
    """Effectue un GET vers FastAPI."""
    return appeler("GET", path, params=params)


def modifier(path: str, json: dict | None = None) -> dict | list:
    """Effectue un PUT vers FastAPI (ex: mise à jour d'incident)"""
    return appeler("PUT", path, json=json)