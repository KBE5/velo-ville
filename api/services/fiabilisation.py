"""Règles de fiabilisation des données (module métier testé).

À compléter : fonctions pures, sans accès à la base, qui normalisent ou rejettent
une valeur ou une ligne : horodatages, identifiants de vélo, statuts
d'incident, durées, références de station, cohérence des dates,
doublons. Chaque fonction retourne la valeur normalisée ou signale le
motif de rejet. Ces fonctions sont appelées par scripts/importer.py et
couvertes par tests/unit/.
"""

from datetime import datetime
from typing import Any, Dict, Set, Tuple, Optional
import pandas as pd


# normaliser statut incident (Casse, Formats, Nettoyage)

def normaliser_statut_incident(statut_colonne: str) -> str:
    """Normalise la casse et la forme des statuts d'incidents.
    
    Exemples : 'Ouvert' -> 'ouvert', 'En cours' -> 'en_cours', 'RESOLU' -> 'resolu'.
    """
    if not statut_colonne or str(statut_colonne).strip().lower() in ("", "nan", "none"):
        return ""
    statut_clean = str(statut_colonne).strip().lower().replace(" ", "_")
    if statut_clean in {"ouvert", "en_cours", "resolu"}:
        return statut_clean
    return str(statut_colonne).strip()


def valider_et_parser_date(date_str: str) -> Tuple[Optional[datetime], Optional[str]]:
    """Tente de parser une chaîne de date/horodatage au format ISO (AAAA-MM-JJ ou AAAA-MM-JJ HH:MM:SS).
    
    Retourne (datetime_obj, None) si valide, ou (None, motif_erreur).
    """
    if not date_str or str(date_str).strip().lower() in ("", "nan", "none"):
        return None, "Date absente ou vide"
    
    date_clean = str(date_str).strip()
    try:
        dt = datetime.fromisoformat(date_clean)
        return dt, None
    except ValueError:
        return None, f"Format d'horodatage invalide: {date_str}"


# Règles de fiabilisation des stations

def valider_station(ligne: Dict[str, Any]) -> None:
    """Valide les règles de gestion d'une station (RG1).
    
    - capacite : entier strictement positif (> 0).
    """
    valeur_capacite = ligne["capacite"]
    try:
        capa = int(valeur_capacite)
    except (ValueError, TypeError):
        raise ValueError(f"Capacité invalide ou non numérique: {valeur_capacite}")

    if capa <= 0:
        raise ValueError("Capacité doit être un entier strictement positif (> 0)")

# Règles de fiabilisation de trajets

def valider_trajet(ligne: Dict[str, Any], stations_valides: Set[str]) -> None:
    """Valide les règles de gestion d'un trajet (RG4, RG2).
    
    - duree_secondes : entier strictement positif (> 0).
    - station_depart : obligatoire et doit exister dans les stations référencées.
    - station_arrivee : facultative, mais si renseignée, doit exister.
    """
    # RG4
    valeur_duree = ligne["duree_secondes"]
    try:
        duree = int(valeur_duree)
        if duree <= 0:
            raise ValueError("Durée de trajet <= 0 seconde")
    except (ValueError, TypeError):
        raise ValueError(f"Durée invalide ou non numérique: {valeur_duree}")

    # RG2
    st_dep = str(ligne["station_depart"]).strip()
    if not st_dep or st_dep.lower() in ("nan", "none") or st_dep not in stations_valides:
        raise ValueError(f"Station de départ inexistante ou absente: {st_dep}")

    # RG2 / RG3 : Valider station arrivee si présente
    st_arr = ligne["station_arrivee"]
    if pd.notna(st_arr) and str(st_arr).strip().lower() not in ("", "nan", "none"):
        st_arr_clean = str(st_arr).strip()
        if st_arr_clean not in stations_valides:
            raise ValueError(f"Station d'arrivée inexistante dans le référentiel: {st_arr_clean}")


def valider_incident(ligne: Dict[str, Any], stations_valides: Set[str]) -> str:
    """Valide et normalise une ligne d'incident (RG6, RG7, RG8).
    
    Retourne le statut normalisé ou lève une ValueError.
    """
    statut_brut = str(ligne["statut"])
    statut = normaliser_statut_incident(statut_brut)

    # RG7 : Statuts autorisés
    if statut not in {"ouvert", "en_cours", "resolu"}:
        raise ValueError(f"Statut non autorisé: '{statut_brut}'")

    # RG6 : Cible soit un vélo, soit une station
    cible = str(ligne["cible"]).strip().lower()
    st_id = ligne["station_id"]
    v_id = ligne["velo_id"]

    if cible == "station":  # cas station
        st_id_clean = str(st_id).strip() if pd.notna(st_id) else ""
        if not st_id_clean or st_id_clean.lower() in ("nan", "none") or st_id_clean not in stations_valides:
            raise ValueError(f"Station visée invalide ou inexistante: '{st_id}'")
            
    elif cible == "velo":  # cas vélo
        v_id_clean = str(v_id).strip() if pd.notna(v_id) else ""
        if not v_id_clean or v_id_clean.lower() in ("nan", "none"):
            raise ValueError("Cible vélo spécifiée mais identifiant vélo absent")
    else:
        raise ValueError(f"Cible d'incident invalide: '{cible}'")

    # RG8 : Cohérence des dates de signalement 
    date_sig_str = ligne["date_signalement"]
    dt_sig, err_sig = valider_et_parser_date(date_sig_str)
    if err_sig:
        raise ValueError(f"Date de signalement invalide: {err_sig}")

    # RG8 : Cohérence des dates de résolution 
    date_res_str = ligne["date_resolution"]
    if statut == "resolu":
        if pd.notna(date_res_str) and str(date_res_str).strip().lower() not in ("", "nan", "none"):
            dt_res, err_res = valider_et_parser_date(date_res_str)
            if err_res:
                raise ValueError(f"Date de résolution invalide: {err_res}")
            if dt_res and dt_sig and dt_res < dt_sig:
                raise ValueError("Date de résolution antérieure à la date de signalement")

    return statut