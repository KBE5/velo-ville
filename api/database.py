"""Connexion à PostgreSQL (SQLAlchemy 2).

Lire DATABASE_URL depuis l'environnement (.env), créer l'engine, la
fabrique de sessions et la dépendance get_db() utilisée par les routeurs.
"""
"""Connexion PostgreSQL et gestion des sessions SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from api.config import DATABASE_URL

# L'engine représente la connexion générale à PostgreSQL.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Fabrique de sessions utilisées par les endpoints.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe de base commune aux modèles SQLAlchemy."""
    pass


def get_db():
    """Injecte une session SQLAlchemy puis la ferme proprement."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
