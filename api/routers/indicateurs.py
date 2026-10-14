"""Routeur indicateurs.

GET /indicateurs/activite-par-jour,
GET /indicateurs/stations-actives et
GET /indicateurs/incidents-par-statut.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.services.indicateurs import (activite_par_jour, stations_actives, incidents_par_statut,)

router = APIRouter(prefix="/indicateurs", tags=["Indicateurs"])


@router.get("/activite-par-jour")
def get_activite_par_jour(db: Session = Depends(get_db)):
    
    return activite_par_jour(db)


@router.get("/stations-actives") 
def get_stations_actives(limite: int = 10, db: Session = Depends(get_db)):
    """Récupère le classement des stations les plus actives"""
    return stations_actives(db, limite=limite)


@router.get("/incidents-par-statut")
def get_incidents_par_statut(db: Session = Depends(get_db)):
    """Récupère les statistiques des incidents par statut et le délai moyen de résolution"""
    return incidents_par_statut(db)