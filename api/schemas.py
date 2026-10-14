"""Schémas Pydantic (entrées et sorties de l'API).

À compléter : schémas de lecture des trois ressources, enveloppe paginée, corps de
connexion, réponse de connexion, corps de changement de statut, réponses
des trois indicateurs.
"""

from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


# =================Authentification & Token ================================

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Literal["exploitant", "direction"]


# =================Stations ================================================

class StationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    station_id: str = Field(..., max_length=10)
    nom: str = Field(..., max_length=255)
    commune: str = Field(..., max_length=100)
    capacite: int
    latitude: float
    longitude: float
    date_mise_en_service: date


class StationPageResponse(BaseModel):
    resultats: List[StationResponse]
    total: int
    page: int = Field(..., ge=1)
    taille_page: int = Field(..., ge=1, le=100)


# =================Trajets =================================================

class TrajetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trajet_id: str = Field(..., max_length=12)
    velo_id: str = Field(..., max_length=8)
    depart_horodatage: datetime
    station_depart: str = Field(..., max_length=10)
    station_arrivee: Optional[str] = Field(None, max_length=10)
    duree_secondes: int
    type_usager: str = Field(..., max_length=20)
    usager_ref: Optional[str] = Field(None, max_length=20)


class TrajetPageResponse(BaseModel):
    resultats: List[TrajetResponse]
    total: int
    page: int = Field(..., ge=1)
    taille_page: int = Field(..., ge=1, le=100)


# =================Incidents ===============================================

class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: str = Field(..., max_length=12)
    date_signalement: datetime
    cible: str = Field(..., max_length=10)
    velo_id: Optional[str] = Field(None, max_length=8)
    station_id: Optional[str] = Field(None, max_length=10)
    type_incident: str = Field(..., max_length=100)
    statut: Literal["ouvert", "en_cours", "resolu"]
    date_resolution: Optional[datetime] = None
    technicien: Optional[str] = Field(None, max_length=100)


class IncidentUpdateStatut(BaseModel):
    statut: Literal["en_cours", "resolu"]


class IncidentPageResponse(BaseModel):
    resultats: List[IncidentResponse]
    total: int
    page: int = Field(..., ge=1)
    taille_page: int = Field(..., ge=1, le=100)

# =================Indicateurs métiers =====================================

class ActiviteJourItem(BaseModel):
    jour: date
    nb_trajets: int


class IndicateurActiviteResponse(BaseModel):
    donnees: List[ActiviteJourItem]


class StationActiveItem(BaseModel):
    station_id: str
    nom: str
    nb_departs: int
    nb_arrivees: int


class IndicateurStationsActivesResponse(BaseModel):
    donnees: List[StationActiveItem]


class IncidentStatutItem(BaseModel):
    statut: str
    nb_incidents: int


class IndicateurIncidentsResponse(BaseModel):
    donnees: List[IncidentStatutItem]
    delai_moyen_resolution_heures: Optional[float] = None