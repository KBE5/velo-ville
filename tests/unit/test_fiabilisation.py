"""Tests unitaires des règles de fiabilisation.

À compléter : un test par règle, cas nominal et cas de rejet.
"""
from datetime import datetime
import pytest

from api.services.fiabilisation import (
    normaliser_statut_incident,
    valider_et_parser_date,
    valider_station,
    valider_trajet,
    valider_incident,
)

# Tests sur la normalisation 
def test_normaliser_statut_incident():
    assert normaliser_statut_incident("Ouvert") == "ouvert"
    assert normaliser_statut_incident("En cours") == "en_cours"
    assert normaliser_statut_incident("RESOLU") == "resolu"
    assert normaliser_statut_incident("") == ""
    assert normaliser_statut_incident("inconnu") == "inconnu"


# Tests sur les dates 
def test_valider_et_parser_date_valide():
    dt, err = valider_et_parser_date("2026-10-21T10:00:00")
    assert err is None
    assert isinstance(dt, datetime)
    assert dt.year == 2026
    assert dt.month == 10


def test_valider_et_parser_date_invalide():
    dt, err = valider_et_parser_date("date-invalide")
    assert dt is None
    assert err is not None


def test_valider_et_parser_date_vide():
    dt, err = valider_et_parser_date("")
    assert dt is None
    assert "absente" in err


# Tests sur la validation des stations 
def test_valider_station_valide():
    ligne = {"capacite": 10}
    valider_station(ligne)


def test_valider_station_invalide_negative():
    ligne = {"capacite": -5}
    with pytest.raises(ValueError, match="strictement positif"):
        valider_station(ligne)


def test_valider_station_invalide_texte():
    ligne = {"capacite": "abc"}
    with pytest.raises(ValueError, match="non numérique"):
        valider_station(ligne)


# Tests sur la validation des trajets
def test_valider_trajet_valide():
    stations_valides = {"StationA", "StationB"}
    ligne = {
        "duree_secondes": 300,
        "station_depart": "StationA",
        "station_arrivee": "StationB",
        "depart_horodatage": "2026-06-01 10:00:00"
    }
    valider_trajet(ligne, stations_valides)


def test_valider_trajet_depart_inconnu():
    stations_valides = {"StationA"}
    ligne = {
        "duree_secondes": 300,
        "station_depart": "StationInconnue",
        "station_arrivee": "StationA",
        "depart_horodatage": "2026-06-01 10:00:00"
    }
    with pytest.raises(ValueError, match="inexistante ou absente"):
        valider_trajet(ligne, stations_valides)


def test_valider_trajet_duree_invalide():
    stations_valides = {"StationA"}
    ligne = {
        "duree_secondes": 0,
        "station_depart": "StationA",
        "station_arrivee": "StationA"
    }
    with pytest.raises(ValueError):
        valider_trajet(ligne, stations_valides)

def test_valider_trajet_duplique():
    stations_valides = {"StationA", "StationB"}
    trajets_vus = {"T-001"}
    ligne = {
        "trajet_id": "T-001",
        "duree_secondes": 300,
        "depart_horodatage": "2026-10-21T10:00:00",
        "station_depart": "StationA",
        "station_arrivee": "StationB"
    }
    with pytest.raises(ValueError, match="Trajet dupliqué"):
        valider_trajet(ligne, stations_valides, trajets_deja_vus=trajets_vus)

def test_valider_trajet_arrivee_inconnue():
    stations_valides = {"StationA"}
    ligne = {
        "trajet_id": "T-002",
        "duree_secondes": 300,
        "depart_horodatage": "2026-10-21T10:00:00",
        "station_depart": "StationA",
        "station_arrivee": "StationInconnue"
    }
    with pytest.raises(ValueError, match="Station d'arrivée inexistante"):
        valider_trajet(ligne, stations_valides)

def test_valider_trajet_depart_horodatage_invalide():
    stations_valides = {"StationA"}
    ligne = {
        "trajet_id": "T-003",
        "duree_secondes": 300,
        "depart_horodatage": "date-fause",
        "station_depart": "StationA",
        "station_arrivee": "StationA"
    }
    with pytest.raises(ValueError, match="Horodatage de départ invalide"):
        valider_trajet(ligne, stations_valides)


# Tests sur la validation des incidents 
def test_valider_incident_velo_valide():
    stations_valides = {"StationA"}
    ligne = {
        "statut": "ouvert",
        "cible": "velo",
        "station_id": None,
        "velo_id": "V-999",
        "date_signalement": "2026-10-13T08:00:00",
        "date_resolution": None
    }
    statut = valider_incident(ligne, stations_valides)
    assert statut == "ouvert"


def test_valider_incident_statut_interdit():
    stations_valides = {"StationA"}
    ligne = {
        "statut": "bizarre",
        "cible": "velo",
        "station_id": None,
        "velo_id": "V-999",
        "date_signalement": "2026-10-13T08:00:00",
        "date_resolution": None
    }
    with pytest.raises(ValueError, match="Statut non autorisé"):
        valider_incident(ligne, stations_valides)


def test_valider_incident_station_valide():
    stations_valides = {"StationA"}
    ligne = {
        "statut": "ouvert",
        "cible": "station",
        "station_id": "StationA",
        "velo_id": None,
        "date_signalement": "2026-10-13T08:00:00",
        "date_resolution": None
    }
    statut = valider_incident(ligne, stations_valides)
    assert statut == "ouvert"


def test_valider_incident_station_invalide():
    stations_valides = {"StationA"}
    ligne = {
        "statut": "ouvert",
        "cible": "station",
        "station_id": "StationInconnue",
        "velo_id": None,
        "date_signalement": "2026-10-13T08:00:00",
        "date_resolution": None
    }
    with pytest.raises(ValueError, match="Station visée invalide"):
        valider_incident(ligne, stations_valides)


def test_valider_incident_cible_inconnue():
    stations_valides = {"StationA"}
    ligne = {
        "statut": "ouvert",
        "cible": "trottinette",
        "station_id": None,
        "velo_id": "V-999",
        "date_signalement": "2026-10-13T08:00:00",
        "date_resolution": None
    }
    with pytest.raises(ValueError, match="Cible d'incident invalide"):
        valider_incident(ligne, stations_valides)


def test_valider_incident_resolution_anterieure():
    stations_valides = {"StationA"}
    ligne = {
        "statut": "resolu",
        "cible": "velo",
        "station_id": None,
        "velo_id": "V-999",
        "date_signalement": "2026-10-13T10:00:00",
        "date_resolution": "2026-10-13T09:00:00"  # Plus tôt !
    }
    with pytest.raises(ValueError, match="Date de résolution antérieure"):
        valider_incident(ligne, stations_valides)