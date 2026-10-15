"""Routeur incidents.

GET /incidents (filtre statut, pagination) 
et
PUT /incidents/{incident_id}/statut (rôle exploitant).
"""

from datetime import datetime, timezone
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Incident, Utilisateur as User
from api.schemas import IncidentResponse, IncidentPageResponse, IncidentUpdateStatut
from api.dependencies import get_current_user, require_roles


router = APIRouter(prefix="/incidents", tags=["Incidents"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=IncidentPageResponse)
def lister_incidents(
    statut: Optional[Literal["ouvert", "en_cours", "resolu"]] = None,
    page: int = Query(1, ge=1), taille_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
   ):
    """Récupère la liste paginée des incidents avec filtre optionnel par statut """
    stmt = select(Incident)
    
    if statut:
        stmt = stmt.where(Incident.statut == statut)
        
    # Calcul du total global avec les filtres
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0
    
    # Application de la pagination et du tri
    offset = (page - 1) * taille_page
    stmt = stmt.order_by(Incident.date_signalement.desc()).offset(offset).limit(taille_page)
    
    resultats = db.scalars(stmt).all()
    
    return {
        "total": total,
        "page": page,
        "taille_page": taille_page,
        "resultats": resultats
    }


@router.get("/{incident_id}", response_model=IncidentResponse)
def obtenir_incident(incident_id: str, db: Session = Depends(get_db)):
    """Récupère un incident spécifique par son identifiant."""
    stmt = select(Incident).where(Incident.incident_id == incident_id)
    incident = db.scalar(stmt)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident introuvable")
    return incident


@router.put("/{incident_id}/statut", response_model=IncidentResponse)
def modifier_statut_incident(
    incident_id: str,
    body: IncidentUpdateStatut,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("exploitant"))
):
    """Modifie le statut d'un incident (réservé au rôle exploitant)."""
    stmt = select(Incident).where(Incident.incident_id == incident_id)
    incident = db.scalar(stmt)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident introuvable")
        
    # MàJ du statut
    incident.statut = body.statut
    
    # Si l'incident est résolu >> enregistrer la date de résolution 
    if body.statut == "resolu" and not incident.date_resolution:
        incident.date_resolution = datetime.now(timezone.utc)

    # (ERR interface) > Si l'incident n'est plus résolu >> vider la date pour respecter la contrainte CHECK
    elif body.statut != "resolu":
        incident.date_resolution = None
        
    db.commit()
    db.refresh(incident)
    
    return incident