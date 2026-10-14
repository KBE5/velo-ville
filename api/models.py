"""Modèles ORM SQLAlchemy : Station, Trajet, Incident, Utilisateur.

Déclarer les quatre tables conformément à sql/schema.sql.
"""

from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Numeric, Date, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class Station(Base):
    
    __tablename__ = "station"

    station_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    commune: Mapped[str] = mapped_column(String(100), nullable=False)
    capacite: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False)
    date_mise_en_service: Mapped[date] = mapped_column(Date, nullable=False)

    # Relations optionnelles pour faciliter les requêtes 
    trajets_depart: Mapped[List["Trajet"]] = relationship(
        "Trajet", foreign_keys="[Trajet.station_depart]", back_populates="station_depart_ref"
    )
    trajets_arrivee: Mapped[List["Trajet"]] = relationship(
        "Trajet", foreign_keys="[Trajet.station_arrivee]", back_populates="station_arrivee_ref"
    )
    incidents: Mapped[List["Incident"]] = relationship("Incident", back_populates="station_ref")


class Trajet(Base):
    
    __tablename__ = "trajet"

    trajet_id: Mapped[str] = mapped_column(String(15), primary_key=True)
    velo_id: Mapped[str] = mapped_column(String(10), nullable=False)
    depart_horodatage: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    station_depart: Mapped[str] = mapped_column(String(10), ForeignKey("station.station_id"), nullable=False)
    station_arrivee: Mapped[Optional[str]] = mapped_column(String(10), ForeignKey("station.station_id"), nullable=True)
    duree_secondes: Mapped[int] = mapped_column(Integer, nullable=False)
    type_usager: Mapped[str] = mapped_column(String(20), nullable=False)
    usager_ref: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relations
    station_depart_ref: Mapped["Station"] = relationship("Station", foreign_keys=[station_depart], back_populates="trajets_depart")
    station_arrivee_ref: Mapped[Optional["Station"]] = relationship("Station", foreign_keys=[station_arrivee], back_populates="trajets_arrivee")


class Incident(Base):
    
    __tablename__ = "incident"

    incident_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    date_signalement: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    cible: Mapped[str] = mapped_column(String(10), nullable=False)
    velo_id: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    station_id: Mapped[Optional[str]] = mapped_column(String(10), ForeignKey("station.station_id"), nullable=True)
    type_incident: Mapped[str] = mapped_column(String(100), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="ouvert")
    date_resolution: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    technicien: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relations
    station_ref: Mapped[Optional["Station"]] = relationship("Station", back_populates="incidents")


class Utilisateur(Base):
    
    __tablename__ = "utilisateur"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
