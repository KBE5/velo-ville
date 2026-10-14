"""Routeur trajets.

GET /trajets (filtres date_debut, date_fin, station ; pagination).
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Trajet
from api.schemas import TrajetResponse, TrajetPageResponse
from api.dependencies import get_current_user

router = APIRouter(prefix="/trajets", tags=["Trajets"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=TrajetPageResponse)
def lister_trajets(
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
    station: Optional[str] = None,
    page: int = Query(1, ge=1),
    taille_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Récupère la liste paginée des trajets avec filtres optionnels (date_debut, date_fin, station)."""
    stmt = select(Trajet)
    
    # Filtre par date de début 
    if date_debut:
        stmt = stmt.where(Trajet.depart_horodatage >= date_debut)
        
    # Filtre par date de fin (trajets jusqu'à cette date)
    if date_fin:
        stmt = stmt.where(Trajet.depart_horodatage <= date_fin)
        
    # Filtre par station (soit le départ, soit l'arrivée)
    if station:
        stmt = stmt.where(
            or_(
                Trajet.station_depart == station,
                Trajet.station_arrivee == station
            )
        )
        
    # Calcul du total global avec les filtres appliqués
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0
    
    # Application de la pagination et du tri
    offset = (page - 1) * taille_page
    stmt = stmt.order_by(Trajet.trajet_id).offset(offset).limit(taille_page)
    
    resultats = db.scalars(stmt).all()
    
    # "resultats" est placé en premier pour s'afficher en haut, et la pagination en bas
    return {
        "resultats": resultats,
        "total": total,
        "page": page,
        "taille_page": taille_page,
    }


@router.get("/{trajet_id}", response_model=TrajetResponse)
def obtenir_trajet(trajet_id: str, db: Session = Depends(get_db)):
    """Récupère un trajet spécifique par son identifiant."""
    stmt = select(Trajet).where(Trajet.trajet_id == trajet_id)
    trajet = db.scalar(stmt)
    
    if not trajet:
        raise HTTPException(status_code=404, detail="Trajet introuvable")
    return trajet