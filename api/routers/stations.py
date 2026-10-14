"""Routeur stations.

GET /stations (filtre commune, pagination) 
et GET /stations/{station_id}.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Station
from api.schemas import StationResponse, StationPageResponse

router = APIRouter(prefix="/stations", tags=["Stations"])


@router.get("", response_model=StationPageResponse)
def lister_stations( commune: str = None, page: int = Query(1, ge=1),
    taille_page: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    
    """Liste paginée des stations avec filtre opt commune"""
    stmt = select(Station)
    
    if commune:
        stmt = stmt.where(Station.commune.ilike(f"%{commune}%"))
        
    count_stmt = select(func.count()).select_from(stmt.subquery()) # Calcul du total global
    total = db.scalar(count_stmt) or 0
    
    # Pagination et tri
    offset = (page - 1) * taille_page
    stmt = stmt.order_by(Station.station_id).offset(offset).limit(taille_page)
    
    resultats = db.scalars(stmt).all()
    
    return {
        "total": total,
        "page": page,
        "taille_page": taille_page,
        "resultats": resultats
    }


@router.get("/{station_id}", response_model=StationResponse)
def obtenir_station(station_id: str, db: Session = Depends(get_db)):
    """Une station spécifique par son id"""
    stmt = select(Station).where(Station.station_id == station_id)
    station = db.scalar(stmt)
    
    if not station:
        raise HTTPException(status_code=404, detail="Station introuvable")
    return station
