"""Tests des fonctions de calcul des indicateurs.

Vérifie les agrégats sur un jeu de données connu respectant les contraintes ORM/BDD.
"""

from datetime import datetime, date
import pytest

from api.models import Trajet, Station, Incident
from api.services.indicateurs import (
    activite_par_jour,
    stations_actives,
    incidents_par_statut,
)


def test_activite_par_jour_connu(db_session):
    """Vérifie l'indicateur activite_par_jour sur un jeu de données"""
    
    # Création préalable des stations référencées par les trajets > contrainte FK
    s1 = Station(
        station_id="1",
        nom="Station 1",
        commune="Lille",
        capacite=15,
        latitude=50.63,
        longitude=3.06,
        date_mise_en_service=date(2025, 1, 1)
    )
    s2 = Station(
        station_id="2",
        nom="Station 2",
        commune="Lille",
        capacite=20,
        latitude=50.64,
        longitude=3.07,
        date_mise_en_service=date(2025, 1, 1)
    )
    s3 = Station(
        station_id="3",
        nom="Station 3",
        commune="Roubaix",
        capacite=10,
        latitude=50.69,
        longitude=3.17,
        date_mise_en_service=date(2025, 1, 1)
    )
    db_session.add_all([s1, s2, s3])

    t1 = Trajet(
        trajet_id="101",
        velo_id="V1",
        station_depart="1",
        station_arrivee="2",
        depart_horodatage=datetime(2026, 8, 24, 8, 0, 0),
        duree_secondes=1800,  
        type_usager="abonne",
    )
    t2 = Trajet(
        trajet_id="102",
        velo_id="V1",
        station_depart="2",
        station_arrivee="1",
        depart_horodatage=datetime(2026, 8, 24, 15, 0, 0),
        duree_secondes=1800,  
        type_usager="abonne",
    )
    t3 = Trajet(
        trajet_id="103",
        velo_id="V2",
        station_depart="1",
        station_arrivee="3",
        depart_horodatage=datetime(2026, 8, 25, 9, 0, 0),
        duree_secondes=1200,  
        type_usager="occasionnel",
    )

    db_session.add_all([t1, t2, t3])
    db_session.commit()

    resultat = activite_par_jour(db_session)

    assert len(resultat) == 2
    assert resultat[0]["jour"] == date(2026, 8, 24)
    assert resultat[0]["nb_trajets"] == 2
    assert resultat[1]["jour"] == date(2026, 8, 25)
    assert resultat[1]["nb_trajets"] == 1


@pytest.mark.parametrize(
    
    "limite_demandee, nb_attendu_resultats, premier_station_id",
    [
        (1, 1, "1"),  # Teste avec limite de 1 station (station_id est de type string)
        (2, 2, "1"),  # Teste avec limite de 2 stations
    ],
)
def test_stations_actives_limites(db_session, limite_demandee, nb_attendu_resultats, premier_station_id):
    
    """Vérifie l'impact du paramètre 'limite' sur les stations actives."""
    s1 = Station(
        station_id="1", 
        nom="Station Lille", 
        commune="Lille",
        capacite=10,
        latitude=50.63,
        longitude=3.06,
        date_mise_en_service=date(2025, 1, 1)
    )
    s2 = Station(
        station_id="2", 
        nom="Station Roubaix", 
        commune="Roubaix",
        capacite=10,
        latitude=50.69,
        longitude=3.17,
        date_mise_en_service=date(2025, 1, 1)
    )
    db_session.add_all([s1, s2])

    t1 = Trajet(
        trajet_id="201",
        velo_id="V1",
        station_depart="1",
        station_arrivee="2",
        depart_horodatage=datetime(2026, 8, 24, 8, 0, 0),
        duree_secondes=1800,  
        type_usager="abonne",
    )
    db_session.add(t1)
    db_session.commit()

    resultat = stations_actives(db_session, limite=limite_demandee)

    assert len(resultat) == nb_attendu_resultats
    assert resultat[0]["station_id"] == premier_station_id


@pytest.mark.parametrize(
    "statut_incident, delai_attendu",
    [
        ("resolu", 4.0),  # Un incident résolu avec 4h d'écart
    ],
)
def test_incidents_par_statut_connu(db_session, statut_incident, delai_attendu):
    
    """Vérifie l'indicateur incidents_par_statut avec des jeux paramétrés."""
    i1 = Incident(
        incident_id="1",  # str
        statut=statut_incident,
        cible="velo",
        type_incident="technique",  
        date_signalement=datetime(2026, 8, 24, 10, 0, 0),
        date_resolution=datetime(2026, 8, 24, 14, 0, 0),
    )
    
    i2 = Incident(
        incident_id="2",  # str
        statut="ouvert",
        cible="station",
        type_incident="vandalisme", 
        date_signalement=datetime(2026, 8, 24, 12, 0, 0),
        date_resolution=None,
    )
    db_session.add_all([i1, i2])
    db_session.commit()

    resultat = incidents_par_statut(db_session)

    donnees = {d["statut"]: d["nb_incidents"] for d in resultat["donnees"]}
    assert donnees[statut_incident] == 1
    assert donnees["ouvert"] == 1
    assert resultat["delai_moyen_resolution_heures"] == delai_attendu