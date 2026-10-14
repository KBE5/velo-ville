"""Fixtures pytest communes.

Client TestClient de l'API, jetons pour exploitant01 et direction01,
session de base de données de test. Aucun secret en dur : lire .env.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.config import DATABASE_URL_TEST
from api.database import get_db
from api.main import app
from api.securite import create_access_token 

# Engine de test connecté à la base PostgreSQL de test
engine_test = create_engine(
    DATABASE_URL_TEST,
    pool_pre_ping=True
)

SessionTest = sessionmaker(
    bind=engine_test,
    autoflush=False,
    autocommit=False
)


@pytest.fixture()
def db_session():
    """Ouvre une transaction et fait un rollback automatique à la fin du test"""
    connexion = engine_test.connect()
    transaction = connexion.begin()

    session = SessionTest(bind=connexion)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connexion.close()


@pytest.fixture()
def client(db_session):
    """Surcharge la dépendance get_db pour utiliser la session de test isolée"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def entete(token: str) -> dict:
    """Helper pour générer les en-têtes d'authentification Bearer"""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def token_exploitant():
    """Génère un token JWT valide pour un utilisateur avec le rôle exploitant"""
    return create_access_token(username="exploitant01", role="exploitant")


@pytest.fixture
def token_direction():
    """Génère un token JWT valide pour un utilisateur avec le rôle direction"""
    return create_access_token(username="direction01", role="direction")
