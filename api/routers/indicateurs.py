"""Routeur indicateurs.

GET /indicateurs/activite-par-jour,
GET /indicateurs/stations-actives et
GET /indicateurs/incidents-par-statut.
"""
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.services.indicateurs import (activite_par_jour, stations_actives, incidents_par_statut,)
from api.dependencies import get_current_user

router = APIRouter(prefix="/indicateurs", tags=["Indicateurs"], dependencies=[Depends(get_current_user)])


@router.get("/activite-par-jour")
def get_activite_par_jour(date_debut: date, date_fin: date,db: Session = Depends(get_db)): #Rajout des dates suite à err interface
    
    return activite_par_jour(db, date_debut=date_debut, date_fin=date_fin)


@router.get("/stations-actives") 
def get_stations_actives(limite: int = 10, db: Session = Depends(get_db)):
    """Récupère le classement des stations les plus actives"""
    return stations_actives(db, limite=limite)


@router.get("/incidents-par-statut")
def get_incidents_par_statut(db: Session = Depends(get_db)):
    """Récupère les statistiques des incidents par statut et le délai moyen de résolution"""
    return incidents_par_statut(db)