"""Fixtures pytest communes.

À compléter : client TestClient de l'API, jetons pour exploitant01 et direction01,
session de base de données de test. Aucun secret en dur : lire .env.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from api.database import Base, get_db
from api.main import app
#from api.security import create_access_token

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Exemple : utilisation d'une base SQLite en mémoire pour les tests
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture(scope="function")
def db_session():
    """Session de base de données de test isolée pour chaque test."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {})
    Base.metadata.create_all(engine)
    SessionTest = sessionmaker(bind=engine)
    session = SessionTest()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Client TestClient de l'API avec injection de la session de test."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def token_exploitant():
    """Génère un jeton d'accès valide pour l'utilisateur exploitant01."""
    # Aucun secret en dur : on s'appuie sur la logique de sécurité qui lit la clé secrète via l'env
    return create_access_token(username="exploitant01", role="exploitant")


@pytest.fixture
def token_direction():
    """Génère un jeton d'accès valide pour l'utilisateur direction01."""
    return create_access_token(username="direction01", role="direction")