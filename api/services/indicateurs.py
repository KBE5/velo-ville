"""Calcul des trois indicateurs (module métier testé).

À compléter : activite_par_jour(session, date_debut, date_fin),
stations_actives(session, limite) et incidents_par_statut(session).
Les routeurs ne font qu'appeler ces fonctions.
"""

from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy import select, extract
from sqlalchemy.orm import Session
from collections import Counter

from api.models import Trajet, Station, Incident


def activite_par_jour(session: Session, date_debut: Optional[date] = None, 
                      date_fin: Optional[date] = None) -> List[Dict[str, Any]]:
    
    """Calcule la répartition du nombre de trajets par jour de départ."""
    stmt = select(Trajet)
    
    if date_debut:
        stmt = stmt.where(Trajet.depart_horodatage >= date_debut)
    if date_fin:
        stmt = stmt.where(Trajet.depart_horodatage <= date_fin)

    trajets = session.scalars(stmt).all()
 
    compteur_jours = Counter()
    for trajet in trajets:
        jour = trajet.depart_horodatage.date()
        compteur_jours[jour] += 1
        
        jours_tries = sorted(compteur_jours.keys()) # Tri par jour croissant
    
    return [
        {"jour": jour, "nb_trajets": compteur_jours[jour]}
        for jour in jours_tries
    ]


def stations_actives(session: Session, limite: int = 10) -> List[Dict[str, Any]]:
    
    """Retourne les stations ayant le plus de mouvements (départs + arrivées)."""
    stations = session.scalars(select(Station)).all()
    trajets = session.scalars(select(Trajet)).all()
    
    stats_stations = {}
    for station in stations:
        stats_stations[station.station_id] = {
            "station_id": station.station_id,
            "nom": station.nom,
            "nb_departs": 0,
            "nb_arrivees": 0
        }
        
    for trajet in trajets:
        if trajet.station_depart in stats_stations:
            stats_stations[trajet.station_depart]["nb_departs"] += 1
        if trajet.station_arrivee and trajet.station_arrivee in stats_stations:
            stats_stations[trajet.station_arrivee]["nb_arrivees"] += 1
            
    # Calculer le total des mouvements > pour le tri
    resultats = []
    for data in stats_stations.values():
        total_mouvements = data["nb_departs"] + data["nb_arrivees"]
        resultats.append({
            "station_id": data["station_id"],
            "nom": data["nom"],
            "nb_departs": data["nb_departs"],
            "nb_arrivees": data["nb_arrivees"],
            "total": total_mouvements
        })
        
    # Tri décroissant sur le total des mouvements
    # Ensuite, croissant sur l'ID de la station
    resultats.sort(key=lambda x: (-x["total"], x["station_id"]))
    
    # > limite
    top_stations = resultats[:limite]
    
    return [
        {
            "station_id": r["station_id"],
            "nom": r["nom"],
            "nb_departs": r["nb_departs"],
            "nb_arrivees": r["nb_arrivees"]
        }
        for r in top_stations
    ]


def incidents_par_statut(session: Session) -> Dict[str, Any]:
    
    """Calcule le nombre d'incidents par statut et le délai moyen de résolution."""
    incidents = session.scalars(select(Incident)).all()
    
    compteur_statuts = Counter()
    delais_secondes = []
    
    for incident in incidents:
        compteur_statuts[incident.statut] += 1
        
        if incident.statut == "resolu" and incident.date_resolution and incident.date_signalement:
            delta = incident.date_resolution - incident.date_signalement
            delais_secondes.append(delta.total_seconds())
            
    donnees_statuts = [
        {"statut": statut, "nb_incidents": nb}
        for statut, nb in compteur_statuts.items()
    ]
    
    delai_moyen_heures: Optional[float] = None
    if delais_secondes:
        moyenne_secondes = sum(delais_secondes) / len(delais_secondes)
        delai_moyen_heures = round(moyenne_secondes / 3600.0, 1)

    return {
        "donnees": donnees_statuts,
        "delai_moyen_resolution_heures": delai_moyen_heures
    }